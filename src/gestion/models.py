import logging
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


# ==================== CUSTOM MANAGERS ====================
class VentaActivaManager(models.Manager):
    """Manager que filtra automáticamente ventas eliminadas"""
    def get_queryset(self):
        return super().get_queryset().filter(eliminada=False)


class VentaManager(models.Manager):
    """Manager que incluye todas las ventas (incluso eliminadas)"""
    pass


# ==================== MODELOS ====================
class Venta(models.Model):
    fecha = models.DateTimeField(default=timezone.now)
    cliente = models.CharField(max_length=200, blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # 🗄️ SOFT DELETE SYSTEM - ARQUITECTURA DB PROFESIONAL
    eliminada = models.BooleanField(
        default=False,
        verbose_name="Venta Eliminada",
        help_text="Marca la venta como eliminada sin borrar el registro"
    )
    fecha_eliminacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Eliminación"
    )
    razon_eliminacion = models.TextField(
        blank=True,
        verbose_name="Razón de Eliminación",
        help_text="Motivo por el cual se eliminó la venta"
    )
    usuario_eliminacion = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ventas_eliminadas',
        verbose_name="Usuario que Eliminó"
    )

    # 🚀 CUSTOM MANAGERS
    # Por defecto, solo ventas activas (NO eliminadas)
    objects = VentaActivaManager()  # Manager por defecto - filtra eliminadas
    todos = VentaManager()  # Manager explícito para incluir eliminadas
    # Uso: Venta.objects.all() → solo activas
    #      Venta.todos.all() → todas (incluso eliminadas)

    def __str__(self):
        status = " [ELIMINADA]" if self.eliminada else ""
        return f"Venta #{self.id} - {self.fecha.strftime('%Y-%m-%d %H:%M')}{status}"

    class Meta:
        verbose_name_plural = "Ventas"
        ordering = ['-fecha']
        # 🚀 ÍNDICES OPTIMIZADOS PARA PERFORMANCE
        indexes = [
            models.Index(fields=['fecha', 'eliminada'], name='venta_fecha_eliminada_idx'),
            models.Index(fields=['eliminada'], name='venta_eliminada_idx'),
            models.Index(fields=['usuario'], name='venta_usuario_idx'),
        ]

    def calcular_total(self):
        total = sum([detalle.subtotal for detalle in self.detalles.all()])
        self.total = total
        self.save()

    def eliminar_venta(self, usuario, razon=""):
        """🔒 MÉTODO SEGURO PARA ELIMINAR VENTAS"""
        self.eliminada = True
        self.fecha_eliminacion = timezone.now()
        self.razon_eliminacion = razon
        self.usuario_eliminacion = usuario
        self.save()

    def restaurar_venta(self, usuario):
        """♻️ MÉTODO PARA RESTAURAR VENTAS"""
        self.eliminada = False
        self.fecha_eliminacion = None
        self.razon_eliminacion = ""
        self.usuario_eliminacion = None
        self.save()


# Modelo para los detalles de cada venta (productos vendidos, cantidad, precio unitario, subtotal)
class VentaDetalle(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} (${self.subtotal})"


# ==================== SISTEMA DE ALERTAS INTELIGENTES ====================
class Alerta(models.Model):
    """
    Sistema de alertas inteligentes para gestión proactiva del negocio.
    Generadas automáticamente por AlertasService.
    """

    # Tipos de alerta (7 categorías)
    TIPOS_ALERTA = [
        ('stock_agotado', 'Stock Agotado'),
        ('stock_critico', 'Stock Crítico'),
        ('vencimiento', 'Próximo a Vencer'),
        ('margen_negativo', 'Margen Negativo'),
        ('margen_bajo', 'Margen Bajo'),
        ('stock_muerto', 'Stock Muerto'),
        ('oportunidad_venta', 'Oportunidad de Venta'),
    ]

    # Niveles de severidad
    NIVELES = [
        ('danger', 'Peligro'),
        ('warning', 'Advertencia'),
        ('success', 'Oportunidad'),
        ('info', 'Información'),
    ]

    # Campos principales
    tipo = models.CharField(
        max_length=30,
        choices=TIPOS_ALERTA,
        verbose_name="Tipo de Alerta"
    )
    nivel = models.CharField(
        max_length=10,
        choices=NIVELES,
        default='info',
        verbose_name="Nivel de Severidad"
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título"
    )
    mensaje = models.TextField(
        verbose_name="Mensaje Detallado"
    )

    # Relaciones
    producto = models.ForeignKey(
        'Producto',
        on_delete=models.CASCADE,
        related_name='alertas',
        verbose_name="Producto Relacionado"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='alertas',
        verbose_name="Usuario Destinatario"
    )

    # Datos de impacto
    valor_impacto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor de Impacto ($)",
        help_text="Pérdida potencial o ganancia estimada en pesos"
    )
    accion_sugerida = models.TextField(
        blank=True,
        verbose_name="Acción Sugerida",
        help_text="Recomendación específica para resolver la alerta"
    )

    # Timestamps
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_expiracion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Expiración",
        help_text="Fecha límite de relevancia de la alerta"
    )

    # Estados
    leida = models.BooleanField(
        default=False,
        verbose_name="Leída",
        help_text="Indica si el usuario ha visto la alerta"
    )
    fecha_lectura = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Lectura"
    )
    archivada = models.BooleanField(
        default=False,
        verbose_name="Archivada",
        help_text="Indica si la alerta fue archivada manualmente"
    )
    fecha_archivo = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Archivo"
    )

    class Meta:
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas"
        ordering = ['-fecha_creacion']

        # 🚀 ÍNDICES OPTIMIZADOS PARA CONSULTAS RÁPIDAS
        indexes = [
            models.Index(
                fields=['usuario', 'leida', 'archivada'],
                name='alerta_usuario_estado_idx'
            ),
            models.Index(
                fields=['tipo', 'nivel'],
                name='alerta_tipo_nivel_idx'
            ),
            models.Index(
                fields=['producto', 'tipo'],
                name='alerta_producto_tipo_idx'
            ),
            models.Index(
                fields=['fecha_creacion'],
                name='alerta_fecha_idx'
            ),
        ]

        # Permisos personalizados
        permissions = [
            ('can_view_all_alertas', 'Puede ver todas las alertas'),
            ('can_manage_alertas', 'Puede gestionar alertas'),
        ]

    def __str__(self):
        estado = "📖" if self.leida else "🔔"
        return f"{estado} {self.get_tipo_display()} - {self.producto.nombre}"

    def marcar_como_leida(self):
        """Marca la alerta como leída con timestamp."""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save(update_fields=['leida', 'fecha_lectura'])

    def archivar(self):
        """Archiva la alerta con timestamp."""
        if not self.archivada:
            self.archivada = True
            self.fecha_archivo = timezone.now()
            self.save(update_fields=['archivada', 'fecha_archivo'])

    def esta_vigente(self):
        """Verifica si la alerta sigue siendo relevante."""
        if self.archivada:
            return False
        if self.fecha_expiracion:
            return timezone.now() < self.fecha_expiracion
        return True

    def get_icono(self):
        """Retorna el icono Bootstrap Icons apropiado según el tipo."""
        iconos = {
            'stock_agotado': 'bi-x-circle-fill',
            'stock_critico': 'bi-exclamation-triangle-fill',
            'vencimiento': 'bi-calendar-x',
            'margen_negativo': 'bi-graph-down-arrow',
            'margen_bajo': 'bi-graph-down',
            'stock_muerto': 'bi-box-seam',
            'oportunidad_venta': 'bi-graph-up-arrow',
        }
        return iconos.get(self.tipo, 'bi-bell')

    def get_color_badge(self):
        """Retorna la clase CSS del badge según el nivel."""
        colores = {
            'danger': 'bg-danger',
            'warning': 'bg-warning text-dark',
            'success': 'bg-success',
            'info': 'bg-info text-dark',
        }
        return colores.get(self.nivel, 'bg-secondary')

    def get_dias_desde_creacion(self):
        """Retorna los días transcurridos desde la creación."""
        delta = timezone.now() - self.fecha_creacion
        return delta.days

    def get_dias_hasta_expiracion(self):
        """Retorna los días restantes hasta la expiración (si aplica)."""
        if self.fecha_expiracion:
            delta = self.fecha_expiracion - timezone.now()
            return max(0, delta.days)
        return None


