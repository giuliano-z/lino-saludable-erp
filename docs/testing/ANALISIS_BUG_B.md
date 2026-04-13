# 🔍 ANÁLISIS DETALLADO: BUG-B

## Problema Identificado

Cuando un usuario marca `tiene_receta=True` en el formulario de crear/editar producto, pero **NO selecciona una receta**, el producto se guarda sin validación clara, generando inconsistencias.

---

## 📍 UBICACIÓN DEL BUG

### En el Formulario (forms.py)
**Ubicación:** `src/gestion/forms.py` líneas 253-255

```python
elif tipo_producto == 'receta':
    # Para recetas, validar que tenga receta asociada
    if cleaned_data.get('tiene_receta') and not cleaned_data.get('receta'):
        raise forms.ValidationError('Para productos con receta debe seleccionar una receta')
```

**Problema:** La validación SOLO ocurre si `tipo_producto == 'receta'`

**¿Dónde falla?**
1. Si usuario marca `tiene_receta=True` pero elige `tipo_producto='reventa'` o `'fraccionamiento'`
2. No se valida que tenga una receta seleccionada
3. El producto se guarda inconsistente

### En el Modelo (models.py)
**Ubicación:** `src/gestion/models.py` línea 358

```python
tiene_receta = models.BooleanField(
    default=False, 
    verbose_name='¿Usa receta?', 
    help_text='Marcar si el producto se produce a partir de una receta'
)
```

**Problema:** Campo booleano sin validador que garantice que si es `True`, `receta` no puede ser `None`

---

## 🎯 IMPACTO DEL BUG

### Escenario de Error

1. Usuario abre formulario crear producto
2. Completa datos básicos
3. Marca checkbox `¿Usa receta?` = True
4. PERO no selecciona una receta (dropdown vacío)
5. Envía formulario
6. Producto se crea o actualiza SIN receta

### Consecuencias

| Aspecto | Consecuencia |
|--------|---|
| **Data Consistency** | Campo `tiene_receta=True` pero `receta=None` - Inconsistente |
| **Stock Management** | Si se vende, no hay ingredientes para descontar (aunque esté marcado) |
| **Reporting** | Reportes de productos con receta incluyen productos sin receta |
| **Business Logic** | Contradicción: "usa receta" pero "sin receta asignada" |

---

## 🔧 SOLUCIÓN PROPUESTA

### Opción A: REFORZAR VALIDACIÓN EN FORMULARIO (Recomendado)

**Dónde:** `src/gestion/forms.py` método `clean()`

**Cambio:** Agregar validación adicional que sea INDEPENDIENTE del `tipo_producto`

```python
def clean(self):
    cleaned_data = super().clean()
    
    # ... código existente ...
    
    # 🛡️ BUG-B FIX: Validación de tiene_receta
    # IMPORTANTE: Esta validación es INDEPENDIENTE del tipo_producto
    # Si el usuario marca "tiene_receta=True", DEBE seleccionar una receta
    if cleaned_data.get('tiene_receta'):
        if not cleaned_data.get('receta'):
            raise forms.ValidationError(
                '❌ Si marca "¿Usa receta?" debe seleccionar una receta en el campo "Receta"'
            )
    
    return cleaned_data
```

**Ubicación exacta:** Línea ~217 (ANTES de las validaciones por tipo_producto)

### Opción B: AGREGAR VALIDADOR EN MODELO

**Dónde:** `src/gestion/models.py` método `clean()` en clase `Producto`

```python
def clean(self):
    # 🛡️ BUG-B FIX: Validación de tiene_receta
    if self.tiene_receta and not self.receta:
        raise ValidationError(
            'Si marca "¿Usa receta?" debe seleccionar una receta'
        )
```

---

## 📋 CHECKLIST: VALIDACIONES A CUBRIR

```
VALIDACIÓN ACTUAL (formulario, línea 253-255):
  ✅ Si tipo_producto='receta' → requiere receta

VALIDACIÓN FALTANTE (BUG-B):
  ❌ Si tiene_receta=True → requiere receta (SIN importar tipo_producto)

CASOS A VALIDAR:

Caso 1: tiene_receta=False, receta=None
  ✅ PERMITIDO (sin receta, sin marcar)

Caso 2: tiene_receta=True, receta=None
  ❌ RECHAZADO (marcó receta pero no seleccionó)

Caso 3: tiene_receta=True, receta=<válido>
  ✅ PERMITIDO (marcó receta y seleccionó)

Caso 4: tiene_receta=False, receta=<válido>
  ⚠️ ADVERTENCIA (tiene receta pero no marcó - inconsistencia)
```

---

## 🔍 CÓMO REPRODUCIR EL BUG

### Paso 1: Abrir formulario crear producto
```
GET http://localhost:8000/gestion/productos/crear/
```

### Paso 2: Rellenar con estos valores
```
Nombre: Producto Test
Categoría: dietetica
Tipo Producto: reventa  ← IMPORTANTE: No 'receta'
Precio Base: 100.00
Stock: 5
¿Usa receta?: TRUE ← MARCA EL CHECKBOX
Receta: (dejar vacío) ← NO SELECCIONA NADA
```

### Paso 3: Enviar formulario
```
Resultado actual: ❌ Producto se crea con tiene_receta=True, receta=None
Resultado esperado: ✅ Error: "Debe seleccionar una receta"
```

---

## 🛠️ IMPLEMENTACIÓN DEL FIX

### Archivo a modificar
```
src/gestion/forms.py
```

### Línea exacta
```
~217 (en el método clean() de ProductoForm)
```

### Código a agregar
```python
# 🛡️ BUG-B FIX: Validación que tiene_receta requiere receta
# Esta validación es INDEPENDIENTE del tipo_producto
if cleaned_data.get('tiene_receta'):
    if not cleaned_data.get('receta'):
        raise forms.ValidationError(
            '❌ Si marca "¿Usa receta?" debe seleccionar una receta'
        )
```

### Dónde exactamente
```
En el método clean(), ANTES de las validaciones por tipo_producto
(aproximadamente línea 217)
```

---

## ✅ VALIDACIÓN POST-FIX

### Test Manual 1: Con receta
```
Nombre: Brownies
tiene_receta: True
receta: Brownies Almendra
→ DEBE PASAR ✅
```

### Test Manual 2: Sin receta (BUG-B)
```
Nombre: Producto Test
tiene_receta: True
receta: (vacío)
→ DEBE FALLAR CON ERROR ✅
```

### Test Manual 3: Sin marcar
```
Nombre: Reventa Test
tiene_receta: False
receta: (vacío)
→ DEBE PASAR ✅
```

---

## 🎯 RESUMEN

| Aspecto | Detalle |
|--------|---------|
| **Archivo** | `src/gestion/forms.py` |
| **Método** | `ProductoForm.clean()` |
| **Línea** | ~217 |
| **Cambio** | Agregar validación tiene_receta → requiere receta |
| **Tipo** | Validación de negocio |
| **Severidad** | MEDIA (previene inconsistencias) |
| **Impacto** | Asegura data consistency |

---

## 🔗 RELACIÓN CON OTROS BUGS

```
BUG-A (COMPLETO): Stock de ingredientes no se descuenta
BUG-B (EN PROGRESO): tiene_receta=True sin receta seleccionada
BUG-C (PENDIENTE): Decorator duplicado

Relación: BUG-B hace más robusta la validación que BUG-A necesita
```
