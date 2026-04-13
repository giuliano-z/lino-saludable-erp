# 📋 REFERENCIA RÁPIDA: TESTING BUG-A FIX

## 🎯 Objetivo
Validar que al vender producto con receta, se descuentan automáticamente los ingredientes

## 🚀 Opción 1: AUTOMÁTICO (2 min)
```bash
# Terminal 1
cd src && python3 manage.py runserver

# Terminal 2
python3 test_bug_a_fix.py
# ✅ Deberías ver: "BUG-A FIX ESTÁ FUNCIONANDO"
```

## 🔧 Opción 2: MANUAL (10 min)
```bash
cd src && python3 manage.py shell
# Pega los bloques de TESTING_RAPIDO.md
```

## 📊 QUÉ VALIDAR

| Item | Valor Esperado | ¿Verificar? |
|------|----------------|-----------|
| Stock Producto | 10 → 8 (disminuyó 2) | ✅ `producto.refresh_from_db()` |
| Stock Harina | 100 → 96 (disminuyó 4) | ✅ `harina.refresh_from_db()` |
| Stock Aceite | 50 → 49 (disminuyó 1) | ✅ `aceite.refresh_from_db()` |
| Movimientos | count() > 0 | ✅ `MovimientoMateriaPrima.objects.filter(venta=v)` |

## 🔑 Puntos Críticos

```
✅ DEBE PASAR:
   1. Producto stock disminuye
   2. Ingredientes stock DISMINUYE (BUG-A FIX)
   3. Movimientos se registran en tabla de auditoría
   
❌ NO DEBE PASAR:
   1. Stock negativo
   2. Movimientos vacíos
   3. Error de validación sin motivo
```

## 📂 Archivos Relacionados

```
TESTING:
  • TESTING_RAPIDO.md ←─ EMPEZÁ AQUÍ (instrucciones paso a paso)
  • test_bug_a_fix.py ← Script automático
  • GUIA_COMPLETA_TESTING.md ← Guía detallada
  • RESUMEN_VISUAL_TESTING.md ← Diagramas y visualización

CÓDIGO MODIFICADO:
  • src/gestion/models.py líneas 654-804 (validación + descuento)
  • src/gestion/views.py línea 3260+ (integración en venta)
  • src/lino_saludable/settings.py líneas 14-21 (security)
```

## ⏰ Timeline

```
Minuto 0-2:   Levantar server + test
Minuto 2-5:   Ver resultados
Minuto 5-10:  Si falla, troubleshooting
Minuto 10+:   git commit
```

## 🎓 Conceptos Clave

```
ANTES (BUG):
  Venta de Brownies x2
  ├─ Stock Brownies: 10 → 8 ✅
  └─ Stock Ingredientes: SIN CAMBIO ❌

DESPUÉS (FIX):
  Venta de Brownies x2
  ├─ Stock Brownies: 10 → 8 ✅
  └─ Stock Ingredientes:
     ├─ Harina: 100 → 96 ✅
     └─ Aceite: 50 → 49 ✅
```

## 🔗 URLs útiles

```
Admin Django: http://localhost:8000/admin/
  • Productos: /admin/gestion/producto/
  • Movimientos: /admin/gestion/movimientomateriapprima/
```

## ✅ Cuando está OK

```bash
# Ver cambios
git diff

# Hacer commit
git add -A
git commit -m "PASO 1+2: Security + BUG-A fix (tested locally)"

# Siguiente paso: BUG-B y BUG-C
```

## 🆘 Quick Help

| Necesitas | Comando |
|-----------|---------|
| Ver stocks en shell | `modelo.refresh_from_db(); print(modelo.stock)` |
| Ver movimientos | `MovimientoMateriaPrima.objects.filter(venta=v).count()` |
| Aumentar stock test | `materia.stock_actual = 1000; materia.save()` |
| Crear usuario | `python3 manage.py createsuperuser` |
| Salir del shell | `exit()` |

---

**Próximos pasos después de validar BUG-A:**
1. BUG-B: Validar que `tiene_receta=True` requiere receta seleccionada
2. BUG-C: Remover decorator duplicado en línea 987
3. Backups automáticos
4. Commit final

**¿Dudas?** Ver `GUIA_COMPLETA_TESTING.md`