class Producto(models.Model):

    # Categorías específicas para dietética
    CATEGORIAS_DIETETICA = [
        ('suplementos', 'Suplementos Nutricionales'),
        ('cereales', 'Cereales y Granos'),
        ('frutos_secos', 'Frutos Secos y Semillas'),
        ('tes_infusiones', 'Tés e Infusiones'),
        ('harinas_especiales', 'Harinas Especiales'),
        ('endulzantes', 'Endulzantes Naturales'),
        ('aceites_vinagres', 'Aceites y Vinagres'),
        ('conservas', 'Conservas y Preservados'),
        ('productos_veganos', 'Productos Veganos'),
        ('sin_tacc', 'Sin TACC'),
        ('organicos', 'Productos Orgánicos'),
        ('especias', 'Especias y Condimentos'),
        ('bebidas', 'Bebidas Naturales'),
        ('otros', 'Otros'),
    ]

    # Atributos especiales para dietética
    ATRIBUTOS_DIETETICOS = [
        ('organico', 'Orgánico'),
        ('vegano', 'Vegano'),
        ('sin_tacc', 'Sin TACC'),
        ('sin_azucar', 'Sin Azúcar'),
        ('integral', 'Integral'),
        ('natural', 'Natural'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.FloatField(default=0, validators=[MinValueValidator(0)])
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    categoria = models.CharField(
        max_length=50,
        default='otros',
        help_text="Categoría del producto. Puede usar una existente o crear una nueva."
    )
    atributos_dieteticos = models.CharField(
        max_length=200,
        blank=True,
        help_text="Ej: orgánico,vegano,sin_tacc (separados por comas)"
    )
    marca = models.CharField(max_length=100, blank=True, help_text="Marca del producto")
    origen = models.CharField(max_length=100, blank=True, help_text="Origen del producto")
    stock_minimo = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    materia_prima_asociada = models.ForeignKey('MateriaPrima', null=True, blank=True, on_delete=models.SET_NULL, related_name='productos_asociados')
    tiene_receta = models.BooleanField(default=False, verbose_name='¿Usa receta?', help_text='Marcar si el producto se produce a partir de una receta')
    receta = models.ForeignKey('Receta', null=True, blank=True, on_delete=models.SET_NULL, related_name='productos_con_receta', verbose_name='Receta principal', help_text='Selecciona la receta principal si corresponde')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def get_estado_stock(self):
        """
        Devuelve el estado del stock basado en el stock actual y mínimo.
        Retorna: 'agotado', 'critico', 'bajo', 'normal'
        """
        if self.stock == 0:
            return 'agotado'
        elif self.stock <= self.stock_minimo:
            return 'critico'
        elif self.stock <= self.stock_minimo * 1.5:  # 50% más que el mínimo
            return 'bajo'
        else:
            return 'normal'

    def get_estado_stock_display(self):
        """
        Devuelve la descripción legible del estado del stock.
        """
        estado = self.get_estado_stock()
        estados = {
            'agotado': 'Agotado',
            'critico': 'Stock Crítico',
            'bajo': 'Stock Bajo',
            'normal': 'Stock Normal'
        }
        return estados.get(estado, 'Desconocido')

    def get_estado_stock_badge_class(self):
        """
        Devuelve la clase CSS para el badge del estado del stock.
        """
        estado = self.get_estado_stock()
        clases = {
            'agotado': 'bg-danger',
            'critico': 'bg-warning text-dark',
            'bajo': 'bg-info text-dark',
            'normal': 'bg-success'
        }
        return clases.get(estado, 'bg-secondary')

    def get_estado_stock_icon(self):
        """
        Devuelve el icono para el estado del stock.
        """
        estado = self.get_estado_stock()
        iconos = {
            'agotado': 'bi-x-circle',
            'critico': 'bi-exclamation-triangle',
            'bajo': 'bi-info-circle',
            'normal': 'bi-check-circle'
        }
        return iconos.get(estado, 'bi-question-circle')

    # ==================== MÉTODOS SIMPLIFICADOS PARA CÁLCULO REAL ====================

    def calcular_costo_real(self):
        """
        Calcula el costo REAL del producto según su configuración.
        - CON receta: Suma el costo de todos los ingredientes
        - SIN receta (fraccionado): Costo proporcional de la materia prima
        """
        from decimal import Decimal

        if self.tiene_receta and self.receta:
            # CON RECETA: sumar costo de todos los ingredientes
            try:
                return self.receta.costo_total()
            except Exception as e:
                logger.warning("Error calculando costo de receta para producto '%s' (id=%s): %s", self, self.pk, e)
                return Decimal('0.00')

        elif self.materia_prima_asociada and self.cantidad_fraccion:
            # SIN RECETA (Fraccionado): costo proporcional
            # cantidad_fraccion ahora está en la MISMA unidad que la materia prima
            try:
                cantidad = Decimal(str(self.cantidad_fraccion))
                precio_materia = Decimal(str(self.materia_prima_asociada.costo_unitario or 0))

                # 🔧 DEBUG: Logging para diagnóstico
                costo_calculado = (precio_materia * cantidad).quantize(Decimal('0.01'))

                # 🛡️ VALIDACIÓN: Si el costo es sospechosamente bajo (< $1), investigar
                if costo_calculado < Decimal('1.00') and precio_materia > Decimal('100'):
                    # Posible error: cantidad en gramos cuando debería estar en kg
                    # Logging de warning (puedes activar Django logging)
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"⚠️ Costo sospechoso para {self.nombre}: "
                        f"cantidad={cantidad} × precio_materia={precio_materia} = {costo_calculado}. "
                        f"¿cantidad_fraccion en unidad incorrecta?"
                    )

                return costo_calculado
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error calculando costo para {self.nombre}: {str(e)}")
                return Decimal('0.00')

        return Decimal('0.00')

    def debug_costo(self):
        """
        🔍 Método de depuración para diagnosticar problemas de costos.
        Retorna dict con toda la información del cálculo.
        """
        from decimal import Decimal

        debug_info = {
            'producto': self.nombre,
            'tiene_receta': self.tiene_receta,
            'tipo_producto': self.tipo_producto,
        }

        if self.tiene_receta and self.receta:
            debug_info.update({
                'metodo_calculo': 'RECETA',
                'receta': self.receta.nombre,
                'costo_receta': float(self.receta.costo_total()),
            })
        elif self.materia_prima_asociada and self.cantidad_fraccion:
            cantidad = Decimal(str(self.cantidad_fraccion))
            precio_materia = Decimal(str(self.materia_prima_asociada.costo_unitario or 0))
            costo = (precio_materia * cantidad).quantize(Decimal('0.01'))

            debug_info.update({
                'metodo_calculo': 'FRACCIONADO',
                'materia_prima': self.materia_prima_asociada.nombre,
                'unidad_materia': self.materia_prima_asociada.get_unidad_medida_display(),
                'cantidad_fraccion': float(cantidad),
                'precio_materia_unitario': float(precio_materia),
                'costo_calculado': float(costo),
                'formula': f"{float(cantidad)} × ${float(precio_materia)} = ${float(costo)}"
            })
        else:
            debug_info.update({
                'metodo_calculo': 'SIN CONFIGURACIÓN',
                'costo': 0.00
            })

        debug_info['costo_final'] = float(self.calcular_costo_real())
        debug_info['precio_venta'] = float(self.precio)
        debug_info['margen_calculado'] = self.calcular_margen_real()

        return debug_info

    def calcular_margen_real(self):
        """
        Calcula el margen de ganancia REAL en %.
        Fórmula CORRECTA: ((precio_venta - costo) / precio_venta) × 100
        
        Nota: Esto es MARGEN, no markup.
        - Margen = (Precio - Costo) / Precio × 100
        - Markup = (Precio - Costo) / Costo × 100
        
        Retorna valor negativo si hay pérdida.
        """
        from decimal import Decimal

        costo = self.calcular_costo_real()
        precio_venta = Decimal(str(self.precio))

        if precio_venta > 0:
            # Fórmula correcta del MARGEN
            margen = ((precio_venta - costo) / precio_venta) * Decimal('100')
            return float(margen.quantize(Decimal('0.01')))

        return 0.0

    def tiene_margen_negativo(self):
        """Retorna True si el margen es negativo (vendés a pérdida)."""
        return self.calcular_margen_real() < 0

    def validar_stock_inventario(self, cantidad_producir):
        """
        Valida si hay suficiente stock en inventario para producir X cantidad.
        Retorna (hay_stock: bool, faltantes: list)
        """
        from decimal import Decimal

        # Convertir cantidad a Decimal para evitar errores de tipo
        cantidad_producir = Decimal(str(cantidad_producir))

        faltantes = []

        if self.tiene_receta and self.receta:
            # CON RECETA: verificar cada ingrediente
            for ingrediente in self.receta.recetamateriaprima_set.all():
                materia = ingrediente.materia_prima
                necesaria = ingrediente.cantidad * cantidad_producir
                disponible = materia.stock_actual

                if disponible < necesaria:
                    faltantes.append({
                        'materia': materia.nombre,
                        'necesaria': float(necesaria),
                        'disponible': float(disponible),
                        'faltante': float(necesaria - disponible),
                        'unidad': materia.get_unidad_medida_display()
                    })

        elif self.materia_prima_asociada and self.cantidad_fraccion:
            # SIN RECETA: verificar materia prima única
            # cantidad_fraccion ahora está en la MISMA unidad que la materia prima
            materia = self.materia_prima_asociada
            cantidad_necesaria = self.cantidad_fraccion * cantidad_producir
            disponible = materia.stock_actual

            if disponible < cantidad_necesaria:
                faltantes.append({
                    'materia': materia.nombre,
                    'necesaria': float(cantidad_necesaria),
                    'disponible': float(disponible),
                    'faltante': float(cantidad_necesaria - disponible),
                    'unidad': materia.get_unidad_medida_display()
                })

        return (len(faltantes) == 0, faltantes)

    def get_categoria_display(self):
        """
        Devuelve el nombre legible de la categoría.
        """
        # Buscar en las categorías predefinidas
        for codigo, nombre in self.CATEGORIAS_DIETETICA:
            if self.categoria == codigo:
                return nombre

        # Si no está en las predefinidas, formatear el nombre
        if self.categoria:
            return self.categoria.replace('_', ' ').title()

        return 'Sin categoría'

    def verificar_stock_materias_primas(self, cantidad):
        """
        Verifica si hay suficiente stock de materias primas para producir 'cantidad' unidades de este producto.
        Devuelve (True, []) si hay suficiente stock, o (False, lista_faltantes) si falta alguna materia prima.
        """
        from decimal import Decimal

        # Convertir cantidad a Decimal para evitar errores de tipo
        cantidad = Decimal(str(cantidad))

        faltantes = []

        # Para productos con receta
        if self.tipo_producto == 'receta':
            if self.receta:
                # Usar la receta asignada al producto
                for ingrediente in self.receta.recetamateriaprima_set.all():
                    materia = ingrediente.materia_prima
                    necesaria = ingrediente.cantidad * cantidad
                    disponible = materia.stock_actual
                    if disponible < necesaria:
                        faltantes.append({
                            'materia_prima': materia.nombre,
                            'necesaria': float(necesaria),
                            'unidad': materia.get_unidad_medida_display(),
                            'disponible': float(disponible)
                        })
                if faltantes:
                    return False, faltantes
                return True, []
            else:
                # Si no hay receta asignada, no se puede producir
                return False, [{'error': 'No hay receta asignada al producto'}]

        # Para productos de fraccionamiento o reventa con materia prima asociada
        elif self.tipo_producto in ['fraccionamiento', 'reventa']:
            if self.materia_prima_asociada:
                # cantidad_fraccion está en la MISMA unidad que la MP
                # Ejemplo: MP en kg, cantidad_fraccion = 0.250 (kg por unidad de producto)
                # cantidad = unidades de producto a fabricar
                necesaria = cantidad * (self.cantidad_fraccion or Decimal('1'))
                disponible = self.materia_prima_asociada.stock_actual
                if disponible < necesaria:
                    faltantes.append({
                        'materia_prima': self.materia_prima_asociada.nombre,
                        'necesaria': float(necesaria),
                        'unidad': self.materia_prima_asociada.get_unidad_medida_display(),
                        'disponible': float(disponible)
                    })
                    return False, faltantes
                return True, []
            else:
                # Productos de reventa SIN materia prima asociada (compras ya listas)
                # No necesitan verificación de materias primas
                return True, []

        # Si llega hasta aquí, algo está mal configurado
        return False, [{'error': 'Tipo de producto no reconocido o mal configurado'}]

    def verificar_stock_ingredientes(self, cantidad):
        """
        🔍 VALIDACIÓN PREVIA: Verifica que hay stock suficiente de TODOS los ingredientes.
        
        IMPORTANTE: Solo VALIDA, NO descuenta nada. Usado ANTES de abrir transaction.
        
        Args:
            cantidad: Cantidad de producto a vender/producir
            
        Raises:
            ValueError: Si algún ingrediente no tiene stock suficiente
            
        Ejemplo:
            try:
                producto.verificar_stock_ingredientes(5)
            except ValueError as e:
                # Handle "Stock insuficiente de 'Almendra': se necesitan 2.5kg, hay 1kg"
                pass
        """
        from decimal import Decimal

        # Para productos con receta
        if self.tipo_producto == 'receta' and self.receta:
            cantidad = Decimal(str(cantidad))

            for ingrediente in self.receta.recetamateriaprima_set.all():
                materia = ingrediente.materia_prima
                necesaria = ingrediente.cantidad * cantidad

                # ✅ Validación: Verificar stock suficiente
                if materia.stock_actual < necesaria:
                    raise ValueError(
                        f"❌ Stock insuficiente de '{materia.nombre}': "
                        f"se necesitan {necesaria}{materia.unidad_medida}, "
                        f"hay {materia.stock_actual}{materia.unidad_medida}"
                    )

        # Para productos de fraccionamiento o reventa
        elif self.tipo_producto in ['fraccionamiento', 'reventa']:
            if self.materia_prima_asociada:
                cantidad = Decimal(str(cantidad))
                materia = self.materia_prima_asociada
                necesaria = cantidad * (self.cantidad_fraccion or Decimal('1'))

                # ✅ Validación: Verificar stock suficiente
                if materia.stock_actual < necesaria:
                    raise ValueError(
                        f"❌ Stock insuficiente de '{materia.nombre}': "
                        f"se necesitan {necesaria}{materia.unidad_medida}, "
                        f"hay {materia.stock_actual}{materia.unidad_medida}"
                    )

    def descontar_materias_primas(self, cantidad, usuario):
        """
        Descuenta del stock de materias primas lo necesario para producir 'cantidad' unidades de este producto.
        
        ⚠️ IMPORTANTE: Debe ser llamado DENTRO de transaction.atomic() para rollback automático si hay error.
        
        ALGORITMO DE DOS FASES:
        1️⃣ VALIDACIÓN: Verifica stock de TODOS los ingredientes (sin modificar BD)
        2️⃣ DESCUENTO: Solo descuenta si TODOS pasaron validación
        
        Registra movimientos de inventario de cada ingrediente descargado.
        
        Raises:
            ValueError: Si algún ingrediente tiene stock insuficiente
        """
        from decimal import Decimal

        from .models import MovimientoMateriaPrima

        # Convertir cantidad a Decimal para evitar errores de tipo
        cantidad = Decimal(str(cantidad))

        # Para productos con receta
        if self.tipo_producto == 'receta':
            if self.receta:
                # 🔍 FASE 1: VALIDACIÓN - Verificar stock de TODOS los ingredientes ANTES de descontar
                # Si alguno falla, lanzar excepción SIN modificar BD
                ingredientes_a_procesar = []

                for ingrediente in self.receta.recetamateriaprima_set.all():
                    materia = ingrediente.materia_prima
                    necesaria = ingrediente.cantidad * cantidad

                    # ✅ VALIDACIÓN: Verificar stock suficiente
                    if materia.stock_actual < necesaria:
                        raise ValueError(
                            f"❌ Stock insuficiente de '{materia.nombre}': "
                            f"se necesitan {necesaria}{materia.unidad_medida}, "
                            f"hay {materia.stock_actual}{materia.unidad_medida}"
                        )

                    # Si pasa validación, guardar para procesar después
                    ingredientes_a_procesar.append({
                        'ingrediente': ingrediente,
                        'materia': materia,
                        'necesaria': necesaria,
                        'stock_anterior': materia.stock_actual
                    })

                # 🔽 FASE 2: DESCUENTO - Solo si TODOS los ingredientes pasaron validación
                for item in ingredientes_a_procesar:
                    materia = item['materia']
                    necesaria = item['necesaria']
                    stock_anterior = item['stock_anterior']

                    materia.stock_actual -= necesaria
                    materia.save()

                    MovimientoMateriaPrima.objects.create(
                        materia_prima=materia,
                        tipo_movimiento='produccion',
                        cantidad=necesaria,
                        cantidad_anterior=stock_anterior,
                        cantidad_nueva=materia.stock_actual,
                        motivo=f'Producción de {cantidad} x {self.nombre}',
                        usuario=usuario
                    )

        # Para productos de fraccionamiento o reventa con materia prima asociada
        elif self.tipo_producto in ['fraccionamiento', 'reventa']:
            if self.materia_prima_asociada:
                materia = self.materia_prima_asociada
                necesaria = cantidad * (self.cantidad_fraccion or Decimal('1'))

                # ✅ VALIDACIÓN: Verificar stock suficiente
                if materia.stock_actual < necesaria:
                    raise ValueError(
                        f"❌ Stock insuficiente de '{materia.nombre}': "
                        f"se necesitan {necesaria}{materia.unidad_medida}, "
                        f"hay {materia.stock_actual}{materia.unidad_medida}"
                    )

                # ✅ DESCUENTO: Si pasó validación
                stock_anterior = materia.stock_actual
                materia.stock_actual -= necesaria
                materia.save()

                MovimientoMateriaPrima.objects.create(
                    materia_prima=materia,
                    tipo_movimiento='fraccionamiento',
                    cantidad=necesaria,
                    cantidad_anterior=stock_anterior,
                    cantidad_nueva=materia.stock_actual,
                    motivo=f'Producción/Fraccionamiento de {cantidad} x {self.nombre}',
                    usuario=usuario
                )

        # Para productos de reventa SIN materia prima asociada, no se necesita descontar nada

    @property
    def necesita_restock(self):
        return self.stock <= self.stock_minimo

    def get_atributos_lista(self):
        """Devuelve los atributos dietéticos como lista."""
        if self.atributos_dieteticos:
            return [attr.strip() for attr in self.atributos_dieteticos.split(',') if attr.strip()]
        return []

    def get_badges_atributos(self):
        """Devuelve badges HTML para los atributos dietéticos."""
        atributos_dict = dict(self.ATRIBUTOS_DIETETICOS)
        badges = []
        for attr in self.get_atributos_lista():
            nombre = atributos_dict.get(attr, attr.title())
            color = self.get_color_atributo(attr)
            badges.append(f'<span class="badge {color} me-1">{nombre}</span>')
        return ' '.join(badges)

    def get_color_atributo(self, atributo):
        """Devuelve la clase CSS del color para cada atributo."""
        colores = {
            'organico': 'dietetica-organico',
            'vegano': 'dietetica-vegano',
            'sin_tacc': 'dietetica-sin-tacc',
            'sin_azucar': 'dietetica-sin-azucar',
            'integral': 'dietetica-integral',
            'natural': 'dietetica-natural',
        }
        return colores.get(atributo, 'bg-light text-dark')

    def estado_stock(self):
        if self.stock <= 0:
            return 'Agotado'
        elif self.stock <= self.stock_minimo:
            return 'Crítico'
        elif self.stock <= self.stock_minimo * 2:
            return 'Bajo'
        else:
            return 'Normal'
    estado_stock.short_description = 'Estado Stock'

    # ==================== CAMPOS PARA SISTEMA DE COSTOS AVANZADO ====================

    # Tipo de producto
    TIPOS_PRODUCTO = [
        ('reventa', 'Reventa Directa'),
        ('fraccionamiento', 'Fraccionamiento'),
        ('receta', 'Con Receta'),
    ]
    tipo_producto = models.CharField(
        max_length=20,
        choices=TIPOS_PRODUCTO,
        default='reventa',
        verbose_name="Tipo de Producto",
        help_text="Define cómo se calcula el costo del producto"
    )

    # Costos y márgenes
    costo_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Costo Base Unitario",
        help_text="Costo calculado automáticamente según el tipo de producto"
    )
    margen_ganancia = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30.00,
        verbose_name="Margen de Ganancia (%)",
        help_text="Porcentaje de ganancia sobre el costo base"
    )
    precio_venta_calculado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Precio de Venta Calculado",
        help_text="Precio calculado automáticamente: costo_base + margen"
    )
    actualizar_precio_automatico = models.BooleanField(
        default=True,
        verbose_name="Actualizar Precio Automáticamente",
        help_text="Si está marcado, el precio se actualiza cuando cambian los costos"
    )

    # Para fraccionamiento
    producto_origen = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='productos_fraccionados',
        verbose_name="Producto de Origen",
        help_text="Producto del cual se fracciona (para tipo fraccionamiento)"
    )
    unidad_compra = models.CharField(
        max_length=10,
        default='kg',
        verbose_name="Unidad de Compra",
        help_text="Unidad en que se compra el producto origen"
    )
    unidad_venta = models.CharField(
        max_length=10,
        default='kg',
        verbose_name="Unidad de Venta",
        help_text="Unidad en que se vende este producto"
    )
    factor_conversion = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=1.0000,
        verbose_name="Factor de Conversión",
        help_text="Cuántas unidades de venta salen de 1 unidad de compra"
    )
    cantidad_origen = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Cantidad del Producto Origen",
        help_text="Cantidad que se compra del producto origen"
    )
    cantidad_fraccion = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Cantidad por Fracción",
        help_text="Cantidad que contiene cada fracción"
    )

    # ==================== MÉTODOS PARA CÁLCULO DE COSTOS ====================

    def calcular_costo_unitario(self):
        """Calcula el costo unitario según el tipo de producto."""
        from decimal import Decimal
        costo_base = Decimal('0.00')

        if self.tipo_producto == 'reventa':
            # Para reventa, primero verificar si hay materia prima asociada
            if self.materia_prima_asociada and self.cantidad_fraccion:
                # cantidad_fraccion ahora está en la MISMA unidad que la materia prima
                # Ejemplo: MP en kg, cantidad_fraccion = 0.250 (kg)
                cantidad = Decimal(str(self.cantidad_fraccion))
                costo_base = self.materia_prima_asociada.costo_unitario * cantidad
            else:
                # Si no hay MP asociada, usar costo_base o precio
                costo_base = self.costo_base or Decimal(str(self.precio))

        elif self.tipo_producto == 'fraccionamiento':
            # Para fraccionamiento, dividir costo origen entre factor de conversión
            if self.producto_origen and self.factor_conversion > 0:
                costo_origen = self.producto_origen.calcular_costo_unitario()
                costo_base = costo_origen / Decimal(str(self.factor_conversion))

        elif self.tipo_producto == 'receta':
            # Para recetas, usar el costo total de la receta asignada
            if self.tiene_receta and self.receta:
                costo_base = self.receta.costo_total()
            elif self.materia_prima_asociada and self.cantidad_fraccion:
                # Fallback: si no tiene receta pero sí MP asociada (fraccionamiento)
                cantidad = Decimal(str(self.cantidad_fraccion))
                costo_base = self.materia_prima_asociada.costo_unitario * cantidad

        # Agregar costos indirectos si están configurados
        try:
            config = ConfiguracionCostos.objects.first()
            if config:
                peso_kg = float(self.cantidad_fraccion or 1000) / 1000  # Convertir gramos a kg
                es_fraccionamiento = self.tipo_producto == 'fraccionamiento'
                costos_indirectos = config.calcular_costos_indirectos(peso_kg, es_fraccionamiento)
                costo_base += costos_indirectos
        except Exception as e:
            logger.warning("Error calculando costos indirectos para producto '%s' (id=%s): %s", self, self.pk, e)

        return costo_base

    def calcular_precio_venta(self):
        """Calcula el precio de venta basado en costo + margen."""
        from decimal import Decimal
        costo = self.calcular_costo_unitario()
        if costo > 0 and self.margen_ganancia:
            margen_decimal = Decimal(str(self.margen_ganancia)) / Decimal('100')
            precio = costo * (Decimal('1') + margen_decimal)

            # Redondear si está configurado
            try:
                config = ConfiguracionCostos.objects.first()
                if config and config.redondear_precios:
                    # Redondear al peso más cercano (múltiplo de 50 centavos)
                    precio = (precio / Decimal('0.50')).quantize(Decimal('1')) * Decimal('0.50')
            except Exception as e:
                logger.warning("Error redondeando precio para producto '%s' (id=%s): %s", self, self.pk, e)

            return precio.quantize(Decimal('0.01'))
        return Decimal('0.00')

    def actualizar_costos_y_precios(self, guardar=True, usuario=None, motivo="Actualización automática", materia_prima_afectada=None):
        """Actualiza los costos y precios calculados."""
        costo_anterior = self.costo_base
        precio_anterior = self.precio_venta_calculado

        # Calcular nuevos valores
        nuevo_costo = self.calcular_costo_unitario()
        nuevo_precio = self.calcular_precio_venta()

        # Solo crear historial si hay cambios significativos
        if (abs(nuevo_costo - (costo_anterior or Decimal('0.00'))) > Decimal('0.01') or
            abs(nuevo_precio - (precio_anterior or Decimal('0.00'))) > Decimal('0.01')):

            # Guardar en histórico
            HistorialCosto.objects.create(
                producto=self,
                costo_anterior=costo_anterior,
                costo_nuevo=nuevo_costo,
                precio_anterior=precio_anterior,
                precio_nuevo=nuevo_precio,
                motivo=motivo,
                usuario=usuario,
                materia_prima_afectada=materia_prima_afectada
            )

        # Actualizar valores
        self.costo_base = nuevo_costo
        self.precio_venta_calculado = nuevo_precio

        if self.actualizar_precio_automatico:
            self.precio = float(self.precio_venta_calculado)

        if guardar:
            self.save()

    def save(self, *args, **kwargs):
        """Override save para validar stock y manejar sincronización de precios."""
        # ✅ VALIDACIÓN: Stock no puede ser negativo
        if self.stock < 0:
            from django.core.exceptions import ValidationError
            raise ValidationError(
                f'❌ El stock no puede ser negativo (stock actual: {self.stock}). '
                'Use un ajuste de inventario para corregir discrepancias.'
            )

        # Si actualizar_precio_automatico está activado y hay precio_venta_calculado,
        # sincronizar con el campo precio para compatibilidad
        if self.actualizar_precio_automatico and self.precio_venta_calculado:
            # Redondear el precio para que sea más práctico
            self.precio = round(float(self.precio_venta_calculado))
        elif self.precio_venta_calculado and not hasattr(self, '_skip_price_sync'):
            # Si no hay precio manual establecido, usar el calculado
            if not self.precio or self.precio == 0:
                self.precio = round(float(self.precio_venta_calculado))

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Compra(models.Model):
    """
    Pedido de compra a proveedor.
    Puede tener múltiples materias primas (CompraDetalle).
    """
    fecha_compra = models.DateField(auto_now_add=True)
    proveedor = models.CharField(max_length=100, verbose_name="Proveedor")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario que registró")

    # Campos legacy (mantener compatibilidad con compras antiguas)
    materia_prima = models.ForeignKey(
        'MateriaPrima',
        on_delete=models.CASCADE,
        related_name='compras',
        null=True,
        blank=True,
        help_text="Campo legacy - usar CompraDetalle para nuevas compras"
    )
    cantidad_mayoreo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Campo legacy - usar CompraDetalle para nuevas compras"
    )
    precio_mayoreo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Campo legacy - usar CompraDetalle para nuevas compras"
    )
    precio_unitario_mayoreo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        null=True,
        blank=True,
        help_text="Campo legacy - usar CompraDetalle para nuevas compras"
    )

    # Campos nuevos
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Total del Pedido"
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Compra al Mayoreo"
        verbose_name_plural = "Compras al Mayoreo"
        ordering = ['-fecha_compra']

    def __str__(self):
        return f"Compra #{self.id} - {self.proveedor} ({self.fecha_compra})"

    def calcular_total(self):
        """Calcula el total sumando todos los detalles."""
        if self.detalles.exists():
            total = sum([detalle.subtotal for detalle in self.detalles.all()])
            self.total = total
            self.save(update_fields=['total'])
        elif self.precio_mayoreo:
            # Legacy: usar precio_mayoreo si existe
            self.total = self.precio_mayoreo
            self.save(update_fields=['total'])

    def es_compra_legacy(self):
        """Verifica si es una compra antigua (sin detalles)."""
        return self.materia_prima is not None and not self.detalles.exists()

    def save(self, *args, **kwargs):
        # Calcula el precio unitario y actualiza el stock/costo de la materia prima
        if self.cantidad_mayoreo and self.precio_mayoreo:
            self.precio_unitario_mayoreo = self.precio_mayoreo / self.cantidad_mayoreo
        super().save(*args, **kwargs)
        materia = self.materia_prima
        # Aplica promedio ponderado para el costo unitario
        if materia:
            stock_anterior = materia.stock_actual
            costo_anterior = materia.costo_unitario
            nueva_cantidad = float(self.cantidad_mayoreo)
            nuevo_costo_total = float(self.precio_mayoreo)
            total_stock = float(stock_anterior) + nueva_cantidad
            if total_stock > 0:
                # Promedio ponderado
                nuevo_costo_unitario = (
                    (float(stock_anterior) * float(costo_anterior) + nuevo_costo_total)
                    / total_stock
                )
                materia.costo_unitario = nuevo_costo_unitario
            materia.stock_actual = total_stock
            materia.save()

            # FIFO: registra lote de materia prima
            from .models import LoteMateriaPrima
            LoteMateriaPrima.objects.create(
                materia_prima=materia,
                cantidad=nueva_cantidad,
                cantidad_disponible=nueva_cantidad,
                precio_unitario=self.precio_unitario_mayoreo,
                fecha_entrada=self.fecha_compra
            )


