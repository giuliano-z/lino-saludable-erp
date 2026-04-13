# 🧪 TESTING BUG-A FIX - CHECKLIST RÁPIDO

## 🚀 INICIO RÁPIDO (2 minutos)

```bash
# Terminal 1: Levantar servidor
cd /Users/giulianozulatto/Proyectos/lino_saludable/src
python3 manage.py runserver
# Esperado: "Starting development server at http://127.0.0.1:8000/"

# Terminal 2: Ejecutar test automático (EN OTRA TERMINAL)
cd /Users/giulianozulatto/Proyectos/lino_saludable
python3 test_bug_a_fix.py
```

**Resultado esperado:**
```
✅ RESUMEN DEL TEST
   ✅ BUG-A FIX ESTÁ FUNCIONANDO
   ✅ Los ingredientes se descuentan automáticamente
   ✅ Los movimientos se registran en auditoría
```

---

## ✅ CHECKLIST MANUAL (5 minutos)

### 1. Servidor levantado ✅
- [ ] Terminal muestra: "Starting development server at http://127.0.0.1:8000/"
- [ ] No hay errores de sintaxis

### 2. Admin accesible ✅
- [ ] Abre `http://localhost:8000/admin/`
- [ ] Se carga el formulario de login
- [ ] Credenciales: `admin_lino` / `changeme` funcionan (o las que creaste)

### 3. Producto con receta existe ✅
**Vía admin Django:**
- [ ] Ve a "Productos"
- [ ] Busca producto con `Tiene Receta = Sí`
- [ ] Anota ID y nombre

**Vía shell:**
```bash
cd src && python3 manage.py shell
>>> from gestion.models import Producto
>>> p = Producto.objects.filter(tiene_receta=True, stock__gte=2).first()
>>> print(f"{p.nombre} (ID: {p.id})")
>>> exit()
```

### 4. Crear venta (opción A: WEB) ✅
- [ ] En el dashboard, busca "Nueva Venta" o "Crear Venta"
- [ ] Selecciona el producto con receta
- [ ] Ingresa cantidad: `2`
- [ ] Haz clic en "Guardar" o "Crear Venta"
- [ ] Aparece mensaje de éxito (sin errores)

**Vía shell (opción B):**
```bash
cd /Users/giulianozulatto/Proyectos/lino_saludable
python3 test_bug_a_fix.py
```

### 5. Verificar Stock del Producto ✅
**Debe disminuir en la cantidad vendida**

Admin Django:
- [ ] Abre producto
- [ ] Stock actual = Stock anterior - cantidad vendida

Shell:
```bash
cd src && python3 manage.py shell
>>> from gestion.models import Producto
>>> p = Producto.objects.get(id=1)  # 👈 TU PRODUCTO
>>> print(f"Stock actual: {p.stock}")  # Debe ser menor
>>> exit()
```

### 6. Verificar Stock de Ingredientes ✅
**ESTO ES EL BUG-A FIX - CRÍTICO**

Shell:
```bash
cd src && python3 manage.py shell
>>> from gestion.models import Producto
>>> p = Producto.objects.get(id=1)  # 👈 TU PRODUCTO
>>> for ing in p.receta.recetamateriaprima_set.all():
...     mp = ing.materia_prima
...     print(f"{mp.nombre}: {mp.stock_actual}{mp.unidad_medida}")
>>> exit()
```

**Esperado:** Stock de cada ingrediente disminuyó
- Harina: 100 → 96 (si se vendieron 2 unidades × 2kg = 4kg)
- Aceite: 50 → 49 (si se vendieron 2 unidades × 0.5l = 1l)

### 7. Verificar Movimientos de Auditoría ✅
**Prueba del descuento real**

Admin Django:
- [ ] Ve a "Movimientos de Materia Prima"
- [ ] Filtra por la venta creada
- [ ] Debe haber movimientos para cada ingrediente

Shell:
```bash
cd src && python3 manage.py shell
>>> from gestion.models import MovimientoMateriaPrima, Venta
>>> v = Venta.objects.latest('fecha_venta')
>>> movs = MovimientoMateriaPrima.objects.filter(venta=v)
>>> print(f"Movimientos encontrados: {movs.count()}")
>>> for m in movs:
...     print(f"  - {m.materia_prima.nombre}: {m.cantidad}{m.unidad}")
>>> exit()
```

**Esperado:** 
- [ ] `count()` > 0 (hay movimientos)
- [ ] Un movimiento por cada ingrediente
- [ ] Cantidades coinciden con lo esperado

---

## 📋 RESUMEN VISUAL

| Validación | Antes | Después | Estado |
|-----------|-------|---------|--------|
| Stock Producto | 10 | 8 | ✅ Decrementó |
| Stock Harina | 100 kg | 96 kg | ✅ Decrementó |
| Stock Aceite | 50 l | 49 l | ✅ Decrementó |
| Movimientos | 0 | 2 | ✅ Se registraron |

---

## 🐛 Si algo falla

### Error: "Stock insuficiente de..."
→ Los ingredientes no tienen suficiente stock
→ Aumenta stock en el admin: Materia Prima → editar

### Error: Producto sin receta
→ Crea un producto con tipo_producto='receta'
→ O ejecuta `python3 test_bug_a_fix.py` que lo crea

### Stock no disminuye
→ El fix NO está funcionando
→ Verifica que `descontar_materias_primas()` esté en `views.py` línea 3260+

### No hay movimientos
→ Igual que arriba - el descuento no se ejecutó

---

## ✅ CUANDO TODO FUNCIONA

```bash
git add -A
git commit -m "PASO 1+2: Security + BUG-A ingredient stock fix - locally tested"
git status  # Debe mostrar "nothing to commit"
```

---

## 📞 REFERENCIAS

- **Guía completa:** Ver `GUIA_TESTING_BUG_A.md`
- **Script automático:** `python3 test_bug_a_fix.py`
- **Modelos afectados:** `src/gestion/models.py` líneas 654-804
- **Vistas modificadas:** `src/gestion/views.py` línea 3260+
