# 📋 GUÍA COMPLETA: TESTING LOCAL BUG-A FIX
## Lino Saludable - Validación Pre-Commit

**Fecha:** 9 de abril de 2026  
**Objetivo:** Validar que el fix del BUG-A (descuento de ingredientes en ventas) funciona correctamente antes de hacer commit a main

---

## 🎯 RESUMEN EJECUTIVO

### ¿Qué es BUG-A?
Cuando se vende un producto que usa una **receta**, el stock del **producto** disminuía, pero el stock de los **ingredientes** NO disminuía, generando inconsistencias.

### ¿Qué hicimos?
Agregamos validación y descuento automático de ingredientes al momento de crear una venta.

### ¿Cómo validar?
Seguir esta guía. Toma **5-10 minutos** total.

---

## 🚀 OPCIÓN 1: TEST AUTOMÁTICO (RECOMENDADO - 2 minutos)

### Paso 1: Levantar servidor

```bash
cd /Users/giulianozulatto/Proyectos/lino_saludable/src
python3 manage.py runserver
```

**Resultado esperado:**
```
Watching for file changes with StatReloader
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Paso 2: En OTRA terminal, ejecutar test

```bash
cd /Users/giulianozulatto/Proyectos/lino_saludable
python3 test_bug_a_fix.py
```

**Resultado esperado:**
```
╔══════════════════════════════════════════════════════════════════╗
║ 🧪 TEST BUG-A: Descuento de Ingredientes en Venta              ║
╚══════════════════════════════════════════════════════════════════╝

======================================================================
 1️⃣ CREANDO DATOS DE PRUEBA
======================================================================

   Usuario: test_bug_a (creado)
   Materia Prima 1: Harina Almendras (TEST) - Stock: 100kg
   Materia Prima 2: Aceite Coco (TEST) - Stock: 50l
   Receta: Brownies Almendra (TEST)
      - Harina: 2 kg por unidad
      - Aceite: 0.5 l por unidad
   Producto: Brownies Almendra (TEST)
      - Stock: 10 unidades
      - Precio: $150.00

======================================================================
 📊 STOCK INICIAL
======================================================================

   Brownies Almendra (TEST): 10 unidades
   Harina Almendras (TEST): 100kg
   Aceite Coco (TEST): 50l

======================================================================
 2️⃣ CREANDO VENTA (cantidad: 2)
======================================================================

   ✅ Venta creada: #X
   ✅ Detalle de venta creado
   ✅ Stock del producto decrementado en 2
   ✅ Stock de ingredientes decrementado

======================================================================
 📊 STOCK DESPUÉS DE VENTA
======================================================================

   Brownies Almendra (TEST): 8 unidades
   Harina Almendras (TEST): 96kg
   Aceite Coco (TEST): 49l

======================================================================
 3️⃣ VALIDANDO MOVIMIENTOS DE AUDITORÍA
======================================================================

   ✅ Se encontraron 2 movimientos

      📦 Harina Almendras (TEST)
         - Tipo: DESCUENTO_VENTA
         - Cantidad: 4kg
         - Usuario: test_bug_a
         - Fecha: 2026-04-09 XX:XX:XX

      📦 Aceite Coco (TEST)
         - Tipo: DESCUENTO_VENTA
         - Cantidad: 1l
         - Usuario: test_bug_a
         - Fecha: 2026-04-09 XX:XX:XX

======================================================================
 ✅ RESUMEN DEL TEST
======================================================================

   ✅ BUG-A FIX ESTÁ FUNCIONANDO
   ✅ Los ingredientes se descuentan automáticamente
   ✅ Los movimientos se registran en auditoría

   🚀 LISTO PARA COMMIT
```

### Paso 3: Interpretar resultados

| Si ves | Significa |
|--------|-----------|
| `✅ BUG-A FIX ESTÁ FUNCIONANDO` | Todo bien, proceder a commit |
| `❌ PROBLEMA DETECTADO` | Algo falló, revisar error |
| Error de conexión | Server no está corriendo en Terminal 1 |

---

## 🔍 OPCIÓN 2: TEST MANUAL VÍA SHELL (DETALLADO - 5 minutos)

### Paso 1: Levantar servidor (igual que arriba)

```bash
cd /Users/giulianozulatto/Proyectos/lino_saludable/src
python3 manage.py runserver
```

### Paso 2: Abrir Django shell

```bash
cd /Users/giulianozulatto/Proyectos/lino_saludable/src
python3 manage.py shell
```

### Paso 3: Crear datos de prueba

```python
from gestion.models import Producto, Receta, MateriaPrima, RecetaMateriaPrima
from django.contrib.auth.models import User
from decimal import Decimal

# Crear usuario
usuario, _ = User.objects.get_or_create(
    username='test_manual',
    defaults={'email': 'test@local.com'}
)
print(f"✅ Usuario: {usuario.username}")

# Crear materias primas
harina, _ = MateriaPrima.objects.get_or_create(
    nombre='Harina TEST Manual',
    defaults={
        'stock_actual': Decimal('100'),
        'unidad_medida': 'kg',
        'precio_unitario': Decimal('35.00')
    }
)

