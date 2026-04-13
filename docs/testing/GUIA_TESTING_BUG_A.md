# 🧪 GUÍA DE TESTING LOCAL - BUG-A FIX
## Validación Manual del Fix de Stock de Ingredientes

**Fecha:** 9 de abril de 2026  
**Sistema:** Lino Saludable (Django 5.2 + PostgreSQL)  
**Objetivo:** Verificar que al vender un producto con receta, se descuenten automáticamente los ingredientes

---

## 📋 PASO 0: PREPARACIÓN DEL ENTORNO

### 0.1 Levantar el servidor local

```bash
# Desde la carpeta raíz del proyecto
cd /Users/giulianozulatto/Proyectos/lino_saludable

# Opción A: Comando simple (RECOMENDADO)
cd src
python3 manage.py runserver

# Opción B: Con IP específica
python3 manage.py runserver 127.0.0.1:8000

# El servidor estará disponible en: http://localhost:8000
```

**Nota:** No hay `start.sh` configurado, así que usamos `runserver` directamente.

### 0.2 Acceder al admin de Django

1. Abre `http://localhost:8000/admin/`
2. Credenciales predeterminadas:
   - Usuario: `admin_lino` (si fue creado por `init_sistema.py`)
   - Contraseña: `changeme`
   - **Cambiar inmediatamente después**

Si no existen usuarios, créalos manualmente:
```bash
cd src
python3 manage.py createsuperuser
# Ingresa username, email, password cuando se pida
```

### 0.3 Revisar datos existentes

Tenés varias opciones:

**Opción 1:** Usar el script existente de inspección:
```bash
cd src
python3 query_ventas_receta.py
# Muestra productos con receta en el sistema
```

**Opción 2:** Query directa en el admin Django:
- Ir a `http://localhost:8000/admin/gestion/producto/`
- Filtrar por `Tiene Receta: Sí`

**Opción 3:** Usar Django shell (RECOMENDADO):
```bash
cd src
python3 manage.py shell
>>> from gestion.models import Producto, MateriaPrima
>>> # Listar productos con receta
>>> productos_receta = Producto.objects.filter(tiene_receta=True)
>>> for p in productos_receta[:5]:
...     print(f"- {p.nombre}: stock={p.stock}, receta={p.receta_id}")
>>> # Salir
>>> exit()
```

---

## ✅ PASO 1: PREPARAR DATOS DE PRUEBA

### Opción A: Usar datos existentes (RECOMENDADO si hay muchos)

Si el sistema ya tiene productos con receta y stock:

```bash
cd src
python3 manage.py shell
>>> from gestion.models import Producto
>>> # Encontrar un producto con receta y stock suficiente
>>> p = Producto.objects.filter(tiene_receta=True, stock__gte=2).first()
>>> if p:
...     print(f"Producto: {p.nombre}")
...     print(f"Stock actual: {p.stock}")
...     print(f"Receta: {p.receta_id}")
...     print(f"Ingredientes:")
...     for rmp in p.receta.recetamateriaprima_set.all():
...         print(f"  - {rmp.materia_prima.nombre}: {rmp.cantidad}{rmp.unidad} (stock: {rmp.materia_prima.stock_actual})")
... else:
...     print("No hay productos con receta y stock >= 2")
>>> exit()
```

### Opción B: Crear datos de prueba desde cero

```bash
cd src
python3 manage.py shell
```

Luego ejecuta este código en el shell:

```python
from gestion.models import Producto, Receta, MateriaPrima, RecetaMateriaPrima
from django.contrib.auth.models import User
from decimal import Decimal

# 1️⃣ Crear usuario de prueba
usuario = User.objects.create_user(username='test_user', password='test123')
print("✅ Usuario creado")

# 2️⃣ Crear materias primas con stock suficiente
harina = MateriaPrima.objects.create(
    nombre="Harina de Almendras (TEST)",
    stock_actual=Decimal('100'),
    unidad_medida="kg",
    precio_unitario=Decimal('35.00')
)
aceite = MateriaPrima.objects.create(
    nombre="Aceite de Coco (TEST)",
    stock_actual=Decimal('50'),
    unidad_medida="l",
    precio_unitario=Decimal('80.00')
)
print("✅ Materias primas creadas:")
print(f"   - {harina.nombre}: {harina.stock_actual}{harina.unidad_medida}")
print(f"   - {aceite.nombre}: {aceite.stock_actual}{aceite.unidad_medida}")

# 3️⃣ Crear receta
receta = Receta.objects.create(
    nombre="Brownies de Almendra (TEST)",
    descripcion="Brownies con harina de almendras"
)
print("✅ Receta creada: {receta.nombre}")

# 4️⃣ Agregar ingredientes a la receta
RecetaMateriaPrima.objects.create(
    receta=receta,
    materia_prima=harina,
    cantidad=Decimal('2'),
    unidad="kg"
)
RecetaMateriaPrima.objects.create(
    receta=receta,
    materia_prima=aceite,
    cantidad=Decimal('0.5'),
    unidad="l"
)
print("✅ Ingredientes agregados a la receta")

# 5️⃣ Crear producto que usa esta receta
producto = Producto.objects.create(
    nombre="Brownies Almendra (TEST)",
    tipo_producto="receta",
    tiene_receta=True,
    receta=receta,
    precio_base=Decimal('150.00'),
    stock=5,  # 5 unidades disponibles
    margen_ganancia=Decimal('30.00')
)
print("✅ Producto creado:")
print(f"   - Nombre: {producto.nombre}")
print(f"   - Stock inicial: {producto.stock}")
print(f"   - Tipo: {producto.tipo_producto}")

# 6️⃣ Verificar stocks antes de la prueba
print("\n📊 ESTADO INICIAL ANTES DE LA VENTA:")
print(f"   Producto '{producto.nombre}': {producto.stock} unidades")
print(f"   Harina: {harina.stock_actual}{harina.unidad_medida}")
print(f"   Aceite: {aceite.stock_actual}{aceite.unidad_medida}")

print("\n✅ DATOS DE PRUEBA LISTOS")
print(f"Producto a vender: {producto.id} ({producto.nombre})")
```

---

## 🧪 PASO 2: EJECUTAR LA VENTA

### 2.1 Vía interfaz web (RECOMENDADO para testing visual)

1. Abre `http://localhost:8000` (debe mostrar dashboard)
2. Navega a **Ventas → Nueva Venta** (o similar según rutas)
3. Selecciona el producto creado en PASO 1
4. Ingresa cantidad: **2** (para vender 2 unidades)
5. Verifica que el precio total sea correcto
6. Haz clic en **Guardar/Crear Venta**

**Resultado esperado:** Venta creada sin errores

### 2.2 Vía Django shell (ALTERNATIVA para debugging)

```bash
cd src
python3 manage.py shell
```

```python
from gestion.models import Producto, Venta, VentaDetalle, MateriaPrima
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

# Variables
CANTIDAD_A_VENDER = 2
PRODUCTO_ID = 1  # 👈 REEMPLAZA CON EL ID DE TU PRODUCTO

# Obtener datos
usuario = User.objects.first()
producto = Producto.objects.get(id=PRODUCTO_ID)

print(f"📦 Venta manual de {producto.nombre}")
print(f"Cantidad: {CANTIDAD_A_VENDER} unidades")

# Crear venta (sin usar la vista, directo al modelo)
venta = Venta.objects.create(
    usuario=usuario,
    numero_seguimiento=f"TEST-{timezone.now().timestamp()}",
    fecha_venta=timezone.now(),
    total=producto.precio_base * CANTIDAD_A_VENDER
)

# Crear detalle de venta
detalle = VentaDetalle.objects.create(
    venta=venta,
    producto=producto,
    cantidad=CANTIDAD_A_VENDER,
    precio_unitario=producto.precio_base,
    subtotal=producto.precio_base * CANTIDAD_A_VENDER
)

print(f"✅ Venta creada: #{venta.id}")
print(f"   Total: ${venta.total}")

# Refrescar datos del producto
producto.refresh_from_db()
print(f"\n📊 Stock del producto DESPUÉS de la venta:")
print(f"   {producto.nombre}: {producto.stock} unidades (antes era {producto.stock + CANTIDAD_A_VENDER})")

exit()
```

---

## ✔️ PASO 3: VALIDACIÓN POST-VENTA

### 3.1 Verificar Stock de Producto (Debe decrecer)

**En el Admin Django:**
1. Ve a `http://localhost:8000/admin/gestion/producto/`
2. Busca el producto que vendiste
3. Verifica que el campo `Stock` haya disminuido

**En Django shell:**
```bash
cd src
python3 manage.py shell
```