# ==================== MODELO COMPRA DETALLE ====================
class CompraDetalle(models.Model):
    """
    Detalle de una compra: cada materia prima dentro del pedido.
    Similar a VentaDetalle pero para compras.
    """
    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name="Compra"
    )
    materia_prima = models.ForeignKey(
        'MateriaPrima',
        on_delete=models.CASCADE,
        verbose_name="Materia Prima"
    )
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Cantidad",
        help_text="Cantidad comprada (usa la unidad de la materia prima)"
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Precio Unitario",
        help_text="Precio por unidad de medida"
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Subtotal",
        help_text="Calculado automáticamente: cantidad × precio_unitario"
    )

    class Meta:
        verbose_name = "Detalle de Compra"
        verbose_name_plural = "Detalles de Compras"
        ordering = ['id']

    def __str__(self):
        return f"{self.materia_prima.nombre} x{self.cantidad} @ ${self.precio_unitario} = ${self.subtotal}"

    def save(self, *args, **kwargs):
        """Calcula el subtotal y actualiza stock/costo de materia prima."""
        # 1. Calcular subtotal
        self.subtotal = self.cantidad * self.precio_unitario

        # 2. Guardar el detalle
        super().save(*args, **kwargs)

        # 3. Actualizar stock y costo de materia prima (promedio ponderado)
        materia = self.materia_prima
        stock_anterior = materia.stock_actual
        costo_anterior = materia.costo_unitario
        nueva_cantidad = float(self.cantidad)
        nuevo_costo_unitario = float(self.precio_unitario)

        # Calcular nuevo stock
        total_stock = float(stock_anterior) + nueva_cantidad

        # Calcular nuevo costo (promedio ponderado)
        if total_stock > 0:
            valor_anterior = float(stock_anterior) * float(costo_anterior)
            valor_nuevo = nueva_cantidad * nuevo_costo_unitario
            promedio_ponderado = (valor_anterior + valor_nuevo) / total_stock
            materia.costo_unitario = Decimal(str(promedio_ponderado))

        materia.stock_actual = Decimal(str(total_stock))
        materia.save()

        # 4. Crear lote FIFO
        from .models import LoteMateriaPrima
        LoteMateriaPrima.objects.create(
            materia_prima=materia,
            cantidad=self.cantidad,
            cantidad_disponible=self.cantidad,
            precio_unitario=self.precio_unitario,
            fecha_entrada=self.compra.fecha_compra
        )

        # 5. Actualizar total de la compra
        self.compra.calcular_total()


