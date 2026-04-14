# ==================== VISTAS DE VENTAS ====================
"""
Módulo de vistas para la gestión de ventas.
Funcionalidades:
- CRUD de ventas con validación de stock
- Registro detallado de movimientos de stock
- Exportación de datos
- Logging robusto para transacciones de dinero
"""

# ==================== IMPORTS ====================
import traceback
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django_ratelimit.decorators import ratelimit

from .forms import VentaDetalleFormSet, VentaForm
from .logging_system import LinoLogger, get_request_info
from .models import Venta
from .resources import VentaResource

# ==================== VISTAS DE VENTAS ====================

@login_required
def lista_ventas(request):
    """Vista de lista de ventas con KPIs LINO V3."""
    from django.core.paginator import Paginator

    from gestion.utils.kpi_builder import prepare_ventas_kpis

    ventas = Venta.objects.filter(eliminada=False).prefetch_related('detalles__producto')

    # Filtros
    query = request.GET.get('q')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if query:
        ventas = ventas.filter(
            Q(cliente__icontains=query) |
            Q(detalles__producto__nombre__icontains=query)
        ).distinct()

    if fecha_inicio:
        ventas = ventas.filter(fecha__date__gte=fecha_inicio)

    if fecha_fin:
        ventas = ventas.filter(fecha__date__lte=fecha_fin)

    # Ventas del mes para KPIs
    ventas_mes = Venta.objects.filter(
        eliminada=False,
        fecha__month=timezone.now().month,
        fecha__year=timezone.now().year
    )

    # Preparar KPIs
    kpis = prepare_ventas_kpis(ventas_mes)

    # Paginación
    paginator = Paginator(ventas.order_by('-fecha'), 25)
    page_number = request.GET.get('page', 1)
    ventas_paginadas = paginator.get_page(page_number)

    # Clientes activos (únicos)
    clientes_activos = ventas.exclude(cliente__isnull=True).exclude(cliente__exact='').values('cliente').distinct().count()

    context = {
        'ventas': ventas_paginadas,
        'kpis': kpis,
        'query': query,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'clientes_activos': clientes_activos,
        'title': 'Ventas',
        'subtitle': 'Gestión completa de ventas y transacciones',
        'icon': 'cart-check',
        'create_url': reverse('gestion:crear_venta'),
        'export_url': reverse('gestion:exportar_ventas'),
    }

    return render(request, 'modules/ventas/lista.html', context)


