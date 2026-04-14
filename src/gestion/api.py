from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import MateriaPrima, Producto, Venta


@login_required
@require_GET
def producto_precio(request, pk):
    try:
        producto = Producto.objects.get(pk=pk)
        return JsonResponse({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'stock': producto.stock
        })
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)


@login_required
@require_GET
def api_productos(request):
    """API para sincronización de productos"""
    try:
        productos = Producto.objects.all()
        data = [
            {
                'id': p.id,
                'nombre': p.nombre,
                'precio': float(p.precio),
                'stock': p.stock,
                'descripcion': p.descripcion or '',
                'updated_at': p.fecha_creacion.isoformat(),
            }
            for p in productos
        ]
        return JsonResponse({
            'status': 'success',
            'data': data,
            'count': len(data),
            'last_updated': datetime.now().isoformat(),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_GET
def api_inventario(request):
    """API para sincronización de inventario/materias primas"""
    try:
        materias_primas = MateriaPrima.objects.all()
        data = [
            {
                'id': m.id,
                'nombre': m.nombre,
                'stock_actual': float(m.stock_actual),
                'stock_minimo': float(m.stock_minimo),
                'unidad_medida': m.unidad_medida,
                'costo_unitario': float(m.costo_unitario),
                'proveedor': m.proveedor or '',
                'updated_at': m.fecha_creacion.isoformat(),
            }
            for m in materias_primas
        ]
        return JsonResponse({
            'status': 'success',
            'data': data,
            'count': len(data),
            'last_updated': datetime.now().isoformat(),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_GET
def api_ventas(request):
    """API para sincronización de ventas — últimas 100"""
    try:
        ventas = Venta.objects.order_by('-fecha')[:100]
        data = [
            {
                'id': v.id,
                'fecha': v.fecha.isoformat(),
                'total': float(v.total),
                'cliente': v.cliente or '',
                'items_count': v.detalles.count(),
                'updated_at': v.fecha.isoformat(),
            }
            for v in ventas
        ]
        return JsonResponse({
            'status': 'success',
            'data': data,
            'count': len(data),
            'last_updated': datetime.now().isoformat(),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