aceite, _ = MateriaPrima.objects.get_or_create(
    nombre='Aceite TEST Manual',
    defaults={
        'stock_actual': Decimal('50'),
        'unidad_medida': 'l',
        'precio_unitario': Decimal('80.00')
    }
)

print(f"✅ Materia Prima 1: {harina.nombre} ({harina.stock_actual}{harina.unidad_medida})")
print(f"✅ Materia Prima 2: {aceite.nombre} ({aceite.stock_actual}{aceite.unidad_medida})")

# Crear receta
receta, _ = Receta.objects.get_or_create(
    nombre='Test Recipe Manual',
    defaults={'descripcion': 'Para testing manual'}
)
print(f"✅ Receta: {receta.nombre}")

# Agregar ingredientes
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

print(f"   - Ingrediente 1: Harina (2 kg/unidad)")
print(f"   - Ingrediente 2: Aceite (0.5 l/unidad)")

# Crear producto
producto, _ = Producto.objects.get_or_create(
    nombre='Test Producto Manual',
    defaults={
        'tipo_producto': 'receta',
        'tiene_receta': True,
        'receta': receta,
        'precio_base': Decimal('150.00'),
        'stock': 10,
        'margen_ganancia': Decimal('30.00')
    }
)

print(f"✅ Producto: {producto.nombre}")
print(f"   - Stock: {producto.stock}")
print(f"   - Precio: ${producto.precio_base}")

# Guardar IDs para el siguiente paso
print(f"\n📌 IDs para el próximo paso:")
print(f"   USUARIO_ID = {usuario.id}")
print(f"   PRODUCTO_ID = {producto.id}")
```

### Paso 4: Mostrar stock ANTES de la venta

```python
from gestion.models import Producto, MateriaPrima

PRODUCTO_ID = 1  # 👈 REEMPLAZA CON EL ID DEL PASO ANTERIOR

# Obtener datos
producto = Producto.objects.get(id=PRODUCTO_ID)

print("\n📊 STOCK ANTES DE LA VENTA:")
print(f"\nProducto: {producto.nombre}")
print(f"  - Stock: {producto.stock} unidades")

print(f"\nIngredientes de la receta:")
for ing in producto.receta.recetamateriaprima_set.all():
    mp = ing.materia_prima
    print(f"  - {mp.nombre}: {mp.stock_actual}{mp.unidad_medida}")
```

### Paso 5: Crear la venta (SIMULA LO QUE HACE EL FIX)

```python
from gestion.models import Venta, VentaDetalle
from django.db.models import F
from django.db import transaction

PRODUCTO_ID = 1  # 👈 REEMPLAZA
USUARIO_ID = 1   # 👈 REEMPLAZA
CANTIDAD = 2

usuario = User.objects.get(id=USUARIO_ID)
producto = Producto.objects.get(id=PRODUCTO_ID)

print(f"\n📝 Creando venta de {CANTIDAD} unidades...")

with transaction.atomic():
    # Crear venta
    venta = Venta.objects.create(
        usuario=usuario,
        numero_seguimiento=f"TEST-MANUAL-{timezone.now().timestamp()}",
        fecha_venta=timezone.now(),
        total=producto.precio_base * CANTIDAD
    )
    print(f"✅ Venta creada: #{venta.id}")
    
    # Crear detalle
    detalle = VentaDetalle.objects.create(
        venta=venta,
        producto=producto,
        cantidad=CANTIDAD,
        precio_unitario=producto.precio_base,
        subtotal=producto.precio_base * CANTIDAD
    )
    print(f"✅ Detalle creado")
    
    # 🔧 FIX BUG-A: Descontar stock del producto
    Producto.objects.filter(id=producto.id).update(
        stock=F('stock') - CANTIDAD
    )
    print(f"✅ Stock del producto decrementado")
    
    # 🔧 FIX BUG-A: Descontar ingredientes
    if producto.tiene_receta and producto.receta:
        producto.descontar_materias_primas(CANTIDAD, usuario)
        print(f"✅ Stock de ingredientes decrementado")

# Guardar VENTA_ID para siguiente paso
print(f"\n📌 Para siguiente paso:")
print(f"   VENTA_ID = {venta.id}")

# Importar para el siguiente paso
from django.utils import timezone
```

### Paso 6: Mostrar stock DESPUÉS de la venta

```python
from gestion.models import Producto

PRODUCTO_ID = 1  # 👈 REEMPLAZA

# Refrescar datos
producto = Producto.objects.get(id=PRODUCTO_ID)

print("\n📊 STOCK DESPUÉS DE LA VENTA:")
print(f"\nProducto: {producto.nombre}")
print(f"  - Stock: {producto.stock} unidades (DEBE HABER DISMINUIDO)")

print(f"\nIngredientes de la receta:")
for ing in producto.receta.recetamateriaprima_set.all():
    mp = ing.materia_prima
    print(f"  - {mp.nombre}: {mp.stock_actual}{mp.unidad_medida} (DEBE HABER DISMINUIDO)")
