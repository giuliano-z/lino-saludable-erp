
from django import forms
from .models import (
    Producto, Venta, Compra, MateriaPrima, ProductoMateriaPrima, MovimientoMateriaPrima, PerfilUsuario, VentaDetalle, Receta, AjusteInventario
)
from django.forms import inlineformset_factory


# Formulario placeholder para registrar ventas con verificación de materias primas
class VentaConMateriasForm(forms.Form):
    """Formulario placeholder para registrar ventas con verificación de materias primas."""
    # Puedes agregar campos y lógica según tus necesidades reales
    pass


class ProductoForm(forms.ModelForm):
    
    # Campo adicional para nueva categoría
    nueva_categoria = forms.CharField(
        required=False,
        label='Nueva Categoría',
        help_text='Escriba una nueva categoría si no encuentra la que busca',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de la nueva categoría...',
            'style': 'display: none;'  # Inicialmente oculto
        })
    )
    
    # Campo adicional para producción desde materias primas
    cantidad_a_producir = forms.IntegerField(
        required=False,
        label='Cantidad a Producir (unidades)',
        help_text='Número de unidades/bolsas/frascos a producir desde materias primas',
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'lino-input',
            'min': '0',
            'step': '1',
            'placeholder': 'Ej: 8 para producir 8 bolsas'
        })
    )

    class Meta:
        model = Producto
        fields = [
            # Información básica
            'nombre', 'descripcion', 'categoria', 'marca', 'origen',
            # Tipo de producto
            'tiene_receta', 'receta', 'materia_prima_asociada', 'cantidad_fraccion', 'tipo_producto',
            # Precio y stock
            'precio', 'stock', 'stock_minimo',
            # Otros
            'atributos_dieteticos'
        ]
        widgets = {
            # Información básica
            'nombre': forms.TextInput(attrs={
                'class': 'lino-input',
                'placeholder': 'Ej: Maní sin sal 500g'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'lino-textarea',
                'rows': 3,
                'placeholder': 'Descripción del producto (opcional)'
            }),
            'categoria': forms.Select(attrs={
                'class': 'lino-select',
                'id': 'id_categoria'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'lino-input',
                'placeholder': 'Marca del producto (opcional)'
            }),
            'origen': forms.TextInput(attrs={
                'class': 'lino-input',
                'placeholder': 'Origen del producto (opcional)'
            }),
            
            # Tipo de producto
            'tiene_receta': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_tiene_receta'
            }),
            'receta': forms.Select(attrs={
                'class': 'lino-select',
                'id': 'id_receta'
            }),
            'materia_prima_asociada': forms.Select(attrs={
                'class': 'lino-select',
                'id': 'id_materia_prima_asociada'
            }),
            'cantidad_fraccion': forms.NumberInput(attrs={
                'class': 'lino-input',
                'step': '0.001',  # Permitir decimales para mayor precisión
                'min': '0.001',
                'placeholder': 'Ej: 0.250 para 250gr si MP está en kg',
                'id': 'id_cantidad_fraccion'
            }),
            'tipo_producto': forms.HiddenInput(),  # Campo oculto, se calcula automáticamente
            
            # Precio y stock
            'precio': forms.NumberInput(attrs={
                'class': 'lino-input',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
                'id': 'id_precio'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'lino-input',
                'min': '0',
                'id': 'id_stock'
            }),
            'stock_minimo': forms.NumberInput(attrs={
                'class': 'lino-input',
                'min': '1',
                'id': 'id_stock_minimo'
            }),
            
            # Otros
            'atributos_dieteticos': forms.TextInput(attrs={
                'class': 'lino-input',
                'placeholder': 'Ej: organico,vegano,sin_tacc (separados por comas)'
            }),
        }
        labels = {
            'nombre': 'Nombre del Producto',
            'descripcion': 'Descripción',
            'categoria': 'Categoría',
            'marca': 'Marca',
            'origen': 'Origen',
            'tiene_receta': '¿Este producto usa una receta?',
            'receta': 'Receta',
            'materia_prima_asociada': 'Materia Prima Base',
            'cantidad_fraccion': 'Cantidad por unidad *',
            'precio': 'Precio de Venta ($)',
            'stock': 'Stock Actual (unidades)',
            'stock_minimo': 'Stock Mínimo',
            'atributos_dieteticos': 'Atributos Dietéticos',
            'marca': 'Marca',
            'origen': 'Origen',
        }
        help_texts = {
            'cantidad_fraccion': 'En LA MISMA UNIDAD que la MP. Ej: MP en kg → 0.250 (250gr), MP en litros → 0.500 (500ml), MP en unidades → 1',
            'precio': 'Precio al que vendés este producto',
            'stock': 'Cantidad de unidades listas para la venta',
            'tiene_receta': 'Marca si el producto se produce a partir de una receta',
            'atributos_dieteticos': 'Características especiales: orgánico, vegano, sin TACC, etc.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Obtener todas las categorías disponibles
        from .models import Producto
        
        # Categorías predefinidas
        categorias_predefinidas = list(Producto.CATEGORIAS_DIETETICA)
        
        # Categorías dinámicas de la base de datos
        categorias_bd = Producto.objects.exclude(categoria__in=[cat[0] for cat in Producto.CATEGORIAS_DIETETICA]).values_list('categoria', flat=True).distinct()
        categorias_dinamicas = [(cat, cat) for cat in categorias_bd if cat and cat.strip()]
        
        # Crear lista completa de opciones
        todas_categorias = categorias_predefinidas + categorias_dinamicas
        
        # Configurar el widget del campo categoria
        self.fields['categoria'].widget.choices = todas_categorias
        
        # Configurar el campo receta (sistema de costos)
        if 'receta' in self.fields:
            self.fields['receta'].queryset = Receta.objects.all()
            self.fields['receta'].required = False
            self.fields['receta'].empty_label = "Selecciona una receta"
            
        # Configurar el campo materia_prima_asociada
        if 'materia_prima_asociada' in self.fields:
            self.fields['materia_prima_asociada'].queryset = MateriaPrima.objects.all()
            self.fields['materia_prima_asociada'].required = False
            self.fields['materia_prima_asociada'].empty_label = "Selecciona materia prima"
            
        # Configurar el campo producto_origen (para fraccionamiento)
        if 'producto_origen' in self.fields:
            self.fields['producto_origen'].queryset = Producto.objects.exclude(tipo_producto='fraccionamiento')
            self.fields['producto_origen'].required = False
            self.fields['producto_origen'].empty_label = "Seleccionar producto origen"
        
        # Configurar campos del sistema de costos
        if 'tipo_producto' in self.fields:
            self.fields['tipo_producto'].required = False  # Se calcula automáticamente en clean()
            
        if 'costo_base' in self.fields:
            self.fields['costo_base'].required = False
            
        if 'margen_ganancia' in self.fields:
            self.fields['margen_ganancia'].required = False
            
        if 'precio_venta_calculado' in self.fields:
            self.fields['precio_venta_calculado'].required = False
            
        # Hacer campos de fraccionamiento opcionales por defecto
        campos_fraccionamiento = ['unidad_compra', 'unidad_venta', 'factor_conversion', 'cantidad_origen', 'cantidad_fraccion']
        for campo in campos_fraccionamiento:
            if campo in self.fields:
                self.fields[campo].required = False

    def clean(self):
        cleaned_data = super().clean()
        categoria = cleaned_data.get('categoria')
        nueva_categoria = cleaned_data.get('nueva_categoria')
        tipo_producto = cleaned_data.get('tipo_producto')
        
        # 🛡️ BUG-B FIX: Validación independiente de tiene_receta
        # Esta validación ocurre SIN importar el tipo_producto
        # Si el usuario marca "¿Usa receta?" DEBE seleccionar una receta
        tiene_receta = cleaned_data.get('tiene_receta')
        receta = cleaned_data.get('receta')
        
        if tiene_receta and not receta:
            raise forms.ValidationError(
                '❌ Si marca "¿Usa receta?" debe seleccionar una receta. '
                'Si el producto NO usa receta, desmarca la opción.'
            )
        
        # Si no se especificó tipo_producto, establecer valor por defecto basado en configuración
        if not tipo_producto:
            # Determinar tipo basado en si tiene receta o materia prima
            if cleaned_data.get('tiene_receta') and cleaned_data.get('receta'):
                cleaned_data['tipo_producto'] = 'receta'
            elif cleaned_data.get('materia_prima_asociada'):
                cleaned_data['tipo_producto'] = 'reventa'  # Fraccionamiento/reventa
            else:
                cleaned_data['tipo_producto'] = 'reventa'  # Por defecto reventa
            tipo_producto = cleaned_data['tipo_producto']
        
        # Si seleccionó "nueva" pero no escribió una nueva categoría
        if categoria == 'nueva':
            if not nueva_categoria:
                raise forms.ValidationError('Debe escribir el nombre de la nueva categoría')
            
            # Convertir a formato slug para coherencia
            nueva_cat_slug = nueva_categoria.lower().replace(' ', '_').replace('ñ', 'n')
            cleaned_data['categoria'] = nueva_cat_slug
            
            # Verificar que no exista ya
            from .models import Producto
            if nueva_cat_slug in [choice[0] for choice in Producto.CATEGORIAS_DIETETICA]:
                raise forms.ValidationError(f'La categoría "{nueva_categoria}" ya existe')
        
        # Validaciones condicionales según el tipo de producto
        if tipo_producto:
            if tipo_producto == 'fraccionamiento':
                # Para fraccionamiento, validar campos específicos
                if not cleaned_data.get('producto_origen'):
                    raise forms.ValidationError('Para productos fraccionados debe seleccionar un producto origen')
                if not cleaned_data.get('factor_conversion'):
                    raise forms.ValidationError('Para productos fraccionados debe especificar el factor de conversión')
                if not cleaned_data.get('unidad_compra'):
                    raise forms.ValidationError('Para productos fraccionados debe especificar la unidad de compra')
                if not cleaned_data.get('unidad_venta'):
                    raise forms.ValidationError('Para productos fraccionados debe especificar la unidad de venta')
            
            elif tipo_producto == 'receta':
                # Para recetas, validar que tenga receta asociada
                if cleaned_data.get('tiene_receta') and not cleaned_data.get('receta'):
                    raise forms.ValidationError('Para productos con receta debe seleccionar una receta')
            
            # Para todos los tipos, margen de ganancia es opcional pero si se especifica debe ser válido
            margen = cleaned_data.get('margen_ganancia')
            if margen is not None and margen < 0:
                raise forms.ValidationError('El margen de ganancia no puede ser negativo')
        
        # En edición, cantidad_a_producir puede ser vacía o 0
        if self.instance and self.instance.pk:
            cantidad = cleaned_data.get('cantidad_a_producir')
            if cantidad is not None and cantidad < 1:
                cleaned_data['cantidad_a_producir'] = None
        
        # ============================================================
        # 🛡️ VALIDADORES DE SEGURIDAD ROBUSTOS
        # ============================================================
        
        # 1. Precio debe ser positivo
        precio = cleaned_data.get('precio')
        if precio is not None:
            if precio <= 0:
                raise forms.ValidationError('El precio de venta debe ser mayor a 0')
            if precio > 999999:
                raise forms.ValidationError('El precio de venta no puede exceder $999,999')
        
        # 2. Stock debe ser no negativo
        stock = cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError('El stock no puede ser negativo')
        
        # 3. Stock mínimo debe ser no negativo
        stock_min = cleaned_data.get('stock_minimo')
        if stock_min is not None and stock_min < 0:
            raise forms.ValidationError('El stock mínimo no puede ser negativo')
        
        # 4. Cantidad de fracción debe ser positiva
        cant_fracc = cleaned_data.get('cantidad_fraccion')
        if cant_fracc is not None and cant_fracc <= 0:
            raise forms.ValidationError('La cantidad por unidad debe ser mayor a 0')
        
        # 5. Límite de caracteres en campos de texto
        nombre = cleaned_data.get('nombre', '')
        if len(nombre) > 200:
            raise forms.ValidationError('El nombre no puede exceder 200 caracteres')
        
        descripcion = cleaned_data.get('descripcion', '')
        if len(descripcion) > 1000:
            raise forms.ValidationError('La descripción no puede exceder 1000 caracteres')
        
        # 6. Sanitizar caracteres peligrosos en nombre
        import re
        if nombre and not re.match(r'^[a-zA-Z0-9\s\-_áéíóúÁÉÍÓÚñÑ.,()%°]+$', nombre):
            raise forms.ValidationError('El nombre contiene caracteres no permitidos')
                
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Establecer tipo_producto basado en la configuración
        if instance.tiene_receta and instance.receta:
            instance.tipo_producto = 'receta'
        elif instance.materia_prima_asociada:
            instance.tipo_producto = 'reventa'  # Fraccionamiento/reventa
        else:
            instance.tipo_producto = 'reventa'  # Por defecto reventa
        
        # El campo categoria ya viene procesado del clean()
        if commit:
            instance.save()
        return instance

## Formulario para la cabecera de la venta
class VentaForm(forms.ModelForm):
    # Campo de fecha validado en servidor - NO depender solo de input HTML
    fecha = forms.DateField(
        required=True,
        label='Fecha de Venta',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text='Selecciona la fecha en que se realizó la venta'
    )
    
    class Meta:
        model = Venta
        fields = ['cliente', 'fecha']
        widgets = {
            'cliente': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nombre del cliente (opcional)'
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

## Formulario para cada producto en la venta
class VentaDetalleForm(forms.ModelForm):
    class Meta:
        model = VentaDetalle
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 🔧 FIX: Filtrar solo productos disponibles para venta
        # Mostrar solo productos con stock disponible
        self.fields['producto'].queryset = Producto.objects.filter(
            stock__gt=0  # Solo productos con stock
        ).order_by('nombre')
        
        # Mensaje de ayuda si no hay productos disponibles
        if not self.fields['producto'].queryset.exists():
            self.fields['producto'].empty_label = "No hay productos disponibles para venta"
        else:
            self.fields['producto'].empty_label = "Seleccione un producto"

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        
        # Validar que cantidad sea positiva
        if cantidad is not None and cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a 0')
        
        if producto and cantidad:
            if cantidad > producto.stock:
                raise forms.ValidationError(
                    f'No hay suficiente stock para {producto.nombre}. Disponible: {producto.stock}'
                )
        return cleaned_data

## Formset para múltiples productos en una venta
VentaDetalleFormSet = inlineformset_factory(
    Venta,
    VentaDetalle,
    form=VentaDetalleForm,
    extra=1,
    can_delete=True
)

class CompraForm(forms.ModelForm):
    """Formulario para registrar compras de materias primas."""
    materia_prima = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Materia Prima',
        help_text='Selecciona la materia prima a comprar'
    )

    def __init__(self, *args, **kwargs):
        from .models import MateriaPrima
        super().__init__(*args, **kwargs)
        self.fields['materia_prima'].queryset = MateriaPrima.objects.filter(activo=True)
        # Si hay una materia prima seleccionada, sugerir proveedor automáticamente
        if 'materia_prima' in self.data:
            try:
                mp_id = int(self.data.get('materia_prima'))
                mp = MateriaPrima.objects.get(pk=mp_id)
                self.fields['proveedor'].initial = mp.proveedor
            except Exception:
                pass
        elif self.instance.pk and self.instance.materia_prima:
            self.fields['proveedor'].initial = self.instance.materia_prima.proveedor

    class Meta:
        model = Compra
        fields = ['materia_prima', 'proveedor', 'cantidad_mayoreo', 'precio_mayoreo']
        widgets = {
            'proveedor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del proveedor'
            }),
            'cantidad_mayoreo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Cantidad'
            }),
            'precio_mayoreo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Precio total de la compra'
            }),
        }
        labels = {
            'proveedor': 'Proveedor',
            'materia_prima': 'Materia Prima',
            'cantidad_mayoreo': 'Cantidad',
            'precio_mayoreo': 'Precio Total ($)',
        }

    def clean_cantidad_mayoreo(self):
        cantidad = self.cleaned_data.get('cantidad_mayoreo')
        if cantidad and cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a 0')
        if cantidad and cantidad > 999999:
            raise forms.ValidationError('La cantidad no puede exceder 999,999')
        return cantidad

    def clean_precio_mayoreo(self):
        precio = self.cleaned_data.get('precio_mayoreo')
        if precio and precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0')
        if precio and precio > 99999999:
            raise forms.ValidationError('El precio no puede exceder $99,999,999')
        return precio
    
    def clean_proveedor(self):
        """Validar proveedor contra inyección"""
        proveedor = self.cleaned_data.get('proveedor', '')
        if len(proveedor) > 100:
            raise forms.ValidationError('El nombre del proveedor no puede exceder 100 caracteres')
        
        import re
        if proveedor and not re.match(r'^[a-zA-Z0-9\s\-_áéíóúÁÉÍÓÚñÑ.,&()]+$', proveedor):
            raise forms.ValidationError('El nombre del proveedor contiene caracteres no permitidos')
        
        return proveedor