class LoteMateriaPrima(models.Model):
    materia_prima = models.ForeignKey('MateriaPrima', on_delete=models.CASCADE, related_name='lotes')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_disponible = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_entrada = models.DateField()
    fecha_consumo = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Lote de Materia Prima"
        verbose_name_plural = "Lotes de Materias Primas"
        ordering = ['fecha_entrada', 'id']

    def __str__(self):
        return f"{self.materia_prima.nombre} | {self.cantidad_disponible}/{self.cantidad} @ ${self.precio_unitario} ({self.fecha_entrada})"



class MateriaPrima(models.Model):
    """Modelo principal para materias primas: gestiona inventario, compras y stock."""
    UNIDADES_MEDIDA = [
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('l', 'Litros'),
        ('ml', 'Mililitros'),
        ('unidad', 'Unidades'),
        ('m', 'Metros'),
        ('cm', 'Centímetros'),
    ]

    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.CharField(max_length=10, choices=UNIDADES_MEDIDA)
    stock_actual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    stock_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    costo_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    proveedor = models.CharField(max_length=200, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Materia Prima"
        verbose_name_plural = "Materias Primas"
        ordering = ['nombre']
        permissions = [
            ('can_manage_materias_primas', 'Puede gestionar materias primas'),
            ('can_view_stock_reports', 'Puede ver reportes de stock'),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.get_unidad_medida_display()})"

    @property
    def necesita_restock(self):
        """Indica si la materia prima necesita reposición."""
        return self.stock_actual <= self.stock_minimo

    @property
    def valor_total_stock(self):
        """Calcula el valor total del stock actual."""
        return self.stock_actual * self.costo_unitario

    def actualizar_productos_relacionados(self, usuario=None):
        """Actualiza costos de productos que usan esta materia prima."""
        productos_afectados = []

        # Buscar productos que usan esta materia prima en recetas
        for receta_mp in self.recetas_materia_prima.all():
            producto = receta_mp.receta.producto
            if producto.tipo_producto == 'receta':
                if producto.actualizar_costos_y_precios(
                    usuario=usuario,
                    motivo=f"Cambio en precio de {self.nombre}",
                    materia_prima_afectada=self
                ):
                    productos_afectados.append(producto)

        # También buscar productos que derivan de productos que usan esta materia prima
        for producto in productos_afectados:
            # Buscar productos fraccionados de este producto
            for producto_fraccionado in producto.productos_fraccionados.all():
                if producto_fraccionado.actualizar_costos_y_precios(
                    usuario=usuario,
                    motivo=f"Cambio por actualización en {producto.nombre}",
                    materia_prima_afectada=self
                ):
                    productos_afectados.append(producto_fraccionado)

        return productos_afectados

    def save(self, *args, **kwargs):
        """🚀 Override save para versionado automático y actualizaciones."""
        costo_anterior = None
        proveedor_anterior = None

        if self.pk:  # Si ya existe
            try:
                obj_anterior = MateriaPrima.objects.get(pk=self.pk)
                costo_anterior = obj_anterior.costo_unitario
                proveedor_anterior = obj_anterior.proveedor or ""
            except MateriaPrima.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # 🎯 CREAR HISTORIAL AUTOMÁTICO CUANDO CAMBIA EL PRECIO
        if costo_anterior is not None and costo_anterior != self.costo_unitario:

            # Contar productos afectados
            productos_count = self.productos.count() if hasattr(self, 'productos') else 0

            # Crear registro histórico
            HistorialPreciosMateriaPrima.objects.create(
                materia_prima=self,
                precio_anterior=costo_anterior,
                precio_nuevo=self.costo_unitario,
                proveedor_anterior=proveedor_anterior or "",
                proveedor_nuevo=self.proveedor or "",
                productos_afectados_count=productos_count,
                motivo="Actualización automática de precio"
            )

            # Actualizar productos relacionados si está configurado
            try:
                config = ConfiguracionCostos.objects.first()
                if config and config.actualizar_automaticamente:
                    self.actualizar_productos_relacionados()
            except Exception as e:
                logger.error("Error actualizando productos relacionados para materia prima '%s' (id=%s): %s", self, self.pk, e)

    def crear_historial_manual(self, usuario, motivo="Cambio manual"):
        """🔍 Método para crear historial manualmente."""
        if hasattr(self, '_precio_anterior'):
            productos_count = self.productos.count()
            HistorialPreciosMateriaPrima.objects.create(
                materia_prima=self,
                precio_anterior=self._precio_anterior,
                precio_nuevo=self.costo_unitario,
                usuario=usuario,
                productos_afectados_count=productos_count,
                motivo=motivo
            )

