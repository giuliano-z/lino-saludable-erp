# 🧪 PLAN DE TESTING COMPLETO - lino_saludable

**Fecha:** 12 de Abril de 2026  
**Objetivo:** Crear suite de tests que detecte inconsistencias automáticamente

---

## 📐 ESTRUCTURA DE TESTING PROPUESTA

```
gestion/tests/
├── __init__.py
├── conftest.py                    # Fixtures compartidas (pytest)
├── factories.py                   # Factories para crear datos de test
├── test_ventas.py                 # ✅ Tests flujo de ventas
├── test_compras.py                # ✅ Tests flujo de compras
├── test_productos_recetas.py      # ✅ Tests productos y recetas
├── test_forms.py                  # ✅ Tests de formularios
├── test_templates_urls.py         # ✅ Tests de templates e URLs
└── test_views_integration.py      # ✅ Tests de integración completos
```

### Archivos Existentes a Reemplazar:
- `gestion/tests/test_flow.py` → Migrará a estructura modular
- `gestion/tests.py` → Se puede eliminar o consolidar

---

## 🎯 COBERTURA DE TESTS POR ÁREA

### 1️⃣ **test_ventas.py** - Flujo Completo de Ventas

```python
✅ TestCrearVentaView
   └─ test_get_crear_venta_anónimo → Redirige a login
   └─ test_get_crear_venta_autenticado → Carga formulario
   └─ test_post_crear_venta_válida → Guarda venta + detalles + descuenta stock
   └─ test_post_crear_venta_sin_stock → Rechaza con mensaje
   └─ test_post_crear_venta_fecha_inválida → Valida fecha servidor
   └─ test_post_crear_venta_cantidad_inválida → Rechaza cantidad ≤ 0
   └─ test_post_crear_venta_producto_nulo → Rechaza producto sin asociar

✅ TestEliminarVentaView
   └─ test_soft_delete_restaura_stock → Venta marcada + stock restaurado
   └─ test_eliminar_sin_permisos → Rechaza usuario sin permisos

✅ TestDetalleVentaView
   └─ test_detalle_venta_existe → Carga correctamente
   └─ test_detalle_venta_inexistente → 404 Not Found

✅ TestExportarVentasView
   └─ test_export_xlsx_valido → Descarga archivo válido

✅ TestCrearVentaConMateriasView
   └─ test_vista_desactivada_redirige → Redirige a crear_venta
   └─ test_loguea_intento_acceso → Se registra en LinoLogger
```

### 2️⃣ **test_compras.py** - Flujo Completo de Compras

```python
✅ TestCrearCompraView
   └─ test_get_crear_compra_autenticado → Carga formulario
   └─ test_post_crear_compra_válida → Guarda + actualiza stock MP
   └─ test_post_crear_compra_cantidad_inválida → Rechaza
   └─ test_compra_actualiza_costo_unitario → FIFO calcula correcto

✅ TestDetalleCompraView
   └─ test_detalle_compra_existe → Carga correctamente

✅ TestEliminarCompraView
   └─ test_eliminar_compra_reversión → Stock restaurado correctamente
   └─ test_eliminar_compra_recalcula_costo → Promedio ponderado correcto
```

### 3️⃣ **test_productos_recetas.py** - Productos y Recetas

```python
✅ TestListaProductosView
   └─ test_lista_productos_cargada → Pagina 25 items por página
   └─ test_filtro_por_nombre → Busca productos correctamente
   └─ test_kpis_calculados → KPIs no están vacíos

✅ TestCrearProductoView
   └─ test_crear_producto_válido → Se guarda correctamente
   └─ test_crear_producto_con_receta → Asocia receta

✅ TestListaRecetasView
   └─ test_lista_recetas_cargada → Recetas paginadas

✅ TestCrearRecetaView
   └─ test_crear_receta_con_ingredientes → Se guarda con detalles
   └─ test_procesar_ingredientes_json → Valida JSON correctamente
```

### 4️⃣ **test_forms.py** - Integridad de Formularios

```python
✅ TestVentaForm
   └─ test_fecha_requerida → Campo fecha es obligatorio
   └─ test_fecha_formato_válido → Acepta ISO format
   └─ test_fecha_formato_inválido → Rechaza formato incorrecto
   └─ test_cliente_opcional → Cliente puede estar vacío
   └─ test_form_valido_con_datos_mínimos → Solo cliente+fecha

✅ TestVentaDetalleForm
   └─ test_queryset_solo_con_stock → Solo productos con stock > 0
   └─ test_cantidad_mayor_a_stock → clean() rechaza
   └─ test_cantidad_menor_a_cero → Rechaza cantidad ≤ 0
   └─ test_precio_unitario_opcional → Si no hay, usa precio del producto

✅ TestVentaDetalleFormSet
   └─ test_formset_extra_1 → Trae 1 form vacío para agregar
   └─ test_formset_válido → Valida múltiples productos

✅ TestCompraForm
   └─ test_cantidad_requerida → No puede estar vacía
   └─ test_precio_requerido → No puede estar vacío
   └─ test_materia_prima_existente → Solo MP existentes
```

### 5️⃣ **test_templates_urls.py** - Templates e URLs

