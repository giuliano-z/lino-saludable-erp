# ✅ RESPUESTAS A TUS 3 PREGUNTAS

## Pregunta 1: ¿Cómo levanto el servidor local?

### Respuesta corta:
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

### ¿Hay algún comando especial?
No. Es el comando estándar de Django. El proyecto **no tiene `start.sh` configurado**.

### Acceso después de levantado:
- **Web:** `http://localhost:8000`
- **Admin:** `http://localhost:8000/admin/`
- **Credenciales:** `admin_lino` / `changeme`

---

## Pregunta 2: ¿Hay datos de prueba en local o necesito seed_demo_data.py?

### Respuesta:
**NO necesitás seed_demo_data.py**. Tenés 3 opciones:

### Opción A: Usar datos existentes en BD (SI HAY)
```bash
cd /Users/giulianozulatto/Proyectos/lino_saludable/src
python3 manage.py shell

# Verificar si existen productos con receta
>>> from gestion.models import Producto
>>> p = Producto.objects.filter(tiene_receta=True, stock__gte=2).first()
>>> if p:
...     print(f"Producto: {p.nombre} (ID: {p.id})")
... else:
...     print("No hay productos con receta")
>>> exit()
```

### Opción B: Crear datos de prueba automáticamente
```bash
# Ejecutar el script automático que CREA datos
python3 test_bug_a_fix.py
```

Este script **automáticamente**:
1. Crea usuario de prueba
2. Crea 2 materias primas con stock
3. Crea receta con esos ingredientes
4. Crea producto que usa la receta
5. Crea venta
6. Valida todo

### Opción C: Crear datos manualmente en shell (10 min)
Ver sección "Paso 3" en `GUIA_COMPLETA_TESTING.md` con código copy/paste

### Resumen:
- **Automático (Recomendado):** `python3 test_bug_a_fix.py` (2 min)
- **Manual:** Seguir pasos en GUIA_COMPLETA_TESTING.md (10 min)
- **Existente:** Si hay datos, usarlos directamente

---

## Pregunta 3: Checklist de exactamente qué probar para validar BUG-A fix

### CHECKLIST COMPLETA