class ProductoMateriaPrima(models.Model):
    """Receta: relación entre productos y materias primas (asociación y cantidad necesaria)."""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='recetas')
    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.CASCADE, related_name='productos')
    cantidad_necesaria = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Cantidad de materia prima necesaria por unidad de producto"
    )

    class Meta:
        verbose_name = "Receta de Producto"
        verbose_name_plural = "Recetas de Productos"
        unique_together = ['producto', 'materia_prima']

    def __str__(self):
        return f"{self.producto.nombre} - {self.materia_prima.nombre}: {self.cantidad_necesaria} {self.materia_prima.get_unidad_medida_display()}"

class MovimientoMateriaPrima(models.Model):
    """Registro de movimientos de inventario de materias primas (entradas, salidas, ajustes, producción, devolución)."""
    TIPOS_MOVIMIENTO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste de Inventario'),
        ('produccion', 'Uso en Producción'),
        ('devolucion', 'Devolución'),
    ]

    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.CASCADE, related_name='movimientos')
    tipo_movimiento = models.CharField(max_length=20, choices=TIPOS_MOVIMIENTO)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cantidad_nueva = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    motivo = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Movimiento de Materia Prima"
        verbose_name_plural = "Movimientos de Materias Primas"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.get_tipo_movimiento_display()} - {self.materia_prima.nombre}: {self.cantidad}"

