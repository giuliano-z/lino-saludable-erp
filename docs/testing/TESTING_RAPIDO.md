# 🚀 INSTRUCCIONES RÁPIDAS: TESTING BUG-A (1 PÁGINA)

## Levanta servidor + ejecuta test automático

### Terminal 1: Server Django
```bash
cd /Users/giulianozulatto/Proyectos/lino_saludable/src
python3 manage.py runserver
# Esperado: "Starting development server at http://127.0.0.1:8000/"
```

### Terminal 2: Test automático
```bash
cd /Users/giulianozulatto/Proyectos/lino_saludable
python3 test_bug_a_fix.py
```

## Interpretación de resultados

| Output | Significa | Acción |
|--------|-----------|--------|
| `✅ BUG-A FIX ESTÁ FUNCIONANDO` | TODO OK | Proceder a git commit |
| `❌ PROBLEMA DETECTADO` | Algo falló | Ver error, revisar logs |
| `No connection/Error` | Server no levantó | Terminal 1: verificar que está corriendo |

---

## Si quieres probar manualmente paso a paso

```bash
# En Terminal 2 (nueva), en carpeta src:
python3 manage.py shell

# Luego pega SOLO ESTOS COMANDOS (en orden):
```

### Bloque 1: Crear datos
```python
from gestion.models import Producto, Receta, MateriaPrima, RecetaMateriaPrima
from django.contrib.auth.models import User
from decimal import Decimal

usuario, _ = User.objects.get_or_create(username='test', defaults={'email': 'test@local.com'})
harina, _ = MateriaPrima.objects.get_or_create(nombre='Harina TEST', defaults={'stock_actual': Decimal('100'), 'unidad_medida': 'kg', 'precio_unitario': Decimal('35')})
aceite, _ = MateriaPrima.objects.get_or_create(nombre='Aceite TEST', defaults={'stock_actual': Decimal('50'), 'unidad_medida': 'l', 'precio_unitario': Decimal('80')})
receta, _ = Receta.objects.get_or_create(nombre='Brownies TEST', defaults={'descripcion': 'test'})
RecetaMateriaPrima.objects.get_or_create(receta=receta, materia_prima=harina, defaults={'cantidad': Decimal('2'), 'unidad': 'kg'})
RecetaMateriaPrima.objects.get_or_create(receta=receta, materia_prima=aceite, defaults={'cantidad': Decimal('0.5'), 'unidad': 'l'})
producto, _ = Producto.objects.get_or_create(nombre='Brownies TEST', defaults={'tipo_producto': 'receta', 'tiene_receta': True, 'receta': receta, 'precio_base': Decimal('150'), 'stock': 10, 'margen_ganancia': Decimal('30')})

print(f"✅ Producto: {producto.id}")
print(f"   Stock: {producto.stock}")
print(f"   Harina: {harina.stock_actual}kg")
print(f"   Aceite: {aceite.stock_actual}l")
```

### Bloque 2: Ver stock ANTES
```python
producto.refresh_from_db()
harina.refresh_from_db()
aceite.refresh_from_db()
print(f"ANTES - Producto: {producto.stock}, Harina: {harina.stock_actual}, Aceite: {aceite.stock_actual}")
```

### Bloque 3: Crear venta
```python
from gestion.models import Venta, VentaDetalle
from django.db.models import F
from django.db import transaction
from django.utils import timezone

CANTIDAD = 2

with transaction.atomic():
    venta = Venta.objects.create(usuario=usuario, numero_seguimiento=f"TEST-{timezone.now().timestamp()}", fecha_venta=timezone.now(), total=producto.precio_base * CANTIDAD)
    VentaDetalle.objects.create(venta=venta, producto=producto, cantidad=CANTIDAD, precio_unitario=producto.precio_base, subtotal=producto.precio_base * CANTIDAD)
    Producto.objects.filter(id=producto.id).update(stock=F('stock') - CANTIDAD)
    if producto.tiene_receta and producto.receta:
        producto.descontar_materias_primas(CANTIDAD, usuario)

print(f"✅ Venta #{venta.id} creada")
```

### Bloque 4: Ver stock DESPUÉS
```python
producto.refresh_from_db()
harina.refresh_from_db()
aceite.refresh_from_db()
print(f"DESPUÉS - Producto: {producto.stock}, Harina: {harina.stock_actual}, Aceite: {aceite.stock_actual}")
```

### Bloque 5: Validar movimientos ✅
```python
from gestion.models import MovimientoMateriaPrima

movs = MovimientoMateriaPrima.objects.filter(venta=venta)
print(f"\n✅ Movimientos: {movs.count()}")
if movs.count() > 0:
    for m in movs:
        print(f"   - {m.materia_prima.nombre}: {m.cantidad}{m.unidad}")
    print("\n✅ BUG-A FIX FUNCIONA")
else:
    print("❌ BUG-A NO FUNCIONA")

exit()
```

---

## ✅ Checklist visual

```
Stock del Producto:
  ANTES: [████████████] 10 unidades
  DESPUÉS: [████████] 8 unidades  ✅ Disminuyó 2

Stock de Harina:
  ANTES: [████████████████████] 100 kg
  DESPUÉS: [████████████████] 96 kg  ✅ Disminuyó 4

Stock de Aceite:
  ANTES: [█████████████] 50 l
  DESPUÉS: [████████████] 49 l  ✅ Disminuyó 1

Movimientos Registrados:
  [✅] Harina: 4 kg
  [✅] Aceite: 1 l
```

---

## Cuando todo está OK

```bash
git status  # Ver cambios
git add -A
git commit -m "PASO 1+2: Security + BUG-A ingredient stock fix (tested locally)"
git status  # Verificar: "nothing to commit"
```

---

## ¿Hay problema?

| Error | Solución |
|-------|----------|
| `ModuleNotFoundError: No module named 'gestion'` | `cd src` antes de correr shell |
| `ProgrammingError: relation "gestion_..." does not exist` | Base datos vacía, correr migraciones: `python3 manage.py migrate` |
| Server no levanta | `.env` no existe o `SECRET_KEY` falta. Ejecutar: `echo "SECRET_KEY=test123" > .env && echo "DEBUG=True" >> .env` |
| Test produce error | Ver `GUIA_COMPLETA_TESTING.md` sección "Troubleshooting" |

---

## Documentación disponible

- **Guía detallada:** `GUIA_COMPLETA_TESTING.md`
- **Checklist rápida:** `TESTING_CHECKLIST_RAPIDO.md`  
- **Resumen visual:** `RESUMEN_VISUAL_TESTING.md`
- **Script automático:** `test_bug_a_fix.py`

---

**Tiempo total:** 5-15 minutos | **Dificultad:** Fácil | **Riesgo:** Ninguno (test local)
