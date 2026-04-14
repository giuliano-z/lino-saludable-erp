# ==================== VISTAS DE COMPRAS ====================
"""
Módulo de vistas para la gestión de compras de materias primas.
Funcionalidades:
- CRUD de compras con actualización automática de stock y costos
- Soporte para compras legacy (1 producto) y modernas (múltiples productos)
- FIFO con lotes de materias primas
- Logging robusto para transacciones financieras
- Reversión total de compras con recalculo de costos
"""

# ==================== IMPORTS ====================
import traceback
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import CompraForm
from .logging_system import LinoLogger, get_request_info
from .models import (
    Compra,
    LoteMateriaPrima,
    MateriaPrima,
    MovimientoMateriaPrima,
)

# ==================== VISTAS DE COMPRAS ====================

@login_required
def lista_compras(request):
    """Vista para listar compras con KPIs LINO V3."""
    from django.core.paginator import Paginator

    from gestion.utils.kpi_builder import prepare_compras_kpis

    try:
        compras = Compra.objects.all().order_by('-fecha_compra')

        # Filtros opcionales
        materia_prima_id = request.GET.get('materia_prima')
        proveedor = request.GET.get('proveedor')
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        q = request.GET.get('q')

        if materia_prima_id:
            compras = compras.filter(materia_prima_id=materia_prima_id)
        if proveedor:
            compras = compras.filter(proveedor__icontains=proveedor)
        if q:
            compras = compras.filter(
                Q(proveedor__icontains=q) |
                Q(materia_prima__nombre__icontains=q)
            )
        if fecha_inicio:
            compras = compras.filter(fecha_compra__gte=fecha_inicio)
        if fecha_fin:
            compras = compras.filter(fecha_compra__lte=fecha_fin)

        # Compras del mes para KPIs
        compras_mes = Compra.objects.filter(
            fecha_compra__month=timezone.now().month,
            fecha_compra__year=timezone.now().year
        )

        # Preparar KPIs
        kpis = prepare_compras_kpis(compras_mes)

        # Paginación
        paginator = Paginator(compras, 25)
        page_number = request.GET.get('page', 1)
        compras_paginadas = paginator.get_page(page_number)

        materias_primas = MateriaPrima.objects.all()

        context = {
            'compras': compras_paginadas,
            'kpis': kpis,
            'materias_primas': materias_primas,
            'materia_prima_id': materia_prima_id,
            'proveedor': proveedor,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'q': q,
            'title': 'Compras',
            'subtitle': 'Gestión de compras y proveedores',
            'icon': 'truck',
            'create_url': reverse('gestion:crear_compra'),
        }
        return render(request, 'modules/compras/lista.html', context)
    except Exception as e:
        messages.error(request, f'Error inesperado al listar compras: {str(e)}')
        return redirect('gestion:panel_control')