@login_required
@ratelimit(key='user', rate=getattr(settings, 'RATELIMIT_VENTAS', '30/h'), method='POST', block=True)
def crear_venta(request):
    """
    Vista CRÍTICA: Crear venta con logging robusto y validaciones completas.
    Esta función maneja dinero real - cualquier error debe ser trackeado.
    """
    # Obtener información de la request para logging
    request_info = get_request_info(request)

    # Log del intento de acceso
    LinoLogger.log_accion_admin(request.user, "INTENTO_CREAR_VENTA", "Venta", 0)

    # Verificar permisos
    if not request.user.has_perm('gestion.add_venta'):
        LinoLogger.log_error_critico(
            "ventas", "crear_venta",
            f"Usuario {request.user.username} sin permisos",
            request_info
        )
        messages.error(request, 'No tienes permiso para registrar ventas.')
        return redirect('gestion:lista_ventas')

    if request.method == 'POST':
        form = VentaForm(request.POST)
        formset = VentaDetalleFormSet(request.POST, prefix='form')

        # Log del intento de procesamiento
        LinoLogger.business_logger.info(f"PROCESANDO VENTA - Usuario: {request.user.username}")

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Crear venta base
                    venta = form.save(commit=False)
                    venta.usuario = request.user  # Asignar usuario que crea la venta
                    venta.save()

                    total = Decimal('0.00')
                    errores_stock = []
                    productos_vendidos = []

                    # Procesar detalles de la venta
                    detalles = formset.save(commit=False)

                    # VALIDACIÓN CRÍTICA: Verificar stock ANTES de procesar
                    for detalle in detalles:
                        producto = detalle.producto
                        if not producto:
                            LinoLogger.log_venta_error("PRODUCTO_NULO", detalle.cantidad,
                                                     "Detalle sin producto asociado", request.user)
                            errores_stock.append("Producto no válido")
                            continue

                        if detalle.cantidad <= 0:
                            LinoLogger.log_venta_error(producto.nombre, detalle.cantidad,
                                                     "Cantidad inválida (≤0)", request.user)
                            errores_stock.append(f"{producto.nombre}: cantidad inválida")
                            continue

                        if producto.stock < detalle.cantidad:
                            LinoLogger.log_venta_error(producto.nombre, detalle.cantidad,
                                                     f"Stock insuficiente. Disponible: {producto.stock}",
                                                     request.user)
                            errores_stock.append(f"{producto.nombre} (disponible: {producto.stock})")
                            continue

                    # Si hay errores de stock, abortar la transacción
                    if errores_stock:
                        LinoLogger.log_venta_error("MULTIPLE_PRODUCTOS", len(detalles),
                                                 f"Errores de stock: {', '.join(errores_stock)}",
                                                 request.user)
                        messages.error(request, 'No hay suficiente stock para: ' + ", ".join(errores_stock))
                        transaction.set_rollback(True)
                        return render(request, 'modules/ventas/form_v3_natural.html', {
                            'form': form,
                            'formset': formset,
                            'titulo': 'Registrar Venta'
                        })

                    # Procesar cada detalle exitosamente
                    for detalle in detalles:
                        producto = detalle.producto
                        stock_anterior = producto.stock

                        # Actualizar stock
                        producto.stock -= detalle.cantidad

                        # Detectar stock crítico ANTES de guardar
                        if producto.stock <= producto.stock_minimo:
                            if producto.stock == 0:
                                LinoLogger.log_stock_agotado(producto.nombre)
                            else:
                                LinoLogger.log_stock_critico(producto.nombre, producto.stock, producto.stock_minimo)

                        producto.save()

                        # Log del cambio de stock
                        LinoLogger.log_stock_actualizado(
                            producto.nombre, stock_anterior, producto.stock,
                            f"Venta ID: {venta.id}", request.user
                        )

                        # Configurar detalle
                        detalle.venta = venta
                        if not detalle.precio_unitario:
                            detalle.precio_unitario = producto.precio
                        if not detalle.subtotal or detalle.subtotal == 0:
                            detalle.subtotal = detalle.cantidad * detalle.precio_unitario

                        detalle.save()
                        total += detalle.subtotal

                        productos_vendidos.append({
                            'nombre': producto.nombre,
                            'cantidad': detalle.cantidad,
                            'subtotal': detalle.subtotal
                        })

                    # Actualizar total de la venta
                    venta.total = total
                    venta.save()

                    # LOG EXITOSO de venta creada
                    productos_str = ', '.join([f"{p['nombre']} x{p['cantidad']}" for p in productos_vendidos])
                    LinoLogger.log_venta_creada(venta.id, productos_str, len(detalles), total, request.user)

                    messages.success(request, f'✅ Venta #{venta.id} registrada exitosamente. Total: ${total}. Stock actualizado.')
                    return redirect('gestion:lista_ventas')

            except Exception as e:
                # Log detallado del error
                error_trace = traceback.format_exc()
                LinoLogger.log_error_critico(
                    "ventas", "crear_venta",
                    f"Excepción no controlada: {str(e)}",
                    {"traceback": error_trace, "request_info": request_info}
                )
                messages.error(request, f'❌ Error crítico al registrar la venta. Contacte al administrador. Error: {str(e)}')

        else:
            # Log de errores de validación
            form_errors = form.errors.as_json() if form.errors else "Sin errores"
            formset_errors = []
            for form_error in formset.errors:
                if form_error:
                    formset_errors.append(str(form_error))

            LinoLogger.log_venta_error("FORMULARIO_INVALIDO", 0,
                                     f"Form errors: {form_errors}, Formset errors: {formset_errors}",
                                     request.user)
            messages.error(request, 'Formulario inválido. Verifica todos los campos.')
    else:
        # GET request - mostrar formulario vacío
        form = VentaForm()
        formset = VentaDetalleFormSet(prefix='form')
        LinoLogger.business_logger.info(f"FORMULARIO_VENTA_CARGADO - Usuario: {request.user.username}")

    return render(request, 'modules/ventas/form_v3_natural.html', {
        'form': form,
        'formset': formset,
        'titulo': 'Registrar Venta'
    })