## Formularios principales para materias primas, productos y movimientos

class MateriaPrimaForm(forms.ModelForm):
    """Formulario para crear o editar materias primas."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer activo=True por defecto al crear nueva materia prima
        if not self.instance.pk:  # Solo si es nuevo (no tiene ID)
            self.initial['activo'] = True
    
    class Meta:
        model = MateriaPrima
        fields = ['nombre', 'descripcion', 'unidad_medida', 'stock_actual', 
                 'stock_minimo', 'costo_unitario', 'proveedor', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unidad_medida': forms.Select(attrs={'class': 'form-control'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'costo_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre de la Materia Prima',
            'descripcion': 'Descripción',
            'unidad_medida': 'Unidad de Medida',
            'stock_actual': 'Stock Actual',
            'stock_minimo': 'Stock Mínimo',
            'costo_unitario': 'Costo Unitario ($)',
            'proveedor': 'Proveedor Principal',
            'activo': 'Materia Prima Activa',
        }

class ProductoMateriaPrimaForm(forms.ModelForm):
    """Formulario para asociar materias primas a productos."""
    class Meta:
        model = ProductoMateriaPrima
        fields = ['producto', 'materia_prima', 'cantidad_necesaria']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'materia_prima': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_necesaria': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'producto': 'Producto',
            'materia_prima': 'Materia Prima',
            'cantidad_necesaria': 'Cantidad Necesaria',
        }

class MovimientoMateriaPrimaForm(forms.ModelForm):
    """Formulario para registrar movimientos de materias primas."""
    class Meta:
        model = MovimientoMateriaPrima
        fields = ['materia_prima', 'tipo_movimiento', 'cantidad', 'motivo']
        widgets = {
            'materia_prima': forms.Select(attrs={'class': 'form-control'}),
            'tipo_movimiento': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'materia_prima': 'Materia Prima',
            'tipo_movimiento': 'Tipo de Movimiento',
            'cantidad': 'Cantidad',
            'motivo': 'Motivo/Observaciones',
        }

class PerfilUsuarioForm(forms.ModelForm):
    """Formulario para editar perfil de usuario."""
    class Meta:
        model = PerfilUsuario
        fields = ['rol', 'telefono', 'departamento']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'rol': 'Rol del Usuario',
            'telefono': 'Teléfono',
            'departamento': 'Departamento',
        }


## Formulario para búsqueda y filtros de materias primas
class BusquedaMateriaPrimaForm(forms.Form):
    busqueda = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre...'
        })
    )
    unidad_medida = forms.ChoiceField(
        required=False,
        choices=[('', 'Todas las unidades')] + MateriaPrima.UNIDADES_MEDIDA,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    stock_bajo = forms.BooleanField(
        required=False,
        label="Solo mostrar stock bajo",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


# ==================== FORMULARIO RECETA ====================
class RecetaForm(forms.ModelForm):
    """Formulario para crear y editar recetas."""
    
    class Meta:
        model = Receta
        fields = ['nombre', 'descripcion', 'productos', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la receta...'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la receta...'
            }),
            'productos': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '5'
            }),
            'activa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'nombre': 'Nombre de la Receta',
            'descripcion': 'Descripción',
            'productos': 'Productos que usan esta receta',
            'activa': 'Receta activa',
        }
        help_texts = {
            'nombre': 'Ingrese un nombre descriptivo para la receta',
            'descripcion': 'Agregue detalles sobre la preparación o características',
            'productos': 'Seleccione los productos que utilizarán esta receta',
            'activa': 'Marque si la receta está activa y puede utilizarse',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar queryset de productos
        self.fields['productos'].queryset = Producto.objects.filter(
            tiene_receta=True
        ).order_by('nombre')
        
        # Hacer que el campo nombre sea requerido y único
        self.fields['nombre'].required = True
        
        # Configurar valor por defecto para activa
        if not self.instance.pk:
            self.fields['activa'].initial = True

    def save(self, commit=True):
        """Guarda la receta y maneja las materias primas dinámicas."""
        receta = super().save(commit=commit)
        
        if commit:
            # Aquí procesaremos los ingredientes dinámicos
            # Esta lógica se implementará en la vista
            pass
            
        return receta


# ==================== ⚖️ FORMULARIOS DE AJUSTES DE INVENTARIO ====================

class AjusteProductoForm(forms.ModelForm):
    """Formulario para ajustar stock de productos terminados."""
    
    stock_nuevo = forms.DecimalField(
        label='Nuevo Stock',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'lino-input',
            'placeholder': 'Ej: 10',
            'step': '0.01',
            'min': '0'
        })
    )
    
    class Meta:
        model = AjusteInventario
        fields = ['producto', 'stock_nuevo', 'tipo', 'razon']
        widgets = {
            'producto': forms.Select(attrs={
                'class': 'lino-select',
                'id': 'id_producto_ajuste'
            }),
            'tipo': forms.Select(attrs={
                'class': 'lino-select'
            }),
            'razon': forms.Textarea(attrs={
                'class': 'lino-textarea',
                'rows': 3,
                'placeholder': 'Ej: Conteo físico encontró 3 unidades más de lo registrado'
            })
        }
    
    def __init__(self, *args, **kwargs):
        # Extraer producto_id si viene en kwargs
        producto_id = kwargs.pop('producto_id', None)
        super().__init__(*args, **kwargs)
        
        # Ordenar productos por nombre
        self.fields['producto'].queryset = Producto.objects.all().order_by('nombre')
        
        # Si viene producto_id, pre-seleccionar y ocultar el campo
        if producto_id:
            try:
                producto = Producto.objects.get(id=producto_id)
                self.fields['producto'].initial = producto
                self.fields['producto'].widget.attrs['readonly'] = True
                self.producto_preseleccionado = producto
            except Producto.DoesNotExist:
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        stock_nuevo = cleaned_data.get('stock_nuevo')
        
        if producto and stock_nuevo is not None:
            # Guardar stock anterior para el save
            cleaned_data['stock_anterior'] = producto.stock
            
        return cleaned_data
    
    def save(self, commit=True):
        ajuste = super().save(commit=False)
        
        # Establecer stock_anterior desde el producto
        if ajuste.producto:
            ajuste.stock_anterior = ajuste.producto.stock
            
        if commit:
            ajuste.save()
            # Actualizar el stock del producto
            ajuste.producto.stock = ajuste.stock_nuevo
            ajuste.producto.save()
            
        return ajuste


class AjusteMateriaPrimaForm(forms.ModelForm):
    """Formulario para ajustar stock de materias primas."""
    
    stock_nuevo = forms.DecimalField(
        label='Nuevo Stock',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'lino-input',
            'placeholder': 'Ej: 8.5',
            'step': '0.01',
            'min': '0'
        })
    )
    
    class Meta:
        model = AjusteInventario
        fields = ['materia_prima', 'stock_nuevo', 'tipo', 'razon']
        widgets = {
            'materia_prima': forms.Select(attrs={
                'class': 'lino-select',
                'id': 'id_mp_ajuste'
            }),
            'tipo': forms.Select(attrs={
                'class': 'lino-select'
            }),
            'razon': forms.Textarea(attrs={
                'class': 'lino-textarea',
                'rows': 3,
                'placeholder': 'Ej: Bolsa rota, se perdieron 2kg en almacén'
            })
        }
    
    def __init__(self, *args, **kwargs):
        # Extraer materia_prima_id si viene en kwargs
        mp_id = kwargs.pop('materia_prima_id', None)
        super().__init__(*args, **kwargs)
        
        # Ordenar materias primas por nombre, solo activas
        self.fields['materia_prima'].queryset = MateriaPrima.objects.filter(
            activo=True
        ).order_by('nombre')
        
        # Si viene mp_id, pre-seleccionar
        if mp_id:
            try:
                mp = MateriaPrima.objects.get(id=mp_id)
                self.fields['materia_prima'].initial = mp
                self.fields['materia_prima'].widget.attrs['readonly'] = True
                self.mp_preseleccionada = mp
            except MateriaPrima.DoesNotExist:
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        materia_prima = cleaned_data.get('materia_prima')
        stock_nuevo = cleaned_data.get('stock_nuevo')
        
        if materia_prima and stock_nuevo is not None:
            # Guardar stock anterior para el save
            cleaned_data['stock_anterior'] = materia_prima.stock_actual
            
        return cleaned_data
    
    def save(self, commit=True):
        ajuste = super().save(commit=False)
        
        # Establecer stock_anterior desde la materia prima
        if ajuste.materia_prima:
            ajuste.stock_anterior = ajuste.materia_prima.stock_actual
            
        if commit:
            ajuste.save()
            # Actualizar el stock de la materia prima
            ajuste.materia_prima.stock_actual = ajuste.stock_nuevo
            ajuste.materia_prima.save()
            
        return ajuste