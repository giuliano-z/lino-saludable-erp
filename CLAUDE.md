# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ ADVERTENCIA CRÍTICA: ESTO ES PRODUCCIÓN REAL

**Cualquier push a `main` se despliega automáticamente en Railway (producción).**

- La base de datos PostgreSQL tiene 1800+ transacciones reales de clientes reales.
- No hay entorno de staging — local (SQLite) y producción (PostgreSQL) son los únicos entornos.
- Antes de cualquier operación que afecte datos o despliegue, confirmar explícitamente con el usuario.
- **NUNCA** hacer `git push` sin pedir confirmación explícita al usuario.
- **NUNCA** correr formatters (`ruff --fix`, `black`, `isort`) automáticamente sin avisar — generan decenas de cambios de formato que ensucian el historial git.

## Project Overview

Lino Saludable is a Django-based business management system for a nuts and healthy products shop. It tracks sales, purchases, inventory, raw materials, recipes, and profitability. The production database has 1800+ transactions on Railway (PostgreSQL); local development uses SQLite.

## Development Commands

All Django commands must be run from `src/`:

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then configure

# Development server
cd src && python manage.py runserver

# Migrations
cd src && python manage.py migrate
cd src && python manage.py makemigrations

# Load sample data
cd src && python manage.py cargar_ejemplo_simple

# Static files (production)
cd src && python manage.py collectstatic
```

## Running Tests

pytest is configured from the project root. `conftest.py` and `pytest.ini` set `pythonpath = src` and `testpaths = tests_e2e`, but unit tests live in `src/gestion/tests/`.

```bash
# Run all tests
pytest

# Run unit tests only
pytest src/gestion/tests/

# Run a single test file
pytest src/gestion/tests/test_ventas.py

# Run a single test
pytest src/gestion/tests/test_ventas.py::TestVenta::test_crear_venta

# Run by marker
pytest -m smoke
pytest -m "not e2e"

# E2E tests (requires Playwright)
pytest tests_e2e/ -m e2e
```

Available markers: `e2e`, `slow`, `critical`, `smoke`.

## Architecture

### App Structure

The single Django app `gestion` (in `src/gestion/`) contains all business logic. Views are split into topic files to keep them manageable:

- [views.py](src/gestion/views.py) — dashboard, reports, alerts, inventory adjustments, API endpoints
- [views_ventas.py](src/gestion/views_ventas.py) — sales CRUD
- [views_compras.py](src/gestion/views_compras.py) — purchase CRUD
- [views_productos.py](src/gestion/views_productos.py) — products and raw materials
- [views_recetas.py](src/gestion/views_recetas.py) — recipe management

Business logic that does not belong in views goes into [services/](src/gestion/services/): `alertas_service.py`, `analytics_service.py`, `dashboard_service.py`, `inventario_service.py`, `marketing_service.py`, `rentabilidad_service.py`.

### Key Architectural Patterns

**Soft Delete**: Records are never hard-deleted. The `Venta` model uses an `eliminada` boolean flag with audit fields (`razon_eliminacion`, `usuario_eliminacion`, `fecha_eliminacion`). `VentaActivaManager` is the default manager (filters out deleted records); `VentaManager` exposes all records. Always use the correct manager when querying.

**Signals are mostly disabled**: [signals.py](src/gestion/signals.py) contains signal handlers that were turned off to prevent duplicate operations. Read the comments in that file before enabling any signal.

**Alert system**: Seven alert types (`stock_agotado`, `stock_critico`, `vencimiento`, `margen_negativo`, `margen_bajo`, `stock_muerto`, `oportunidad_venta`) with severity levels (`danger`, `warning`, `success`, `info`). Generation is handled by `alertas_service.py` and the `generar_alertas` management command.

**API layer**: Simple JSON endpoints at `/api/productos/`, `/api/inventario/`, `/api/ventas/` for AJAX calls. Defined in [api.py](src/gestion/api.py).

### Database

- **Local**: SQLite (`src/db.sqlite3`) — selected automatically when `DATABASE_URL` is absent.
- **Production**: PostgreSQL on Railway via `DATABASE_URL` env var (`dj-database-url` handles parsing). Connection pool: `conn_max_age=600` with health checks.
- Indexes are defined on frequently queried fields (`fecha`, `eliminada`, `usuario` on sales).

### Settings

- [settings.py](src/lino_saludable/settings.py) — used for both local and production; detects environment via env vars.
- [settings_production.py](src/lino_saludable/settings_production.py) — production overrides.
- Security headers (HSTS, CSP, X-Frame-Options) and django-axes rate limiting (5 failures/1 hr) are active in production. In development, axes is configured but Redis is not required.

### Deployment (Railway)

Defined in [railway.toml](railway.toml). Start sequence: `migrate` → `createusers` → `resetpasswords` → `gunicorn` (2 workers, 60 s timeout). A daily cron at 3 AM UTC runs `backup_db`, which dumps data and optionally emails the backup.

### CI/CD

[.github/workflows/django_ci.yml](.github/workflows/django_ci.yml) runs on push/PR to `main`/`develop`: installs deps, runs migrations, then `pytest`.

## Environment Variables

See `.env.example` for the full list. Required for production: `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`. Optional: `EMAIL_*` (SMTP), `REDIS_URL`.

## Trabajo Pendiente (en curso)

### Mejoras al sistema de backups — iniciado en sesión abril 2026
Archivo: [backup_db.py](src/gestion/management/commands/backup_db.py)

Cambios acordados pero **aún no implementados ni commiteados**:
1. Reemplazar email hardcodeado por variable de entorno `BACKUP_EMAIL_RECIPIENT`
2. Agregar `import logging` y `logger = logging.getLogger(__name__)`
3. Agregar validación clara si el email no está configurado
4. Agregar logs en 5 puntos clave: inicio, export, compress, send, cleanup
5. Agregar `settings.py` → variable `BACKUP_EMAIL_RECIPIENT = os.getenv("BACKUP_EMAIL_RECIPIENT", "")`
6. Documentar nueva variable en `.env.example`

Estado: los archivos del proyecto tienen ~60 archivos con cambios de formato (ruff) sin commitear. Resolver eso antes de implementar las mejoras de backup.

## Qué NO hacer

- **No correr `ruff --fix`, `black`, ni `isort` automáticamente** — si hay que formatear, avisar primero y hacerlo en un commit separado dedicado solo a formato.
- **No crear migraciones sin mostrarlas completas primero** — siempre mostrar el archivo generado antes de aplicarlo.
- **No hacer `git push` sin confirmación explícita** — cada push despliega en producción.
- **No modificar `signals.py`** sin leer los comentarios del archivo — los signals están desactivados intencionalmente para evitar duplicados.
- **No usar `python manage.py flush`** — destruye todos los datos de producción.
- **No instalar dependencias nuevas** sin avisar primero al usuario.