@login_required
def eliminar_venta(request, pk):
    """
    ELIMINACIÓN SEGURA CON SOFT DELETE - ARQUITECTURA DB PROFESIONAL.
    Restaura stock de productos y mantiene historial para auditoría.
    """
    venta = get_object_or_404(Venta, pk=pk, eliminada=False)  # Solo ventas activas

    if not request.user.has_perm('gestion.delete_venta'):
        messages.error(request, 'No tienes permiso para eliminar ventas.')
        return redirect('gestion:lista_ventas')

    if request.method == 'POST':
        razon = request.POST.get('razon_eliminacion', '')

        try:
            with transaction.atomic():
                # Guardar información para el mensaje
                monto_venta = venta.total
                productos_restaurados = []

                # Restaurar stock de productos
                detalles = venta.detalles.all()
                for detalle in detalles:
                    producto = detalle.producto
                    producto.stock += detalle.cantidad
                    producto.save()
                    productos_restaurados.append(f"{detalle.producto.nombre} (+{detalle.cantidad})")

                # 🚀 SOFT DELETE - No eliminar, solo marcar
                venta.eliminar_venta(request.user, razon)

                # Mensaje detallado del impacto
                mensaje = 'Venta marcada como eliminada exitosamente. '
                mensaje += 'Se mantiene el historial para auditoría. '
                mensaje += f'Stock restaurado: {", ".join(productos_restaurados)}.'

                messages.success(request, mensaje)

                # Auditoría: registrar acción
                # LogVenta.objects.create(usuario=request.user, accion='eliminar', venta_id=pk, monto=monto_venta)

            return redirect('gestion:lista_ventas')
        except Exception as e:
            messages.error(request, f'Error inesperado al eliminar la venta: {str(e)}')

    # Calcular impacto antes de eliminar (para mostrar en confirmación)
    productos_afectados = []
    for detalle in venta.detalles.all():
        productos_afectados.append({
            'nombre': detalle.producto.nombre,
            'cantidad': detalle.cantidad,
            'stock_actual': detalle.producto.stock,
            'stock_futuro': detalle.producto.stock + detalle.cantidad
        })

    context = {
        'venta': venta,
        'objeto': venta,
        'tipo': 'venta',
        'monto_impacto': venta.total,
        'productos_afectados': productos_afectados,
        'cancel_url': reverse('gestion:lista_ventas')
    }
    return render(request, 'modules/ventas/confirmar_eliminacion_venta.html', context)


@login_required
def detalle_venta(request, pk):
    """Vista para ver el detalle completo de una venta."""
    venta = get_object_or_404(Venta, pk=pk)
    return render(request, 'modules/ventas/detalle_venta.html', {'venta': venta})


@login_required
def exportar_ventas(request):
    """Exporta ventas a Excel."""
    if not request.user.has_perm('gestion.export_venta'):
        messages.error(request, 'No tienes permiso para exportar ventas.')
        return redirect('gestion:lista_ventas')
    try:
        venta_resource = VentaResource()
        dataset = venta_resource.export()
        response = HttpResponse(dataset.xlsx, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="ventas_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        # Auditoría: registrar acción
        # LogVenta.objects.create(usuario=request.user, accion='exportar', descripcion='Exportación de ventas a Excel')
        return response
    except Exception as e:
        messages.error(request, f'Error inesperado al exportar ventas: {str(e)}')
        return redirect('gestion:lista_ventas')


# ==================== VISTAS ADICIONALES DE VENTAS ====================

@login_required
def crear_venta_con_materias(request):
    """
    Vista DESACTIVADA: Usar crear_venta en su lugar.
    
    Esta vista requiere:
    - Implementación completa de VentaConMateriasForm
    - Template 'gestion/venta_con_materias_form.html'
    - Lógica de validación de materias primas
    
    TODO: Completar implementación o eliminar esta vista.
    """
    LinoLogger.business_logger.warning(
        f"ACCESO A VISTA DESACTIVADA: crear_venta_con_materias por usuario {request.user.username}"
    )
    messages.info(
        request,
        '❌ Esta funcionalidad aún no está disponible. Por favor, usa el formulario estándar de ventas.'
    )
    return redirect('gestion:crear_venta')
