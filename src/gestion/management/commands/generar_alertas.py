"""
Management Command: generar_alertas
Genera alertas automáticas para todos los usuarios del sistema
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from gestion.services.alertas_service import AlertasService

User = get_user_model()


class Command(BaseCommand):
    help = 'Genera alertas automáticas para usuarios del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            help='Username específico (opcional). Si no se especifica, genera para todos los usuarios.',
        )

        parser.add_argument(
            '--tipo',
            type=str,
            choices=['stock', 'vencimiento', 'rentabilidad', 'stock_muerto', 'oportunidades', 'todas'],
            default='todas',
            help='Tipo de alertas a generar (default: todas)',
        )

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada',
        )

    def handle(self, *args, **options):
        username = options.get('usuario')
        tipo = options.get('tipo')
        verbose = options.get('verbose')

        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("  LINO - Generador de Alertas Automáticas"))
        self.stdout.write("="*60 + "\n")

        # Obtener usuarios
        if username:
            try:
                usuarios = [User.objects.get(username=username)]
                self.stdout.write(f"👤 Usuario: {username}")
            except User.DoesNotExist:
                raise CommandError(f'Usuario "{username}" no encontrado')
        else:
            usuarios = User.objects.filter(is_active=True)
            self.stdout.write(f"👥 Generando para {usuarios.count()} usuarios activos")

        self.stdout.write(f"📋 Tipo de alertas: {tipo}\n")

        # Generar alertas
        service = AlertasService()
        total_generadas = 0

        for usuario in usuarios:
            if verbose:
                self.stdout.write(f"\nProcesando: {usuario.username}")

            try:
                if tipo == 'todas':
                    resultado = service.generar_todas_alertas(usuario)
                    alertas_generadas = sum(resultado.values())

                    if verbose:
                        for tipo_alerta, count in resultado.items():
                            if count > 0:
                                self.stdout.write(f"  • {tipo_alerta}: {count} alertas")

                elif tipo == 'stock':
                    alertas_generadas = service.generar_alertas_stock(usuario)
                elif tipo == 'vencimiento':
                    alertas_generadas = service.generar_alertas_vencimiento(usuario)
                elif tipo == 'rentabilidad':
                    alertas_generadas = service.generar_alertas_rentabilidad(usuario)
                elif tipo == 'stock_muerto':
                    alertas_generadas = service.generar_alertas_stock_muerto(usuario)
                elif tipo == 'oportunidades':
                    alertas_generadas = service.generar_alertas_oportunidades(usuario)
                else:
                    alertas_generadas = 0

                total_generadas += alertas_generadas

                if not verbose and alertas_generadas > 0:
                    self.stdout.write(self.style.SUCCESS(f"✓ {usuario.username}: {alertas_generadas} alertas generadas"))

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Error procesando {usuario.username}: {str(e)}")
                )

        # Resumen final
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("  ✅ Proceso completado"))
        self.stdout.write("="*60)
        self.stdout.write(f"📊 Total de alertas generadas: {total_generadas}")
        self.stdout.write(f"👥 Usuarios procesados: {len(usuarios)}\n")

        if total_generadas == 0:
            self.stdout.write(self.style.WARNING("💡 No se generaron alertas nuevas (puede que ya existan o no haya condiciones que las activen)"))
        else:
            self.stdout.write(self.style.SUCCESS("🎉 ¡Alertas generadas exitosamente!"))

        self.stdout.write("")
