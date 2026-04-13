# 🎯 ÍNDICE FINAL: CÓMO TESTEAR BUG-A FIX

## 📍 ESTÁS AQUÍ

Has hecho 3 preguntas. Aquí están **todas las respuestas** en un solo lugar.

---

## 🚀 OPCIÓN RÁPIDA (SOLO 2 MINUTOS)

```bash
# Terminal 1: Levantar server
cd /Users/giulianozulatto/Proyectos/lino_saludable/src
python3 manage.py runserver

# Terminal 2: Ejecutar test automático
cd /Users/giulianozulatto/Proyectos/lino_saludable
python3 test_bug_a_fix.py
```

**Resultado esperado:**
```
✅ BUG-A FIX ESTÁ FUNCIONANDO
✅ Los ingredientes se descuentan automáticamente
✅ Los movimientos se registran en auditoría
```

**Si ves esto → git commit. FIN.**

---

## 📚 RESPUESTAS A TUS 3 PREGUNTAS

### ¿Cómo levanto el servidor local?
```bash
cd /Users/giulianozulatto/Proyectos/lino_saludable/src
python3 manage.py runserver
```
➜ Esperas a que veas: "Starting development server at http://127.0.0.1:8000/"
➜ No hay comando especial, es Django standard

**Ver archivo:** `RESPUESTAS_TUS_3_PREGUNTAS.md` (Pregunta 1)

### ¿Hay datos de prueba?
**Opción A (RECOMENDADA):** Script automático crea TODO
```bash
python3 test_bug_a_fix.py
```

**Opción B:** Datos existentes en la BD
```bash
cd src && python3 manage.py shell
>>> from gestion.models import Producto
>>> p = Producto.objects.filter(tiene_receta=True, stock__gte=2).first()
```

**Opción C:** Crear manualmente paso a paso (ver GUIA_COMPLETA_TESTING.md)

**Ver archivo:** `RESPUESTAS_TUS_3_PREGUNTAS.md` (Pregunta 2)

### ¿Qué probar exactamente?
Tres validaciones CRÍTICAS:

1. **✅ Stock del Producto disminuye**
   - ANTES: 10 unidades
   - VENTA: 2 unidades
   - DESPUÉS: 8 unidades ← Debe disminuir

2. **✅ Stock de Ingredientes disminuye (BUG-A FIX)**
   - Harina: 100kg → 96kg (disminuyó 4kg)
   - Aceite: 50l → 49l (disminuyó 1l)
   - ← ESTO ES LO MÁS IMPORTANTE

3. **✅ Movimientos registrados en auditoría**
   - MovimientoMateriaPrima.count() >= 2
   - Debe haber un movimiento por cada ingrediente
   - ← PRUEBA DEFINITIVA del fix

**Ver archivo:** `RESPUESTAS_TUS_3_PREGUNTAS.md` (Pregunta 3)

---

## 🗂️ DOCUMENTOS POR TIPO

### 🏃 QUIERO HACERLO RÁPIDO (2-5 min)
```
TESTING_RAPIDO.md ..................... Copy/paste bloques en shell
test_bug_a_fix.py .................... Script automático
REFERENCE_TESTING.md ................. Cheatsheet / quick reference
```

### 🧠 QUIERO ENTENDER (10-15 min)
```
GUIA_COMPLETA_TESTING.md ............. Guía paso a paso con explicaciones
RESUMEN_VISUAL_TESTING.md ............ Diagramas y visualizaciones
```

### 📋 QUIERO VER MIS RESPUESTAS
```
RESPUESTAS_TUS_3_PREGUNTAS.md ........ Las 3 preguntas que hiciste
INDICE_TESTING_DOCS.md .............. Resumen de qué documento usar
```

### 🎯 ÍNDICES Y REFERENCIAS
```
Este archivo (INDEX_FINAL.md) ........ Estás leyendo esto
INDICE_TESTING_DOCS.md .............. Matriz de documentos
REFERENCE_TESTING.md ................. Tabla de comandos rápidos
```

---

## 📊 MATRIZ: ¿QUÉ DOCUMENTO LEO?