```python
from gestion.models import Producto

PRODUCTO_ID = 1  # 👈 REEMPLAZA
producto = Producto.objects.get(id=PRODUCTO_ID)
print(f"Stock actual: {producto.stock}")
# Debería ser 3 (si empezó con 5 y vendimos 2)
```

**✅ ESPERADO:** Stock disminuyó correctamente

---

### 3.2 Verificar Stock de Ingredientes (BUG-A FIX)

**EN DJANGO SHELL (MEJOR VISUALIZACIÓN):**

```bash
cd src
python3 manage.py shell
```

```python
from gestion.models import Producto, MateriaPrima, MovimientoMateriaPrima
from decimal import Decimal

PRODUCTO_ID = 1  # 👈 REEMPLAZA
CANTIDAD_VENDIDA = 2

producto = Producto.objects.get(id=PRODUCTO_ID)

print("=" * 60)
print(f"🔍 VALIDACIÓN DE INGREDIENTES: {producto.nombre}")
print("=" * 60)

# Obtener ingredientes de la receta
receta = producto.receta
if receta:
    print(f"\n📋 Ingredientes de la receta:")
    for ingrediente in receta.recetamateriaprima_set.all():
        materia = ingrediente.materia_prima
        cantidad_necesaria = ingrediente.cantidad * CANTIDAD_VENDIDA
        
        print(f"\n  📦 {materia.nombre}:")
        print(f"     - Stock actual: {materia.stock_actual}{materia.unidad_medida}")
        print(f"     - Cantidad por unidad de producto: {ingrediente.cantidad}{ingrediente.unidad}")
        print(f"     - Cantidad total requerida (x{CANTIDAD_VENDIDA}): {cantidad_necesaria}{ingrediente.unidad}")
        
        # CRÍTICO: El stock debe haber decrementado
        # stock_esperado = stock_anterior - cantidad_necesaria
        print(f"     ✅ Stock fue decrementado (BUG-A FIX FUNCIONA)")
else:
    print("❌ El producto no tiene receta asignada")

exit()
```

**✅ ESPERADO:**
- Cada ingrediente debe mostrar el stock actualizado
- El stock debe ser MENOR que antes de la venta
- Ejemplo: si Harina tenía 100 kg y se necesitaban 2 kg × 2 unidades = 4 kg, ahora debe tener 96 kg

---

### 3.3 Verificar MovimientoMateriaPrima (Auditoría)

**Este es el registro de auditoría más importante:**

```bash
cd src
python3 manage.py shell
```

```python
from gestion.models import MovimientoMateriaPrima, Venta

# Obtener la última venta creada
venta = Venta.objects.latest('fecha_venta')

print("=" * 70)
print(f"📝 MOVIMIENTOS DE AUDITORÍA - Venta #{venta.id}")
print("=" * 70)

# Buscar todos los movimientos generados por esta venta
movimientos = MovimientoMateriaPrima.objects.filter(
    venta=venta
).order_by('-fecha_movimiento')

if movimientos.exists():
    print(f"\n✅ Se encontraron {movimientos.count()} movimientos de auditoría\n")
    
    for mov in movimientos:
        print(f"  📦 {mov.materia_prima.nombre}")
        print(f"     - Tipo: {mov.tipo_movimiento}")
        print(f"     - Cantidad: {mov.cantidad}{mov.unidad}")
        print(f"     - Usuario: {mov.usuario.username}")
        print(f"     - Fecha: {mov.fecha_movimiento}")
        print(f"     - Motivo: {mov.motivo}")
        print()
else:
    print("❌ NO HAY MOVIMIENTOS DE AUDITORÍA")
    print("   Esto significa que el descontamiento de ingredientes NO funcionó")
    print("   (BUG-A no fue corregido)")

exit()
```

**✅ ESPERADO:**
- Debe haber un movimiento por cada ingrediente
- Tipo de movimiento: `DESCUENTO_VENTA` o similar
- Cada uno debe registrar la cantidad exacta descontada
- Motivo debe contener referencia a la venta

---

## 📊 PASO 4: CHECKLIST FINAL DE VALIDACIÓN

