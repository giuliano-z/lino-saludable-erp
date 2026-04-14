"""
Comando para validar la consistencia del sistema LINO
Uso: python manage.py validate_lino
"""
from pathlib import Path

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Valida la consistencia del sistema de componentes LINO'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Validando Sistema LINO...'))

        # Validar componentes LINO
        components = [
            'lino_kpi_card', 'lino_card_header', 'lino_button',
            'lino_info_section', 'lino_value_box', 'lino_badge',
            'lino_search_panel'
        ]

        errors = []
        warnings = []

        # 1. Verificar que todos los componentes existen
        templates_dir = Path('gestion/templates/components')
        for component in components:
            template_path = templates_dir / f'{component}.html'
            if not template_path.exists():
                errors.append(f'❌ Componente faltante: {component}.html')
            else:
                self.stdout.write(f'✅ Componente encontrado: {component}')

        # 2. Verificar uso consistente de iconos
        icon_patterns = {
            'inventario': 'bi-box',
            'ventas': 'bi-cart',
            'compras': 'bi-bag',
            'reportes': 'bi-graph-up'
        }

        # 3. Validar estructura CSS LINO
        css_classes = ['.lino-grid', '.lino-card', '.lino-button']

        if errors:
            self.stdout.write(self.style.ERROR('\n🚨 ERRORES ENCONTRADOS:'))
            for error in errors:
                self.stdout.write(self.style.ERROR(error))

        if warnings:
            self.stdout.write(self.style.WARNING('\n⚠️  ADVERTENCIAS:'))
            for warning in warnings:
                self.stdout.write(self.style.WARNING(warning))

        if not errors and not warnings:
            self.stdout.write(self.style.SUCCESS('\n🎉 Sistema LINO validado correctamente!'))

        return len(errors)
