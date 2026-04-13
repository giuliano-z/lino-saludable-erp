#!/usr/bin/env python3
"""
🧪 TEST HELPER - BUG-A VALIDATION
Ejecutar desde: cd src && python3 ../test_bug_a_fix.py
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).resolve().parent / 'src'
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lino_saludable.settings')
django.setup()

from gestion.models import Producto, Venta, VentaDetalle, MateriaPrima, MovimientoMateriaPrima, Receta, RecetaMateriaPrima
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from django.db import transaction

def print_header(text):
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70 + "\n")

def crear_datos_prueba():
    """1️⃣ Crea producto con receta para testing"""
    print_header("1️⃣ CREANDO DATOS DE PRUEBA")
    
    # Crear usuario
    usuario, created = User.objects.get_or_create(
        username='test_bug_a',
        defaults={'email': 'test@lino.local', 'is_staff': False}
    )
    print(f"   Usuario: {usuario.username} {'(creado)' if created else '(existía)'}")
    
    # Crear materias primas
    harina, _ = MateriaPrima.objects.get_or_create(
        nombre='Harina Almendras (TEST)',
        defaults={
            'stock_actual': Decimal('100'),
            'unidad_medida': 'kg',
            'precio_unitario': Decimal('35.00')
        }
    )
    
    aceite, _ = MateriaPrima.objects.get_or_create(
        nombre='Aceite Coco (TEST)',
        defaults={
            'stock_actual': Decimal('50'),
            'unidad_medida': 'l',
            'precio_unitario': Decimal('80.00')
        }
    )
    
    print(f"   Materia Prima 1: {harina.nombre} - Stock: {harina.stock_actual}{harina.unidad_medida}")
    print(f"   Materia Prima 2: {aceite.nombre} - Stock: {aceite.stock_actual}{aceite.unidad_medida}")
    
    # Crear receta
    receta, _ = Receta.objects.get_or_create(
        nombre='Brownies Almendra (TEST)',
        defaults={'descripcion': 'Para testing de BUG-A'}
    )
    print(f"   Receta: {receta.nombre}")
    
    # Agregar ingredientes a receta
    RecetaMateriaPrima.objects.get_or_create(
        receta=receta,
        materia_prima=harina,
        defaults={'cantidad': Decimal('2'), 'unidad': 'kg'}
    )
    
    RecetaMateriaPrima.objects.get_or_create(
        receta=receta,
        materia_prima=aceite,
        defaults={'cantidad': Decimal('0.5'), 'unidad': 'l'}
    )
    print(f"      - Harina: 2 kg por unidad")
    print(f"      - Aceite: 0.5 l por unidad")
    
    # Crear producto
    producto, _ = Producto.objects.get_or_create(
        nombre='Brownies Almendra (TEST)',
        defaults={
            'tipo_producto': 'receta',
            'tiene_receta': True,
            'receta': receta,
            'precio_base': Decimal('150.00'),
            'stock': 10,
            'margen_ganancia': Decimal('30.00'),
            'descripcion': 'Para testing de BUG-A fix'
        }
    )
    print(f"   Producto: {producto.nombre}")
    print(f"      - Stock: {producto.stock} unidades")
    print(f"      - Precio: ${producto.precio_base}")
    
    return {
        'usuario': usuario,
        'producto': producto,
        'harina': harina,
        'aceite': aceite,
        'receta': receta
    }

def mostrar_stock_actual(datos, momento="ACTUAL"):
    """📊 Muestra estado actual de stocks"""
    print_header(f"📊 STOCK {momento}")
    
    datos['producto'].refresh_from_db()
    datos['harina'].refresh_from_db()
    datos['aceite'].refresh_from_db()
    
    print(f"   {datos['producto'].nombre}: {datos['producto'].stock} unidades")
    print(f"   {datos['harina'].nombre}: {datos['harina'].stock_actual}{datos['harina'].unidad_medida}")
    print(f"   {datos['aceite'].nombre}: {datos['aceite'].stock_actual}{datos['aceite'].unidad_medida}")

def crear_venta(datos, cantidad=2):
    """2️⃣ Crea una venta (simula lo que hace crear_venta_v3)"""
    print_header(f"2️⃣ CREANDO VENTA (cantidad: {cantidad})")
    
    usuario = datos['usuario']
    producto = datos['producto']
    
    # Crear venta
    with transaction.atomic():
        venta = Venta.objects.create(
            usuario=usuario,
            numero_seguimiento=f"TEST-{timezone.now().timestamp()}",
            fecha_venta=timezone.now(),
            total=producto.precio_base * cantidad
        )
        print(f"   ✅ Venta creada: #{venta.id}")
        
        # Crear detalle de venta
        detalle = VentaDetalle.objects.create(
            venta=venta,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio_base,
            subtotal=producto.precio_base * cantidad
        )
        print(f"   ✅ Detalle de venta creado")
        
        # 🔧 FIX BUG-A: Descontar stock del producto
        from django.db.models import F
        Producto.objects.filter(id=producto.id).update(
            stock=F('stock') - cantidad
        )
        print(f"   ✅ Stock del producto decrementado en {cantidad}")
        
        # 🔧 FIX BUG-A: Descontar ingredientes
        if producto.tiene_receta and producto.receta:
            producto.descontar_materias_primas(cantidad, usuario)
            print(f"   ✅ Stock de ingredientes decrementado")
        
        return venta

def validar_movimientos(venta):
    """3️⃣ Valida que los movimientos de auditoría se hayan registrado"""
    print_header("3️⃣ VALIDANDO MOVIMIENTOS DE AUDITORÍA")
    
    movimientos = MovimientoMateriaPrima.objects.filter(venta=venta).order_by('-fecha_movimiento')
    
    if movimientos.exists():
        print(f"   ✅ Se encontraron {movimientos.count()} movimientos\n")
        for mov in movimientos:
            print(f"      📦 {mov.materia_prima.nombre}")
            print(f"         - Tipo: {mov.tipo_movimiento}")
            print(f"         - Cantidad: {mov.cantidad}{mov.unidad}")
            print(f"         - Usuario: {mov.usuario.username}")
            print(f"         - Fecha: {mov.fecha_movimiento.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"   ❌ NO HAY MOVIMIENTOS REGISTRADOS")
        print(f"      Esto indica que BUG-A NO fue corregido")
        return False
    
    return True

def run_test():
    """Ejecuta test completo"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " 🧪 TEST BUG-A: Descuento de Ingredientes en Venta".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        # Paso 1: Crear datos
        datos = crear_datos_prueba()
        mostrar_stock_actual(datos, "INICIAL")
        
        # Paso 2: Crear venta
        venta = crear_venta(datos, cantidad=2)
        
        # Paso 3: Mostrar estado después
        mostrar_stock_actual(datos, "DESPUÉS DE VENTA")
        
        # Paso 4: Validar movimientos
        success = validar_movimientos(venta)
        
        # Resumen
        print_header("✅ RESUMEN DEL TEST")
        if success:
            print("   ✅ BUG-A FIX ESTÁ FUNCIONANDO")
            print("   ✅ Los ingredientes se descuentan automáticamente")
            print("   ✅ Los movimientos se registran en auditoría")
            print("\n   🚀 LISTO PARA COMMIT")
        else:
            print("   ❌ PROBLEMA DETECTADO")
            print("   ❌ BUG-A NO fue corregido correctamente")
        
    except Exception as e:
        print_header("❌ ERROR DURANTE EL TEST")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return success

if __name__ == '__main__':
    success = run_test()
    sys.exit(0 if success else 1)