| Tengo | Preferencia | Documento | Tiempo |
|-------|-----------|-----------|--------|
| Prisa | Automático | `test_bug_a_fix.py` | 2 min |
| Prisa | Manual | `TESTING_RAPIDO.md` | 5 min |
| Tiempo | Entender todo | `GUIA_COMPLETA_TESTING.md` | 15 min |
| Tiempo | Ver diagramas | `RESUMEN_VISUAL_TESTING.md` | 10 min |
| ? | Cheatsheet | `REFERENCE_TESTING.md` | 2 min |
| ? | Mis respuestas | `RESPUESTAS_TUS_3_PREGUNTAS.md` | 5 min |

---

## ✅ FLUJO RECOMENDADO

```
┌─────────────────────────────────┐
│ 1. Leer RESPUESTAS_TUS_3_...md  │ ← EMPEZÁ AQUÍ
│    (respuestas a tus preguntas) │
└───────────┬─────────────────────┘
            ↓
┌──────────────────────────────────┐
│ 2. Elegir método:                │
│    a) Automático: test_bug_a...py │
│    b) Manual: TESTING_RAPIDO.md   │
│    c) Completo: GUIA_COMPLETA...md│
└───────────┬──────────────────────┘
            ↓
┌──────────────────────────────────┐
│ 3. Ejecutar tests                │
│    (2-15 minutos según opción)   │
└───────────┬──────────────────────┘
            ↓
   ¿Pasaron los tests?
            │
      ┌─────┴─────┐
      ↓           ↓
     SÍ          NO
      ↓           ↓
    git       Ver TROUBLESHOOTING
   commit     en GUIA_COMPLETA...md
      ↓
  LISTO ✅
```

---

## 🎯 COMANDOS CLAVE

### Levantar server
```bash
cd /Users/giulianozulatto/Proyectos/lino_saludable/src
python3 manage.py runserver
```

### Test automático (RECOMENDADO)
```bash
cd /Users/giulianozulatto/Proyectos/lino_saludable
python3 test_bug_a_fix.py
```

### Verificar stocks en shell
```bash
cd src && python3 manage.py shell
>>> from gestion.models import Producto
>>> p = Producto.objects.get(id=1)
>>> for ing in p.receta.recetamateriaprima_set.all():
...     print(f"{ing.materia_prima.nombre}: {ing.materia_prima.stock_actual}")
>>> exit()
```

### Verificar movimientos
```bash
cd src && python3 manage.py shell
>>> from gestion.models import MovimientoMateriaPrima, Venta
>>> v = Venta.objects.latest('fecha_venta')
>>> MovimientoMateriaPrima.objects.filter(venta=v).count()
>>> exit()
```

---

## 📋 CHECKLIST VISUAL

```
ANTES DE EMPEZAR:
  [ ] Leer RESPUESTAS_TUS_3_PREGUNTAS.md
  [ ] Elegir método (automático vs manual)
  
EJECUTAR TEST:
  [ ] Terminal 1: Server corriendo
  [ ] Terminal 2: Ejecutar test
  
VALIDAR RESULTADOS:
  [ ] ✅ Stock producto disminuyó
  [ ] ✅ Stock ingredientes disminuyó (CRÍTICO)
  [ ] ✅ Movimientos registrados (CRÍTICO)
  
DESPUÉS:
  [ ] Todos los puntos anteriores pasaron
  [ ] git commit
  [ ] Siguiente: BUG-B y BUG-C
```

---

## 🚀 EMPEZÁ AQUÍ

### Paso 1: Lee esto
Estás leyendo el INDEX. Ya checkeado ✅

### Paso 2: Lee tus respuestas
Abre: `RESPUESTAS_TUS_3_PREGUNTAS.md`
- Pregunta 1: ¿Cómo levanto el servidor?
- Pregunta 2: ¿Hay datos de prueba?
- Pregunta 3: ¿Qué debo probar?

### Paso 3: Elige un método

**OPCIÓN A - RÁPIDO (RECOMENDADO)**
```bash
# Terminal 1
cd src && python3 manage.py runserver

# Terminal 2
python3 test_bug_a_fix.py
```

**OPCIÓN B - PASO A PASO**
1. Abre `TESTING_RAPIDO.md`
2. Copia/pega los bloques de código en orden
3. Ver resultados

