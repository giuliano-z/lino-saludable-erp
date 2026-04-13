#!/usr/bin/env python
"""
Script para contar ventas con productos que tienen receta.
Útil para diagnosticar el bug de ingredientes no descontados.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lino_saludable.settings')
django.setup()

from gestion.models import Venta, VentaDetalle, Producto
from django.db.models import Q, Count

# Contar ventas que incluyen productos con receta
ventas_con_receta = Venta.objects.filter(
    detalles__producto__tiene_receta=True,
    eliminada=False  # Solo ventas activas
).distinct().count()

print(f"\n📊 DIAGNÓSTICO: Ventas con Productos que tienen Receta")
print(f"{'='*60}")
print(f"Total de ventas ACTIVAS con productos que usan receta: {ventas_con_receta}")

# Desglose por cantidad de productos con receta por venta
detalle_por_venta = Venta.objects.filter(
    detalles__producto__tiene_receta=True,
    eliminada=False
).annotate(
    productos_con_receta=Count('detalles__producto', filter=Q(detalles__producto__tiene_receta=True))
).values('productos_con_receta').annotate(count=Count('id'))

print(f"\nDesglose:")
for item in detalle_por_venta:
    print(f"  - {item['count']} venta(s) con {item['productos_con_receta']} producto(s) con receta")

# Mostrar las últimas 5 ventas como ejemplo
print(f"\nÚltimas 5 ventas con productos con receta:")
print(f"{'-'*60}")
ultimas = Venta.objects.filter(
    detalles__producto__tiene_receta=True,
    eliminada=False
).distinct().order_by('-fecha')[:5]

for venta in ultimas:
    productos_receta = venta.detalles.filter(producto__tiene_receta=True)
    print(f"  Venta #{venta.id} ({venta.fecha.strftime('%Y-%m-%d %H:%M')})")
    for detalle in productos_receta:
        print(f"    - {detalle.producto.nombre} (x{detalle.cantidad})")
        if detalle.producto.receta:
            print(f"      Receta: {detalle.producto.receta.nombre}")
        else:
            print(f"      ⚠️ ADVERTENCIA: tiene_receta=True pero no tiene receta asignada")

print(f"\n{'='*60}\n")
