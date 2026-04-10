# conftest.py - Configuración global de pytest
import pytest
from pytest_django.live_server_helper import LiveServer

@pytest.fixture(scope="session")
def django_db_setup():
    """Configurar base de datos para tests."""
    pass

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Habilitar acceso a base de datos automáticamente para todos los tests.
    Esto evita RuntimeError: Database access not allowed.
    """
    pass

@pytest.fixture(scope="session") 
def live_server(request):
    """Servidor de desarrollo para tests E2E."""
    server = LiveServer("127.0.0.1:8001")
    request.addfinalizer(server.stop)
    return server