**OPCIÓN C - COMPLETO**
1. Abre `GUIA_COMPLETA_TESTING.md`
2. Lee y entiende cada paso
3. Ejecuta manualmente

### Paso 4: Validar
Asegúrate de que:
- [ ] Stock del producto disminuyó
- [ ] Stock de ingredientes disminuyó
- [ ] Movimientos se registraron

### Paso 5: Commit
```bash
git add -A
git commit -m "PASO 1+2: Security + BUG-A fix (tested locally)"
```

---

## 📚 TODOS LOS DOCUMENTOS

```
TESTING:
  ✅ TESTING_RAPIDO.md .................. (1 página - copiar/pegar)
  ✅ test_bug_a_fix.py ................. (script automático)
  ✅ TESTING_CHECKLIST_RAPIDO.md ....... (checklist express)
  ✅ GUIA_COMPLETA_TESTING.md .......... (guía detallada 200+ líneas)
  ✅ RESUMEN_VISUAL_TESTING.md ......... (diagramas ASCII)
  ✅ REFERENCE_TESTING.md .............. (cheatsheet rápida)

TUS RESPUESTAS:
  ✅ RESPUESTAS_TUS_3_PREGUNTAS.md ..... (directo de lo que preguntaste)

ÍNDICES:
  ✅ INDICE_TESTING_DOCS.md ............ (matriz de documentos)
  ✅ Este archivo ....................... (INDEX_FINAL.md)

ORIGINAL:
  ✅ GUIA_TESTING_BUG_A.md ............. (guía original completa)
```

---

## ⏱️ TIEMPO TOTAL

- **Test automático:** 2 minutos
- **Test manual rápido:** 5-10 minutos
- **Test completo:** 15-20 minutos

**Total máximo:** 20 minutos para tener TODO validado

---

## 🎓 ¿QUÉ SE TESTEA?

```
BUG-A FIX: Cuando se vende un producto con RECETA,
           los INGREDIENTES se descuentan automáticamente

ANTES (BUG):
  Producto stock ↓
  Ingredientes stock ❌ (sin cambio - MALO)

DESPUÉS (FIX):
  Producto stock ↓
  Ingredientes stock ↓ (disminuye - BUENO)
  Movimientos registrados ✅ (auditoría)
```

---

## 🔗 REFERENCIAS RÁPIDAS

**¿Cómo levanto server?**
→ `RESPUESTAS_TUS_3_PREGUNTAS.md` Pregunta 1

**¿Hay datos de prueba?**
→ `RESPUESTAS_TUS_3_PREGUNTAS.md` Pregunta 2

**¿Qué probar?**
→ `RESPUESTAS_TUS_3_PREGUNTAS.md` Pregunta 3

**¿Script automático?**
→ `python3 test_bug_a_fix.py`

**¿Manual paso a paso?**
→ `TESTING_RAPIDO.md`

**¿Guía completa?**
→ `GUIA_COMPLETA_TESTING.md`

**¿Tengo un error?**
→ `GUIA_COMPLETA_TESTING.md` sección "Troubleshooting"

---

## ✨ RESUMEN

| Qué | Cómo | Documento |
|-----|------|-----------|
| Responder preguntas | Leer | `RESPUESTAS_TUS_3_PREGUNTAS.md` |
| Test rápido | Ejecutar | `python3 test_bug_a_fix.py` |
| Test manual | Copy/paste | `TESTING_RAPIDO.md` |
| Entender todo | Leer | `GUIA_COMPLETA_TESTING.md` |
| Ver diagramas | Leer | `RESUMEN_VISUAL_TESTING.md` |
| Referencia | Consultar | `REFERENCE_TESTING.md` |

---

## 🎬 AHORA

1. Abre: `RESPUESTAS_TUS_3_PREGUNTAS.md`
2. Lee tus 3 respuestas
3. Elige un método (automático es lo más fácil)
4. Ejecuta tests
5. Si todo pasa → git commit
6. Continúa con BUG-B y BUG-C

---

**Creado:** 9 de abril de 2026  
**Para:** Lino Saludable  
**Objetivo:** Testing rápido y fácil del BUG-A fix  
**Estado:** ✅ Listo para usar
