# ⚡ QUICK REFERENCE - Testing Commands

## 🚀 Run Tests

### Full Test Suite
```bash
cd src/
python manage.py test gestion.tests -v 0
```
**Output:** `Ran 55 tests in 7.754s - OK` ✅

### Test by Module
```bash
python manage.py test gestion.tests.test_forms -v 2
python manage.py test gestion.tests.test_ventas -v 2
python manage.py test gestion.tests.test_compras -v 2
python manage.py test gestion.tests.test_templates_urls -v 2
python manage.py test gestion.tests.test_recetas -v 2
```

### Single Test Class
```bash
python manage.py test gestion.tests.test_forms.TestVentaForm -v 2
python manage.py test gestion.tests.test_ventas.TestCrearVentaView -v 2
python manage.py test gestion.tests.test_compras.TestCrearCompraView -v 2
```

### Single Test Method
```bash
python manage.py test gestion.tests.test_forms.TestVentaDetalleForm.test_cantidad_cero_rechazada -v 2
python manage.py test gestion.tests.test_ventas.TestCrearVentaView.test_post_crear_venta_valida_guarda -v 2
python manage.py test gestion.tests.test_compras.TestEliminarCompraView.test_post_eliminar_compra_reversión_restaura_stock -v 2
```

---

## 📊 Verbosity Levels

```bash
-v 0  # Minimal output (only final result)
-v 1  # Normal output (progress dots)
-v 2  # Verbose (test names + status)
-v 3  # Very verbose (includes setup/teardown)
```

---

## ✅ Test Status

### All Tests Passing
```
test_forms.py ..................... 17/17 ✅
test_ventas.py .................... 13/13 ✅
test_compras.py ................... 8/8 ✅
test_templates_urls.py ............ 10/10 ✅
test_recetas.py ................... 7/7 ✅
─────────────────────────────────────────
TOTAL ............................ 55/55 ✅
```

---

## 🔍 Debug Individual Tests

### Run Test with Print Statements
```bash
python -m pytest gestion/tests/test_forms.py::TestVentaDetalleForm::test_cantidad_cero_rechazada -s
```

### Run Test with Pdb Debugger
```bash
python -m pytest gestion/tests/test_forms.py -k "cantidad_cero" --pdb
```

### Run Tests with Coverage
```bash
pip install coverage
coverage run --source='gestion' manage.py test gestion.tests
coverage report
coverage html
```

---

## 📋 Common Test Patterns

### Test Setup/Teardown
```python
class MyTest(TestCase):
    def setUp(self):
        """Run before each test."""
        self.user = UserFactory.create_user_autenticado()
    
    def tearDown(self):
        """Run after each test (automatic)."""
        # Database automatically rolled back
```

### Factory Usage
```python
# Create test user with permissions
user = UserFactory.create_user_autenticado()
# Create test materia prima
mp = MateriaPrimaFactory.create_mp(stock=10, costo=100)
# Create venta with stock decrement
venta = VentaFactory.create_venta_con_detalle(user=user)
# Create compra with stock increment
compra = CompraFactory.create_compra(mp, cantidad=5, precio=50)
```

### Common Assertions
```python
# HTTP Status
self.assertEqual(response.status_code, 200)
self.assertEqual(response.status_code, 302)  # Redirect

# Database
obj.refresh_from_db()
self.assertEqual(obj.stock, 15)

# Model Relations
self.assertEqual(venta.detalles.count(), 1)

# Redirects
self.assertRedirects(response, '/expected/url/')

# Template
self.assertTemplateUsed(response, 'template.html')
```

---

## 🐛 Troubleshooting

### Test Fails: "User not found"
```python
# Make sure to create user before using client.login()
self.user = UserFactory.create_user_autenticado()
self.client.login(username='testuser', password='testpass123')
```

### Test Fails: "Permission denied"
```python
# Check user has correct permissions
from django.contrib.auth.models import Permission
perms = user.user_permissions.all()
# Or use factory:
user = UserFactory.create_user_autenticado()  # Has perms
```

### Test Fails: "Stock mismatch"
```python
# Always refresh_from_db() after operations
obj.refresh_from_db()
self.assertEqual(obj.stock_actual, expected_value)
```

### Test Fails: "Template not found"
```python
# Check template path in test
self.assertTemplateUsed(response, 'gestion/template.html')
# Or check if template variable exists
self.assertContains(response, 'expected_text')
```

---

## 📈 Best Practices

### Do ✅
```python
# Specific assertions
self.assertEqual(venta.total, Decimal('100.00'))

# Use factories for test data
mp = MateriaPrimaFactory.create_mp()

# Refresh after operations
venta.refresh_from_db()

# Test one thing per test
def test_cantidad_zero_rejected(self):
    # Only test quantity validation
```

### Don't ❌
```python
# Vague assertions
self.assertTrue(venta)

# Hardcoded test data
mp = MateriaPrima.objects.create(nombre='MP')

# Multiple assertions mixing concerns
def test_venta_flow(self):
    # Tests 5 different things
```

---

## 🎯 Test Coverage Goals

**Current Status:**
- Forms: 100% ✅
- Views: ~85% ✅
- Models: ~70% ⚠️ (implicit via views)
- Integration: 80% ✅

**To Improve:**
- Add model validation tests
- Add edge case tests
- Add performance tests

---

## 📝 Report Generation

### Test Results
```bash
python manage.py test gestion.tests --verbosity=2 > test_results.txt
```

### Coverage Report
```bash
coverage report > coverage_report.txt
coverage html  # Generates htmlcov/index.html
```

---

## 🔗 Related Files

```
/gestion/tests/
├── conftest.py           # Fixtures & factories
├── test_forms.py         # 17 form validation tests
├── test_ventas.py        # 13 sales workflow tests
├── test_compras.py       # 8 purchase workflow tests
├── test_templates_urls.py # 10 integration tests
└── test_recetas.py       # 7 recipe tests

Documentation:
├── TESTING_STATUS_FINAL.md
├── FINAL_TESTING_FIXES.md
├── RESUMEN_FINAL_TESTING.md
└── QUICK_REFERENCE_TESTING.md (this file)
```

---

## ⏱️ Typical Test Times

| Module | Count | Time |
|--------|-------|------|
| test_forms.py | 17 | ~0.5s |
| test_ventas.py | 13 | ~2.5s |
| test_compras.py | 8 | ~2.0s |
| test_templates_urls.py | 10 | ~1.5s |
| test_recetas.py | 7 | ~1.3s |
| **TOTAL** | **55** | **~7.8s** |

---

## 📞 Support

**Issue:** Tests failing?
1. Check `python manage.py test gestion.tests -v 2`
2. Review error message carefully
3. Check `FINAL_TESTING_FIXES.md` for common fixes
4. Run single test: `python manage.py test gestion.tests.MODULE.CLASS.METHOD -v 2`

**Issue:** Can't run tests?
1. Ensure in `src/` directory
2. Check venv is active: `source venv/bin/activate`
3. Check dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`

---

**Last Updated:** 2026-04-13 02:39:48 UTC