class PerfilUsuario(models.Model):
    """Perfil de usuario con roles, permisos y datos adicionales."""
    ROLES = [
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('operador', 'Operador'),
        ('vendedor', 'Vendedor'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROLES, default='operador')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_rol_display()}"

    def tiene_permiso(self, accion):
        """Verifica si el usuario tiene permiso para una acción según su rol."""
        permisos_por_rol = {
            'admin': ['crear', 'editar', 'eliminar', 'ver', 'reportes', 'usuarios', 'backup'],
            'supervisor': ['crear', 'editar', 'ver', 'reportes'],
            'operador': ['ver', 'crear'],
            'vendedor': ['ver', 'crear_venta'],
        }
        return accion in permisos_por_rol.get(self.rol, [])


# ==================== MODELO RECETA ====================
class Receta(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la Receta")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    productos = models.ManyToManyField(
        Producto,
        related_name='recetas_producto',
        blank=True,
        verbose_name="Productos que usan esta receta"
    )
    materias_primas = models.ManyToManyField(
        MateriaPrima,
        through='RecetaMateriaPrima',
        related_name='recetas_materia',
        verbose_name="Materias Primas necesarias"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    activa = models.BooleanField(default=True, verbose_name="Receta Activa")
    creador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Creado por"
    )

    class Meta:
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"
        ordering = ['-fecha_modificacion']

    def __str__(self):
        return self.nombre

    def costo_total(self):
        """Calcula el costo total de la receta basado en las materias primas."""
        total = Decimal('0.00')
        for relacion in self.recetamateriaprima_set.all():
            total += relacion.costo_ingrediente()
        return total

    def productos_count(self):
        return self.productos.count()

    def materias_count(self):
        return self.materias_primas.count()