@login_required
def crear_compra(request):
    """
    Vista CRÍTICA: Crear compra de materia prima con logging y validaciones.
    Impacta costos, stock y cálculo automático de precios.
    """
    request_info = get_request_info(request)
    LinoLogger.log_accion_admin(request.user, "INTENTO_CREAR_COMPRA", "Compra", 0)

    if request.method == 'POST':
        form = CompraForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Obtener datos del formulario antes de guardar
                    materia_prima = form.cleaned_data['materia_prima']
                    cantidad = form.cleaned_data['cantidad_mayoreo']
                    precio_total = form.cleaned_data['precio_mayoreo']
                    proveedor = form.cleaned_data['proveedor']

                    # Validaciones adicionales
                    if cantidad <= 0:
                        LinoLogger.log_error_critico(
                            "compras", "crear_compra",
                            f"Cantidad inválida: {cantidad}",
                            {"materia_prima": materia_prima.nombre, "usuario": request.user.username}
                        )
                        messages.error(request, 'La cantidad debe ser mayor a 0.')
                        return render(request, 'modules/compras/compras/crear.html', {'form': form})

                    if precio_total <= 0:
                        LinoLogger.log_error_critico(
                            "compras", "crear_compra",
                            f"Precio inválido: {precio_total}",
                            {"materia_prima": materia_prima.nombre, "usuario": request.user.username}
                        )
                        messages.error(request, 'El precio debe ser mayor a 0.')
                        return render(request, 'modules/compras/compras/crear.html', {'form': form})

                    # Guardar información previa para logging
                    stock_anterior = materia_prima.stock_actual
                    costo_anterior = materia_prima.costo_unitario

                    # Guardar la compra (esto disparará la lógica en el modelo)
                    compra = form.save()

                    # Recargar la materia prima para obtener valores actualizados
                    materia_prima.refresh_from_db()

                    # Log de la compra registrada
                    LinoLogger.log_compra_registrada(
                        materia_prima.nombre, cantidad, precio_total, proveedor, request.user
                    )

                    # Log del cambio de stock
                    LinoLogger.log_stock_actualizado(
                        f"MP: {materia_prima.nombre}", stock_anterior, materia_prima.stock_actual,
                        f"Compra ID: {compra.id}", request.user
                    )

                    # Log del cambio de costo si cambió significativamente
                    if abs(costo_anterior - materia_prima.costo_unitario) > Decimal('0.01'):
                        LinoLogger.log_precio_actualizado(
                            f"MP: {materia_prima.nombre}", costo_anterior,
                            materia_prima.costo_unitario, request.user
                        )

                    # TODO: Implementar integración con sistema de caja/balance
                    # Ajustar caja/balance: disminuir caja por el monto de la compra
                    # from .models import Caja
                    # caja = Caja.objects.first()
                    # if caja:
                    #     caja.saldo -= compra.precio_mayoreo
                    #     caja.save()

                    messages.success(
                        request,
                        f'✅ Compra registrada correctamente. '
                        f'Stock actualizado: {materia_prima.nombre} '
                        f'({stock_anterior} → {materia_prima.stock_actual} {materia_prima.get_unidad_medida_display()})'
                    )
                    return redirect('gestion:lista_compras')

            except Exception as e:
                # Log detallado del error
                error_trace = traceback.format_exc()
                LinoLogger.log_error_critico(
                    "compras", "crear_compra",
                    f"Excepción no controlada: {str(e)}",
                    {"traceback": error_trace, "request_info": request_info}
                )
                messages.error(request, f'❌ Error crítico al registrar la compra. Contacte al administrador. Error: {str(e)}')
        else:
            # Log de errores de formulario
            form_errors = form.errors.as_json() if form.errors else "Sin errores"
            LinoLogger.log_error_critico(
                "compras", "crear_compra",
                f"Formulario inválido: {form_errors}",
                {"usuario": request.user.username}
            )
            messages.error(request, 'Error al registrar la compra. Verifica los datos.')
    else:
        # GET request
        form = CompraForm()
        LinoLogger.business_logger.info(f"FORMULARIO_COMPRA_CARGADO - Usuario: {request.user.username}")

    return render(request, 'modules/compras/compras/crear.html', {'form': form})


@login_required
def detalle_compra(request, pk):
    """Vista de detalle de una compra (compatible con legacy y nueva versión)."""
    compra = get_object_or_404(Compra, pk=pk)

    # Detectar si es compra legacy o nueva con detalles
    es_legacy = compra.es_compra_legacy()
    detalles = compra.detalles.all() if not es_legacy else None

    context = {
        'compra': compra,
        'es_legacy': es_legacy,
        'detalles': detalles,
    }

    return render(request, 'modules/compras/compras/detalle.html', context)


