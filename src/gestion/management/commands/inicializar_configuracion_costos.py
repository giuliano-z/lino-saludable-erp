from django.core.management.base import BaseCommand

from gestion.models import ConfiguracionCostos


class Command(BaseCommand):
    help = 'Inicializa la configuración de costos con valores predeterminados'

    def handle(self, *args, **options):
        # Verificar si ya existe una configuración
        if ConfiguracionCostos.objects.exists():
            self.stdout.write(
                self.style.WARNING('Ya existe una configuración de costos. No se creó una nueva.')
            )
            return

        # Crear configuración inicial
        config = ConfiguracionCostos.objects.create(
            # Costos indirectos por unidad (valores ejemplo para dietética)
            costo_envases_por_kg=50.00,  # $50 por kg en envases
            costo_etiquetas_por_unidad=5.00,  # $5 por etiqueta
            costo_envio_promedio=100.00,  # $100 envío promedio

            # Tiempo y mano de obra
            tiempo_fraccionamiento_por_kg=10.00,  # 10 minutos por kg
            valor_hora_trabajo=500.00,  # $500 por hora de trabajo

            # Configuraciones globales
            incluir_costos_indirectos=False,  # Inicialmente desactivado
            redondear_precios=True,
            actualizar_automaticamente=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Configuración de costos creada exitosamente.\n'
                f'📊 Costos indirectos: {"Activados" if config.incluir_costos_indirectos else "Desactivados"}\n'
                f'🔄 Actualización automática: {"Activada" if config.actualizar_automaticamente else "Desactivada"}\n'
                f'💰 Redondeo de precios: {"Activado" if config.redondear_precios else "Desactivado"}\n\n'
                f'💡 Puedes modificar estos valores desde el panel de administración.'
            )
        )