class RecetaMateriaPrima(models.Model):
    """Tabla intermedia para especificar cantidades de materias primas en recetas."""
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.CASCADE)
    cantidad = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name="Cantidad Necesaria"
    )
    unidad = models.CharField(
        max_length=20,
        choices=MateriaPrima.UNIDADES_MEDIDA,
        default='kg',
        verbose_name="Unidad de Medida"
    )
    notas = models.TextField(blank=True, null=True, verbose_name="Notas especiales")

    class Meta:
        verbose_name = "Materia Prima en Receta"
        verbose_name_plural = "Materias Primas en Recetas"
        unique_together = ['receta', 'materia_prima']

    def __str__(self):
        return f"{self.receta.nombre} - {self.materia_prima.nombre} ({self.cantidad} {self.unidad})"

    def costo_ingrediente(self):
        """Calcula el costo de esta materia prima en la receta."""
        if self.materia_prima.costo_unitario:
            return self.cantidad * self.materia_prima.costo_unitario
        return Decimal('0.00')


# ==================== MODELO HISTÓRICO DE COSTOS ====================
class HistorialCosto(models.Model):
    """Registro histórico de cambios en costos y precios de productos."""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='historial_costos')
    fecha = models.DateTimeField(auto_now_add=True)
    costo_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    costo_nuevo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_nuevo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    motivo = models.CharField(max_length=200, help_text="Razón del cambio de costo/precio")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Campos adicionales para contexto
    materia_prima_afectada = models.ForeignKey(
        'MateriaPrima',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Materia prima que causó el cambio (si aplica)"
    )
    precio_materia_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_materia_nuevo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Histórico de Costo"
        verbose_name_plural = "Histórico de Costos"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.producto.nombre} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"

    def porcentaje_cambio_costo(self):
        """Calcula el porcentaje de cambio en el costo."""
        if self.costo_anterior and self.costo_nuevo:
            cambio = ((self.costo_nuevo - self.costo_anterior) / self.costo_anterior) * 100
            return round(cambio, 2)
        return 0

    def porcentaje_cambio_precio(self):
        """Calcula el porcentaje de cambio en el precio."""
        if self.precio_anterior and self.precio_nuevo:
            cambio = ((self.precio_nuevo - self.precio_anterior) / self.precio_anterior) * 100
            return round(cambio, 2)
        return 0


# ==================== MODELO CONFIGURACIÓN DE COSTOS ====================
class ConfiguracionCostos(models.Model):
    """Configuración global para cálculo de costos indirectos."""

    # Costos indirectos por unidad
    costo_envases_por_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Costo Envases por KG",
        help_text="Costo promedio de envases por kilogramo de producto"
    )
    costo_etiquetas_por_unidad = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Costo Etiquetas por Unidad",
        help_text="Costo promedio de etiquetas por unidad de producto"
    )
    costo_envio_promedio = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Costo Envío Promedio",
        help_text="Costo promedio de envío por producto"
    )

    # Tiempo y mano de obra
    tiempo_fraccionamiento_por_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Tiempo Fraccionamiento (min/kg)",
        help_text="Minutos necesarios para fraccionar 1 kg de producto"
    )
    valor_hora_trabajo = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Valor Hora de Trabajo",
        help_text="Valor por hora de trabajo del emprendedor"
    )

    # Configuraciones globales
    incluir_costos_indirectos = models.BooleanField(
        default=False,
        verbose_name="Incluir Costos Indirectos",
        help_text="Si está marcado, se incluyen costos indirectos en el cálculo"
    )
    redondear_precios = models.BooleanField(
        default=True,
        verbose_name="Redondear Precios",
        help_text="Redondear precios finales al peso más cercano"
    )
    actualizar_automaticamente = models.BooleanField(
        default=True,
        verbose_name="Actualizar Precios Automáticamente",
        help_text="Actualizar precios cuando cambian los costos de materias primas"
    )

    # 🎯 OBJETIVOS DE NEGOCIO - Sistema de Métricas
    margen_objetivo = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('35.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Margen Objetivo (%)",
        help_text="Margen de rentabilidad objetivo para el negocio (ej: 35%)"
    )
    rotacion_objetivo = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('4.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Rotación Objetivo (veces/mes)",
        help_text="Veces que el inventario debería rotar por mes (ej: 4x)"
    )
    cobertura_objetivo_dias = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1)],
        verbose_name="Cobertura Objetivo (días)",
        help_text="Días de cobertura ideal de stock (ej: 30 días)"
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración de Costos"
        verbose_name_plural = "Configuración de Costos"

    def __str__(self):
        return f"Configuración de Costos - {self.fecha_modificacion.strftime('%d/%m/%Y')}"

    @classmethod
    def get_config(cls):
        """
        Obtiene o crea la configuración única del sistema.
        Garantiza que siempre exista exactamente una configuración.
        """
        config, created = cls.objects.get_or_create(pk=1)
        return config

    def calcular_costos_indirectos(self, peso_kg=1, es_fraccionamiento=False):
        """Calcula los costos indirectos para un producto."""
        if not self.incluir_costos_indirectos:
            return Decimal('0.00')

        costos = Decimal('0.00')

        # Costo de envases
        costos += self.costo_envases_por_kg * Decimal(str(peso_kg))

        # Costo de etiquetas (1 por producto)
        costos += self.costo_etiquetas_por_unidad

        # Costo de envío
        costos += self.costo_envio_promedio

        # Costo de mano de obra (solo para fraccionamiento)
        if es_fraccionamiento and self.tiempo_fraccionamiento_por_kg > 0:
            minutos_trabajo = self.tiempo_fraccionamiento_por_kg * Decimal(str(peso_kg))
            horas_trabajo = minutos_trabajo / Decimal('60')
            costo_trabajo = horas_trabajo * self.valor_hora_trabajo
            costos += costo_trabajo

        return costos