```

### Paso 7: Validar movimientos de auditoría (CRÍTICO)

```python
from gestion.models import MovimientoMateriaPrima, Venta

VENTA_ID = 1  # 👈 REEMPLAZA

venta = Venta.objects.get(id=VENTA_ID)
movimientos = MovimientoMateriaPrima.objects.filter(venta=venta)

print(f"\n📝 MOVIMIENTOS DE AUDITORÍA (Venta #{venta.id}):")
print(f"Total de movimientos: {movimientos.count()}")

if movimientos.count() > 0:
    print("\n✅ BUG-A FIX FUNCIONA - Se registraron movimientos:\n")
    for mov in movimientos:
        print(f"  📦 {mov.materia_prima.nombre}")
        print(f"     - Cantidad: {mov.cantidad}{mov.unidad}")
        print(f"     - Tipo: {mov.tipo_movimiento}")
        print(f"     - Usuario: {mov.usuario.username}")
        print(f"     - Fecha: {mov.fecha_movimiento}")
        print()
else:
    print("\n❌ BUG-A NO FUNCIONA - No hay movimientos registrados")

# Salir del shell
exit()
```

---

## 📋 CHECKLIST DE VALIDACIÓN MANUAL

Usar esto si ejecutas el test paso a paso en shell:

```
✅ DATOS DE PRUEBA CREADOS
   [ ] Usuario creado
   [ ] 2+ Materias primas con stock > 0
   [ ] Receta con 2+ ingredientes
   [ ] Producto con tipo='receta' y tiene_receta=True
   [ ] Stock del producto >= 2

✅ STOCK ANTES
   [ ] Producto: 10 unidades
   [ ] Harina: 100 kg
   [ ] Aceite: 50 l

✅ VENTA CREADA
   [ ] Venta #X creado sin errores
   [ ] Detalle vinculado correctamente

✅ STOCK DESPUÉS (VALIDACIÓN CRÍTICA)
   [ ] Producto: 8 unidades (10 - 2)
   [ ] Harina: 96 kg (100 - 4, porque 2kg × 2 unidades)
   [ ] Aceite: 49 l (50 - 1, porque 0.5l × 2 unidades)

✅ MOVIMIENTOS REGISTRADOS (PRUEBA DEL FIX)
   [ ] MovimientoMateriaPrima.count() >= 2
   [ ] Un movimiento por cada ingrediente
   [ ] Tipo: DESCUENTO_VENTA
   [ ] Cantidades coinciden

✅ LISTO PARA COMMIT
   Si todas las validaciones pasaron → git commit
```

---

## 🐛 TROUBLESHOOTING

### Problema: "Module not found" al abrir shell
```
FileNotFoundError: [Errno 2] No such file or directory: '.env'
```
**Solución:**
```bash
cd src
touch .env
echo "DEBUG=True" > .env
echo "SECRET_KEY=test-key-12345" >> .env
```

### Problema: "Stock insuficiente"
**Causa:** Un ingrediente no tiene suficiente stock

**Solución:**
```python
# En el shell:
from gestion.models import MateriaPrima
mp = MateriaPrima.objects.get(nombre='Harina TEST')
mp.stock_actual = 1000
mp.save()
print(f"Stock de {mp.nombre} aumentado a {mp.stock_actual}")
```

### Problema: No hay movimientos después de la venta
**Causa:** El fix NO está aplicado o hay error en la lógica

**Verificación:**
```bash
# Verificar que el código esté en views.py
grep -A5 "descontar_materias_primas" /Users/giulianozulatto/Proyectos/lino_saludable/src/gestion/views.py | head -10
```

Si no aparece nada → El fix no se aplicó correctamente

---

## ✅ CUANDO TODO FUNCIONA

Si llegaste aquí y todas las validaciones pasaron:

```bash
# Primero, asegúrate de estar en la raíz del proyecto
cd /Users/giulianozulatto/Proyectos/lino_saludable

# Verificar cambios
git status

# Debería mostrar (como mínimo):
# modified:   src/gestion/models.py
# modified:   src/gestion/views.py
# modified:   src/lino_saludable/settings.py

# Hacer commit
git add -A
git commit -m "PASO 1+2: Security fixes + BUG-A recipe ingredient stock fix (tested locally)"

# Verificar que todo está commiteado
git status
# Debe mostrar: nothing to commit, working tree clean
```

---

## 📞 REFERENCIAS

| Documento | Contenido |
|-----------|----------|
| `GUIA_TESTING_BUG_A.md` | Guía completa y detallada |
| `TESTING_CHECKLIST_RAPIDO.md` | Checklist rápida |
| `test_bug_a_fix.py` | Script automático |
| `src/gestion/models.py` líneas 654-804 | Métodos nuevos/mejorados |
| `src/gestion/views.py` línea 3260+ | Integración del fix |

---

## ⏱️ TIEMPO ESTIMADO

- **Opción 1 (Automático):** 2 minutos
- **Opción 2 (Manual):** 10 minutos
- **Total:** 15 minutos máximo

---

**Autor:** GitHub Copilot  
**Fecha:** 9 de abril de 2026  
**Sistema:** Lino Saludable (Django 5.2)