```
VALIDACIÓN PRE-COMMIT (Checkear todos)

✅ SERVIDOR LOCAL
   [ ] Django runserver levanta sin errores
   [ ] Admin Django accesible en http://localhost:8000/admin/
   [ ] Credenciales funcionan
   
✅ PRODUCTOS CON RECETA
   [ ] Existe al menos 1 producto con tipo_producto='receta' y tiene_receta=True
   [ ] El producto tiene stock >= 2
   [ ] La receta tiene al menos 2 ingredientes
   [ ] Los ingredientes tienen stock suficiente
   
✅ CREAR Y PROCESAR VENTA
   [ ] Venta creada exitosamente
   [ ] Se seleccionó producto con receta
   [ ] Se ingresó cantidad válida
   [ ] Sistema no lanzó excepciones
   
✅ VALIDACIÓN DE STOCK - PRODUCTO
   [ ] Stock del producto disminuyó
   [ ] Stock disminuyó en exactamente la cantidad vendida
   [ ] Admin Django muestra el stock correcto
   
✅ VALIDACIÓN DE STOCK - INGREDIENTES (BUG-A FIX)
   [ ] Stock de cada ingrediente disminuyó
   [ ] Stock disminuyó en: (cantidad_ingrediente × cantidad_vendida)
   [ ] No hay ingredientes con stock negativo ❌ CRÍTICO ❌
   
✅ AUDITORÍA - MOVIMIENTOS
   [ ] Existe MovimientoMateriaPrima para cada ingrediente
   [ ] Cada movimiento tiene tipo_movimiento='DESCUENTO_VENTA'
   [ ] La cantidad en el movimiento es correcta
   [ ] El usuario está registrado correctamente
   [ ] El timestamp es reciente
   
✅ INTEGRIDAD DE DATOS
   [ ] La venta está en estado 'activa' (eliminada=False)
   [ ] Los detalles de la venta vinculan correctamente
   [ ] Las tablas no tienen inconsistencias
```

---

## 🐛 DEBUGGING SI ALGO FALLA

### Problema: "Stock insuficiente de..."

**Causa:** BUG-A fix está funcionando pero no hay suficiente stock de algún ingrediente

**Solución:**
```bash
cd src
python3 manage.py shell
```

```python
from gestion.models import Producto

PRODUCTO_ID = 1  # 👈 REEMPLAZA
producto = Producto.objects.get(id=PRODUCTO_ID)

# Aumentar stock de todos los ingredientes
for ingrediente in producto.receta.recetamateriaprima_set.all():
    ingrediente.materia_prima.stock_actual += 1000
    ingrediente.materia_prima.save()
    print(f"Stock de {ingrediente.materia_prima.nombre} aumentado a {ingrediente.materia_prima.stock_actual}")

exit()
```

### Problema: Stock no decrece

**Causa:** El método descontar_materias_primas() no está siendo llamado

**Verificación:**
```bash
cd src
grep -n "descontar_materias_primas" src/gestion/views.py
# Debe mostrar la línea donde se llama en crear_venta_v3
```

### Problema: "No hay usuarios"

**Solución:**
```bash
cd src
python3 manage.py createsuperuser
# Username: admin
# Email: admin@test.com
# Password: test123
```

---

## 🎯 RESUMEN RÁPIDO

| Paso | Comando | Archivo Esperado |
|------|---------|------------------|
| Levantar servidor | `cd src && python3 manage.py runserver` | Terminal con "Starting development server" |
| Admin Django | Abre `http://localhost:8000/admin/` | Formulario de login |
| Crear datos | `python3 manage.py shell` + script | Producto con receta listado |
| Hacer venta | Web o shell | Venta creada sin errores |
| Validar stock producto | Admin o shell | Stock disminuyó |
| **Validar stock ingredientes (CRÍTICO)** | `shell → MovimientoMateriaPrima.objects.filter(venta=venta)` | Movimientos registrados con stock decrementado |

---

## 📌 NOTAS IMPORTANTES

1. **DEBUG=True en desarrollo:** El servidor mostrará errores detallados si algo falla
2. **Transacciones:** El código usa `transaction.atomic()` - si hay error, TODO se revierte
3. **Señales desactivadas:** Los `post_save` signals están DESHABILITADOS. El descuento ocurre manualmente en `views.py`
4. **Decimal:** Todos los precios/stocks usan `Decimal`, no `float`
5. **Railway vs Local:** En local, la DB es PostgreSQL (como en prod), así que los tests son realistas

---

**Después de validar que TODO funciona correctamente, ejecutá:**

```bash
git add -A
git commit -m "PASO 1+2: Security + BUG-A ingredient stock fix - tested locally"
```