# ==================== 🚀 SISTEMA DE VERSIONADO AVANZADO ====================
class HistorialPreciosMateriaPrima(models.Model):
    """Registro histórico de cambios en precios de materias primas."""
    materia_prima = models.ForeignKey(
        MateriaPrima,
        on_delete=models.CASCADE,
        related_name='historial_precios'
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    precio_anterior = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio Anterior por Unidad"
    )
    precio_nuevo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio Nuevo por Unidad"
    )
    proveedor_anterior = models.CharField(max_length=200, blank=True)
    proveedor_nuevo = models.CharField(max_length=200, blank=True)
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario que realizó el cambio"
    )
    motivo = models.TextField(
        blank=True,
        verbose_name="Motivo del cambio",
        help_text="Razón del cambio de precio (ej: nueva compra, inflación, cambio de proveedor)"
    )

    # 🎯 IMPACTO EN PRODUCTOS FINALES
    productos_afectados_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Productos Afectados",
        help_text="Cantidad de productos que usan esta materia prima"
    )

    class Meta:
        verbose_name = "Historial de Precios - Materia Prima"
        verbose_name_plural = "Historial de Precios - Materias Primas"
        ordering = ['-fecha_cambio']
        # 🚀 ÍNDICES PARA CONSULTAS RÁPIDAS
        indexes = [
            models.Index(fields=['materia_prima', 'fecha_cambio'], name='mp_historial_idx'),
            models.Index(fields=['fecha_cambio'], name='fecha_cambio_idx'),
        ]

    def __str__(self):
        return f"{self.materia_prima.nombre} - {self.fecha_cambio.strftime('%d/%m/%Y')}"

    def porcentaje_cambio(self):
        """Calcula el porcentaje de cambio en el precio."""
        if self.precio_anterior > 0:
            cambio = ((self.precio_nuevo - self.precio_anterior) / self.precio_anterior) * 100
            return round(cambio, 2)
        return 0

    def diferencia_absoluta(self):
        """Calcula la diferencia absoluta en el precio."""
        return self.precio_nuevo - self.precio_anterior

    def impacto_economico_estimado(self):
        """Estima el impacto económico del cambio considerando stock actual."""
        diferencia = self.diferencia_absoluta()
        stock_actual = self.materia_prima.stock_actual or 0
        return diferencia * stock_actual


# ==================== 🔍 MANAGER PERSONALIZADO PARA VENTAS ====================
class VentaManager(models.Manager):
    """Manager personalizado para manejo de soft deletes en ventas."""

    def activas(self):
        """Retorna solo las ventas no eliminadas."""
        return self.filter(eliminada=False)

    def eliminadas(self):
        """Retorna solo las ventas eliminadas."""
        return self.filter(eliminada=True)

    def del_mes(self, fecha=None):
        """Retorna ventas activas del mes especificado (o actual)."""
        if not fecha:
            fecha = timezone.now().date()
        inicio_mes = fecha.replace(day=1)
        return self.activas().filter(fecha__date__gte=inicio_mes)

    def del_dia(self, fecha=None):
        """Retorna ventas activas del día especificado (o actual)."""
        if not fecha:
            fecha = timezone.now().date()
        return self.activas().filter(fecha__date=fecha)


# ==================== ⚖️ SISTEMA DE AJUSTES DE INVENTARIO ====================
class AjusteInventario(models.Model):
    """
    Sistema unificado para ajustes de stock de Productos y Materias Primas.
    Permite modificar el stock sin afectar costos ni registros de producción/compra.
    
    Casos de uso:
    - Inventario físico (conteo real difiere del sistema)
    - Merma/pérdida (productos vencidos, daños, derrames)
    - Correcciones de errores
    - Regalos/muestras
    """

    # 🎯 ITEM A AJUSTAR (solo uno puede tener valor)
    producto = models.ForeignKey(
        'Producto',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ajustes',
        verbose_name='Producto'
    )
    materia_prima = models.ForeignKey(
        'MateriaPrima',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ajustes',
        verbose_name='Materia Prima'
    )

    # 📊 DATOS DEL AJUSTE
    stock_anterior = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Stock Anterior'
    )
    stock_nuevo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Stock Nuevo'
    )
    diferencia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Diferencia',
        help_text='Positivo = incremento, Negativo = reducción'
    )

    # 🏷️ TIPO DE AJUSTE
    TIPO_CHOICES = [
        ('INVENTARIO_FISICO', 'Inventario Físico'),
        ('MERMA', 'Merma / Pérdida'),
        ('CORRECCION', 'Corrección de Error'),
        ('VENCIDO', 'Producto/MP Vencido'),
        ('REGALO', 'Regalo / Muestra'),
        ('DANIO', 'Daño / Derrame'),
        ('OTRO', 'Otro'),
    ]
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de Ajuste'
    )

    # 📝 AUDITORÍA
    razon = models.TextField(
        verbose_name='Razón del Ajuste',
        help_text='Descripción detallada del motivo del ajuste'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuario'
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y Hora'
    )

    class Meta:
        verbose_name = 'Ajuste de Inventario'
        verbose_name_plural = 'Ajustes de Inventario'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['producto', 'fecha'], name='ajuste_producto_idx'),
            models.Index(fields=['materia_prima', 'fecha'], name='ajuste_mp_idx'),
            models.Index(fields=['tipo', 'fecha'], name='ajuste_tipo_idx'),
            models.Index(fields=['fecha'], name='ajuste_fecha_idx'),
        ]

    def __str__(self):
        item = self.item_nombre
        signo = '+' if self.diferencia > 0 else ''
        return f"{item} - {self.stock_anterior}→{self.stock_nuevo} ({signo}{self.diferencia})"

    # 🔧 MÉTODOS HELPER
    @property
    def item_nombre(self):
        """Retorna el nombre del item ajustado con emoji."""
        if self.producto:
            return f"🍪 {self.producto.nombre}"
        elif self.materia_prima:
            return f"🧪 {self.materia_prima.nombre}"
        return "Sin item"

    @property
    def item_tipo(self):
        """Retorna el tipo de item: 'Producto' o 'Materia Prima'."""
        if self.producto:
            return "Producto"
        elif self.materia_prima:
            return "Materia Prima"
        return "Desconocido"

    @property
    def es_incremento(self):
        """True si el ajuste incrementa el stock."""
        return self.diferencia > 0

    @property
    def es_reduccion(self):
        """True si el ajuste reduce el stock."""
        return self.diferencia < 0

    @property
    def tipo_display(self):
        """Retorna el nombre legible del tipo de ajuste."""
        return dict(self.TIPO_CHOICES).get(self.tipo, self.tipo)

    def clean(self):
        """Validación: solo producto O materia prima puede tener valor."""
        from django.core.exceptions import ValidationError

        if self.producto and self.materia_prima:
            raise ValidationError(
                'Un ajuste debe ser para un Producto O una Materia Prima, no ambos.'
            )
        if not self.producto and not self.materia_prima:
            raise ValidationError(
                'Debe especificar un Producto o una Materia Prima.'
            )

    def save(self, *args, **kwargs):
        """Sobrescribe save para calcular la diferencia automáticamente."""
        self.diferencia = self.stock_nuevo - self.stock_anterior
        super().save(*args, **kwargs)
