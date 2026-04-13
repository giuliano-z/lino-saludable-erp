"""
Suite de tests automatizados para lino_saludable.

Estructura:
- factories.py: Factories para crear datos de test reutilizables
- test_ventas.py: Tests del flujo de ventas (crear, eliminar, detalle)
- test_compras.py: Tests del flujo de compras (crear, eliminar, detalle)
- test_forms.py: Tests de formularios y validaciones
- test_templates_urls.py: Tests de templates e URLs (existencia, resolución)
- test_views_integration.py: Tests de integración completa (futuro)

Ejecutar tests:
    # Todos los tests
    pytest gestion/tests/ -v
    
    # Solo ventas
    pytest gestion/tests/test_ventas.py -v
    
    # Con coverage
    pytest gestion/tests/ --cov=gestion --cov-report=html
    
    # Para fallar en el primer error (TDD)
    pytest gestion/tests/ -x -v

Cobertura esperada: 80%+ de las vistas y modelos críticos
"""