```python
✅ TestTemplatesExisten
   └─ test_template_form_v3_natural_existe → Archivo existe
   └─ test_template_lista_ventas_existe → Archivo existe
   └─ test_template_lista_compras_existe → Archivo existe
   └─ test_no_template_formulario_html → Archivo NO existe (se evita)

✅ TestURLsResuelven
   └─ test_url_crear_venta_resuelve → Reverse name 'crear_venta'
   └─ test_url_lista_ventas_resuelve → Reverse name 'lista_ventas'
   └─ test_url_crear_compra_resuelve → Reverse name 'crear_compra'
   └─ test_no_url_lista_compras_migrado → URL legacy no existe

✅ TestReferenciasMigradas
   └─ test_no_referencias_migrado_en_templates → grep _migrado = 0
   └─ test_no_referencias_migrado_en_urls → grep _migrado = 0
   └─ test_no_referencias_migrado_en_views → grep _migrado = 0
```

### 6️⃣ **test_views_integration.py** - Integración Completa

```python
✅ TestFlujoCar completo
   └─ test_flujo_compra_venta_completo →
       1. Crear MP
       2. Comprar MP
       3. Crear producto con MP
       4. Vender producto
       5. Verificar stocks finales

✅ TestTransacciones
   └─ test_crear_venta_rollback_si_error → Transaction.atomic() funciona
   └─ test_crear_compra_rollback_si_error → Sin datos corruptos

✅ TestPermisos
   └─ test_usuario_sin_permisos_rechazado → @login_required funciona
   └─ test_has_perm_validado → Permisos específicos

✅ TestErrorHandling
   └─ test_producto_inexistente_404 → get_object_or_404
   └─ test_venta_inexistente_404 → get_object_or_404
```

---

## 🔧 FACTORIES.PY - Datos de Test

```python
# Fixtures reutilizables para NO escribir setUp 10 veces

class UserFactory:
    → create_user_autenticado()
    → create_user_sin_permisos()

class MateriaPrimaFactory:
    → create_mp(stock=10, costo=100)
    → create_mp_sin_stock()

class ProductoFactory:
    → create_producto(stock=5, precio=100)
    → create_producto_con_receta()
    → create_producto_sin_stock()

class VentaFactory:
    → create_venta(cliente="Test")
    → create_venta_con_detalle(cantidad=2)

class CompraFactory:
    → create_compra(cantidad=10)
```

---

## 📊 MATRIZ DE COBERTURA

| Área | Test Count | Criticidad | Status |
|------|-----------|-----------|--------|
| Ventas (vista + form) | 12 | 🔴 CRÍTICO | ⏳ POR HACER |
| Compras (vista + form) | 8 | 🔴 CRÍTICO | ⏳ POR HACER |
| Productos/Recetas | 8 | 🟠 ALTO | ⏳ POR HACER |
| Forms (validación) | 14 | 🟠 ALTO | ⏳ POR HACER |
| Templates/URLs | 10 | 🟠 ALTO | ⏳ POR HACER |
| Integración | 8 | 🟡 MEDIO | ⏳ POR HACER |
| **TOTAL** | **60+** | | ⏳ |

---

## 🎯 REGLAS DE TESTING

1. **SIN Humo:** Cada test verifica algo concreto
   - ❌ `test_venta()` - muy vago
   - ✅ `test_post_crear_venta_válida_descuenta_stock()` - específico

2. **Datos Aislados:** Cada test es independiente
   - Usar `setUp()` para datos compartidos
   - Usar factories para datos específicos

3. **Excepciones Claras:** Si algo está roto, falla
   - ❌ `self.assertTrue(venta)` - no dice nada
   - ✅ `self.assertEqual(venta.total, Decimal('200'))` - claro

4. **Coverage:** Apuntar a 80%+ de cobertura
   - `pytest --cov=gestion --cov-report=html`

5. **Velocidad:** Tests deben correr en < 5 segundos
   - Usar `TestCase` para DB (Django transaction rollback)
   - Usar fixtures cuando sea posible

---

## 🚀 EJECUCIÓN DE TESTS

```bash
# Todos los tests
pytest gestion/tests/ -v

# Solo ventas
pytest gestion/tests/test_ventas.py -v

# Con coverage
pytest gestion/tests/ --cov=gestion --cov-report=html

# Solo tests que fallen (TDD)
pytest gestion/tests/ -x -v

# Con output detallado
pytest gestion/tests/ -vv --tb=short
```

---

## 📝 PENDIENTES DE DECISIÓN

1. **¿pytest o unittest?**
   - Propuesta: pytest (más moderno, mejor fixtures)
   - Requiere: `pytest-django`, `pytest-cov`

2. **¿Live Server Tests?**
   - Propuesta: NO (lentos, innecesarios con TestCase)
   - Usar: `Client()` de Django para simular requests

3. **¿Fixture Database?**
   - Propuesta: Usar Django fixtures para datos iniciales
   - O: Factories para datos dinámicos

4. **¿Mocks?**
   - Propuesta: Minimal
   - Solo mockear: Servicios externos (Email, APIs)
   - NO mockear: Models, Forms, Views internas

---

## ✅ BENEFICIOS DE ESTA SUITE

- ✅ **Detección automática:** Se ejecuta en CI/CD
- ✅ **Regresión:** Cambios futuros no rompen nada
- ✅ **Documentación:** Tests = ejemplos de uso
- ✅ **Confianza:** 60+ tests = bajo riesgo
- ✅ **Velocidad:** Feedback inmediato (~5 seg)

---

## 🔄 PRÓXIMAS FASES

**Fase 1 (ESTA):** Crear estructura + test_ventas.py + test_compras.py  
**Fase 2:** test_productos_recetas.py + test_forms.py  
**Fase 3:** test_templates_urls.py + factories.py  
**Fase 4:** test_views_integration.py + Coverage report  
**Fase 5:** CI/CD integration (GitHub Actions)

---

**Plan Propuesto:** ✅ COMPLETO  
**¿Proceder con implementación?** PENDIENTE CONFIRMACIÓN