@login_required
def eliminar_compra(request, pk):
    """
    Vista para eliminar una compra completamente (hard delete con reversión total).
    Compatible con compras legacy (1 producto) y nuevas (múltiples productos vía CompraDetalle).
    Revierte stock, recalcula costos unitarios y mantiene FIFO.
    """
    compra = get_object_or_404(Compra, pk=pk)

    if request.method == 'POST':
        if request.POST.get('confirmar'):
            try:
                with transaction.atomic():
                    es_legacy = compra.es_compra_legacy()

                    if es_legacy:
                        # LEGACY: Compra de 1 solo producto (campos directos)
                        materia_prima = compra.materia_prima
                        stock_anterior = materia_prima.stock_actual
                        costo_anterior = materia_prima.costo_unitario
                        cantidad_compra = float(compra.cantidad_mayoreo)
                        costo_compra = float(compra.precio_unitario_mayoreo)

                        # 1. Revertir el stock
                        nuevo_stock = stock_anterior - compra.cantidad_mayoreo
                        materia_prima.stock_actual = max(Decimal('0.00'), nuevo_stock)

                        # 2. Recalcular costo unitario (revertir promedio ponderado)
                        if nuevo_stock > 0:
                            valor_total_actual = float(stock_anterior) * float(costo_anterior)
                            valor_compra = cantidad_compra * costo_compra
                            valor_sin_compra = valor_total_actual - valor_compra
                            nuevo_costo_unitario = valor_sin_compra / float(nuevo_stock)
                            materia_prima.costo_unitario = Decimal(str(max(0, nuevo_costo_unitario)))
                        else:
                            materia_prima.costo_unitario = Decimal('0.00')

                        materia_prima.save()

                        # 3. Eliminar lotes FIFO asociados
                        lotes_eliminados = LoteMateriaPrima.objects.filter(
                            materia_prima=materia_prima,
                            fecha_entrada=compra.fecha_compra,
                            precio_unitario=compra.precio_unitario_mayoreo
                        ).delete()

                        # 4. Registrar movimiento
                        MovimientoMateriaPrima.objects.create(
                            materia_prima=materia_prima,
                            tipo_movimiento='ajuste',
                            cantidad=compra.cantidad_mayoreo,
                            cantidad_anterior=stock_anterior,
                            cantidad_nueva=materia_prima.stock_actual,
                            motivo=f'Eliminación de compra errónea #{compra.pk} - Proveedor: {compra.proveedor}',
                            usuario=request.user
                        )

                        nombre_materia = materia_prima.nombre
                        cantidad_revertida = compra.cantidad_mayoreo
                        unidad = materia_prima.get_unidad_medida_display()

                        # 5. HARD DELETE
                        compra.delete()

                        messages.success(
                            request,
                            f'✅ Compra eliminada completamente. '
                            f'Stock revertido: -{cantidad_revertida} {unidad}. '
                            f'Nuevo stock de {nombre_materia}: {materia_prima.stock_actual} {unidad}.'
                        )
                    else:
                        # NUEVA: Compra con múltiples productos (CompraDetalle)
                        detalles = compra.detalles.all()
                        items_count = detalles.count()
                        total_revertido = compra.total

                        # Revertir cada detalle
                        for detalle in detalles:
                            materia_prima = detalle.materia_prima
                            stock_anterior = materia_prima.stock_actual
                            costo_anterior = materia_prima.costo_unitario
                            cantidad_compra = float(detalle.cantidad)
                            costo_compra = float(detalle.precio_unitario)

                            # 1. Revertir stock
                            nuevo_stock = stock_anterior - detalle.cantidad
                            materia_prima.stock_actual = max(Decimal('0.00'), nuevo_stock)

                            # 2. Recalcular costo unitario
                            if nuevo_stock > 0:
                                valor_total_actual = float(stock_anterior) * float(costo_anterior)
                                valor_compra = cantidad_compra * costo_compra
                                valor_sin_compra = valor_total_actual - valor_compra
                                nuevo_costo_unitario = valor_sin_compra / float(nuevo_stock)
                                materia_prima.costo_unitario = Decimal(str(max(0, nuevo_costo_unitario)))
                            else:
                                materia_prima.costo_unitario = Decimal('0.00')

                            materia_prima.save()

                            # 3. Eliminar lotes FIFO de este detalle
                            LoteMateriaPrima.objects.filter(
                                materia_prima=materia_prima,
                                fecha_entrada=compra.fecha_compra,
                                precio_unitario=detalle.precio_unitario,
                                cantidad_restante__lte=detalle.cantidad  # Aproximación
                            ).delete()

                            # 4. Registrar movimiento
                            MovimientoMateriaPrima.objects.create(
                                materia_prima=materia_prima,
                                tipo_movimiento='ajuste',
                                cantidad=detalle.cantidad,
                                cantidad_anterior=stock_anterior,
                                cantidad_nueva=materia_prima.stock_actual,
                                motivo=f'Eliminación de compra multi-producto #{compra.pk} - Proveedor: {compra.proveedor}',
                                usuario=request.user
                            )

                        # 5. HARD DELETE (elimina compra y detalles en cascada)
                        compra.delete()

                        messages.success(
                            request,
                            f'✅ Compra multi-producto eliminada completamente. '
                            f'{items_count} producto(s) revertido(s). '
                            f'Total revertido: ${total_revertido}'
                        )

                    return redirect('gestion:lista_compras')

            except Exception as e:
                messages.error(request, f'❌ Error al eliminar la compra: {str(e)}')
                return redirect('gestion:lista_compras')

    # GET: Mostrar confirmación
    es_legacy = compra.es_compra_legacy()
    detalles = compra.detalles.all() if not es_legacy else None

    context = {
        'compra': compra,
        'es_legacy': es_legacy,
        'detalles': detalles,
    }

    return render(request, 'modules/compras/confirmar_eliminacion_compra.html', context)


# ==================== API ENDPOINTS ====================

@login_required
@require_http_methods(["GET"])
def api_costo_receta(request, pk):
    """API endpoint para obtener el costo total de una receta."""
    from .models import Receta

    try:
        receta = get_object_or_404(Receta, pk=pk)
        costo_total = receta.costo_total()

        # También devolver información detallada de ingredientes para debug
        ingredientes = []
        for ingrediente in receta.recetamateriaprima_set.all():
            ingredientes.append({
                'materia_prima': ingrediente.materia_prima.nombre,
                'cantidad': float(ingrediente.cantidad),
                'costo_unitario': float(ingrediente.materia_prima.costo_unitario),
                'costo_total': float(ingrediente.costo_ingrediente())
            })

        return JsonResponse({
            'success': True,
            'costo_total': float(costo_total),
            'ingredientes': ingredientes
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