```
══════════════════════════════════════════════════════════════════
  VALIDACIÓN DEL BUG-A FIX: DESCUENTO DE INGREDIENTES EN VENTA
══════════════════════════════════════════════════════════════════

🔧 PREPARACIÓN
  [ ] Server levantado: http://localhost:8000 accesible
  [ ] Admin accesible: http://localhost:8000/admin/ con login
  [ ] Datos de prueba listos (producto con receta + ingredientes)

📦 PRODUCTO PARA PRUEBA
  [ ] Nombre: Brownies Almendra (o similar con receta)
  [ ] Tipo: receta (no fraccionamiento ni reventa)
  [ ] tiene_receta: Sí/True
  [ ] Stock actual: >= 2 unidades
  [ ] Receta asignada: Sí
  [ ] Ingredientes en la receta: >= 2
      [ ] Ejemplo: Harina 2kg/unidad, Aceite 0.5l/unidad

📊 STOCKS INICIALES (ANTES DE VENTA)
  [ ] Producto: anotar stock (ej: 10 unidades)
  [ ] Ingrediente 1: anotar stock (ej: 100 kg Harina)
  [ ] Ingrediente 2: anotar stock (ej: 50 l Aceite)
  
  Para verificar en admin:
    → Ir a /admin/gestion/producto/
    → Ir a /admin/gestion/materiaprima/

💳 CREAR VENTA
  [ ] Seleccionar producto con receta (Brownies)
  [ ] Cantidad: 2 unidades
  [ ] Verificar precio total correcto
  [ ] Hacer click en "Guardar" o "Crear Venta"
  [ ] Venta creada sin errores (no debe haber mensaje rojo)

✅ VALIDACIÓN 1: STOCK DEL PRODUCTO (BÁSICO)
  [ ] En admin Django o shell, abrir producto
  [ ] Stock anterior: 10
  [ ] Stock nuevo: 8 (= 10 - 2)
  [ ] ¿Disminuyó correctamente? SÍ / NO
  
  Verificar en admin:
    → /admin/gestion/producto/ → buscar producto → ver campo "Stock"

✅ VALIDACIÓN 2: STOCK DE INGREDIENTES (BUG-A FIX CRÍTICO)
  
  🔴 ESTO ES LO MÁS IMPORTANTE 🔴
  
  En Django shell:
  ```
  python3 manage.py shell
  >>> from gestion.models import Producto
  >>> p = Producto.objects.get(id=1)  # TU PRODUCTO
  >>> for ing in p.receta.recetamateriaprima_set.all():
  ...     mp = ing.materia_prima
  ...     print(f"{mp.nombre}: {mp.stock_actual}{mp.unidad_medida}")
  ```
  
  Validar:
  [ ] Harina: 100 kg → 96 kg
      Cálculo: 100 - (2 kg/unidad × 2 unidades) = 100 - 4 = 96 ✅
      ¿Stock disminuyó? SÍ / NO
      
  [ ] Aceite: 50 l → 49 l
      Cálculo: 50 - (0.5 l/unidad × 2 unidades) = 50 - 1 = 49 ✅
      ¿Stock disminuyó? SÍ / NO
  
  Si NO disminuyó → BUG-A NO fue corregido
  Si SÍ disminuyó → BUG-A FIX FUNCIONA ✅

✅ VALIDACIÓN 3: MOVIMIENTOS DE MATERIA PRIMA (AUDITORÍA)
  
  🔴 PRUEBA DEFINITIVA DEL FIX 🔴
  
  En Django shell:
  ```
  python3 manage.py shell
  >>> from gestion.models import MovimientoMateriaPrima, Venta
  >>> v = Venta.objects.latest('fecha_venta')
  >>> movs = MovimientoMateriaPrima.objects.filter(venta=v)
  >>> print(f"Total movimientos: {movs.count()}")
  >>> for m in movs:
  ...     print(f"- {m.materia_prima.nombre}: {m.cantidad}{m.unidad}")
  ```
  
  Validar:
  [ ] Total movimientos: 2 (uno por cada ingrediente)
      ¿count() == 2? SÍ / NO
      
  [ ] Movimiento 1:
      [ ] Materia Prima: Harina
      [ ] Cantidad: 4 kg
      [ ] Tipo: DESCUENTO_VENTA
      [ ] Usuario: test_user
      
  [ ] Movimiento 2:
      [ ] Materia Prima: Aceite
      [ ] Cantidad: 1 l
      [ ] Tipo: DESCUENTO_VENTA
      [ ] Usuario: test_user
  
  Si NO hay movimientos → BUG-A NO fue corregido
  Si HAY movimientos con valores correctos → BUG-A FIX FUNCIONA ✅

═══════════════════════════════════════════════════════════════════

RESULTADO FINAL:

  [ ] VALIDACIÓN 1 (Stock producto): ✅ PASÓ
  [ ] VALIDACIÓN 2 (Stock ingredientes): ✅ PASÓ  ← CRÍTICA
  [ ] VALIDACIÓN 3 (Movimientos): ✅ PASÓ         ← PRUEBA DEFINITIVA

Si las 3 pasaron → BUG-A FIX ESTÁ FUNCIONANDO → git commit ✅
Si alguna falló → BUG-A NO funciona → revisar código ❌
```

---

## 📝 TABLA RESUMEN

| Validación | Qué Chequear | Dónde | Resultado Esperado | ¿Crítico? |
|-----------|---|---|---|---|
| 1️⃣ Stock Producto | Disminuyó en cantidad vendida | Admin o shell | 10 → 8 | ⚠️ |
| 2️⃣ Stock Ingredientes | **Disminuyó por ingrediente** | Shell `.receta.recetamateriaprima_set` | Harina 100→96, Aceite 50→49 | 🔴 |
| 3️⃣ Movimientos | **Registrados en auditoría** | `MovimientoMateriaPrima.objects.filter()` | count() >= 2 con datos correctos | 🔴 |

---

## 🎯 RESUMEN EJECUTIVO

### Pregunta 1: ¿Cómo levanto el servidor?
**Respuesta:** `cd src && python3 manage.py runserver`

### Pregunta 2: ¿Hay datos de prueba?
**Respuesta:** Sí (existentes en BD) o usá `python3 test_bug_a_fix.py` que crea todo automáticamente

### Pregunta 3: ¿Qué probar?
**Respuesta:**
1. ✅ Stock del producto disminuye
2. ✅ Stock de ingredientes disminuye (CRÍTICO)
3. ✅ Movimientos se registran en MovimientoMateriaPrima (CRÍTICO)

Si las 3 pasan → BUG-A FIX funciona → git commit

---

## 🚀 OPCIÓN RÁPIDA (SIN LEER NADA)

```bash
# Terminal 1
cd /Users/giulianozulatto/Proyectos/lino_saludable/src
python3 manage.py runserver

# Terminal 2
python3 test_bug_a_fix.py
```

Si ves `✅ BUG-A FIX ESTÁ FUNCIONANDO` → Listo, git commit

---

## 📚 REFERENCIAS

- **Checklist detallado:** Ver `TESTING_RAPIDO.md`
- **Script automático:** `python3 test_bug_a_fix.py`
- **Guía completa:** `GUIA_COMPLETA_TESTING.md`

---

**Creado:** 9 de abril de 2026  
**Por:** GitHub Copilot
