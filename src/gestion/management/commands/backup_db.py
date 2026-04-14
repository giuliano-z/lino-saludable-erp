"""
Management command: backup_db
Exporta todos los datos de la BD usando dumpdata de Django (JSON)
Comprime el resultado en .gz
Opcionalmente envía por email
Limpia backups antiguos (>7 días)
"""

import gzip
import logging
import os
from datetime import datetime, timedelta
from io import StringIO

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management import call_command
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Respalda la base de datos usando dumpdata (JSON) y opcionalmente envía por email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--send-email',
            action='store_true',
            dest='send_email',
            help='Envía el backup por email a la dirección configurada'
        )

    def handle(self, *args, **options):
        logger.info("Iniciando backup de base de datos")
        self.stdout.write(self.style.SUCCESS('\n🔄 Iniciando backup de base de datos...\n'))

        # Crear carpeta backups si no existe
        backups_dir = 'backups'
        if not os.path.exists(backups_dir):
            os.makedirs(backups_dir)
            self.stdout.write(self.style.SUCCESS(f"✅ Carpeta '{backups_dir}' creada"))

        # Generar nombre del archivo con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.json'
        backup_path = os.path.join(backups_dir, backup_filename)
        backup_gz_path = f'{backup_path}.gz'

        try:
            # 1. EXPORTAR CON DUMPDATA
            self.stdout.write(self.style.WARNING('📦 Exportando datos con dumpdata...'))

            # Usar StringIO para capturar la salida
            json_output = StringIO()
            call_command(
                'dumpdata',
                '--indent=2',
                '--exclude=contenttypes',
                '--exclude=auth.permission',
                stdout=json_output
            )
            json_data = json_output.getvalue()

            logger.info("Datos exportados: %d bytes", len(json_data))
            self.stdout.write(self.style.SUCCESS(f'✅ Datos exportados ({len(json_data)} bytes)'))

            # 2. COMPRIMIR EN .GZ
            self.stdout.write(self.style.WARNING('📂 Comprimiendo archivo...'))
            with gzip.open(backup_gz_path, 'wt', encoding='utf-8') as gz_file:
                gz_file.write(json_data)

            file_size = os.path.getsize(backup_gz_path)
            logger.info("Archivo comprimido: %s (%d bytes)", backup_gz_path, file_size)
            self.stdout.write(self.style.SUCCESS(f'✅ Archivo comprimido: {backup_gz_path} ({file_size} bytes)'))

            # 3. ENVIAR POR EMAIL (OPCIONAL)
            if options['send_email']:
                recipient = getattr(settings, 'BACKUP_EMAIL_RECIPIENT', '')
                if not recipient:
                    logger.warning("BACKUP_EMAIL_RECIPIENT no configurado — omitiendo envío de email")
                    self.stdout.write(self.style.WARNING(
                        '⚠️  BACKUP_EMAIL_RECIPIENT no configurado. Backup guardado localmente sin enviar.'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(f'📧 Enviando backup a {recipient}...'))
                    try:
                        self._send_backup_email(backup_gz_path, backup_filename, recipient)
                        logger.info("Backup enviado por email a %s", recipient)
                        self.stdout.write(self.style.SUCCESS(f'✅ Email enviado a {recipient}'))

                        # Borrar archivo después de enviarlo
                        os.remove(backup_gz_path)
                        logger.info("Archivo local eliminado tras envío exitoso")
                        self.stdout.write(self.style.SUCCESS('🗑️  Archivo eliminado del servidor'))
                    except Exception as email_error:
                        logger.error("Error al enviar backup por email: %s", str(email_error), exc_info=True)
                        self.stdout.write(self.style.ERROR(
                            f'❌ Error al enviar email: {str(email_error)}\n'
                            f'   El archivo de backup sigue en: {backup_gz_path}'
                        ))

            # 4. LIMPIAR BACKUPS ANTIGUOS (>7 DÍAS)
            self.stdout.write(self.style.WARNING('🧹 Limpiando backups antiguos...'))
            self._cleanup_old_backups(backups_dir)

            logger.info("Backup completado exitosamente")
            self.stdout.write(self.style.SUCCESS('\n✅ Backup completado exitosamente\n'))

        except Exception as e:
            logger.error("Backup fallido: %s", str(e), exc_info=True)
            self.stdout.write(self.style.ERROR(f'\n❌ Error durante el backup: {str(e)}\n'))
            raise

    def _send_backup_email(self, backup_gz_path, backup_filename, recipient_email):
        """
        Envía el archivo de backup por email al destinatario configurado.
        El email se define con la variable de entorno BACKUP_EMAIL_RECIPIENT en settings.py.
        """
        # Crear mensaje
        subject = f'🔒 Backup de BD Lino Saludable - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        body = f"""
Hola,

Se adjunta el backup automático de la base de datos de Lino Saludable.

Detalles:
- Archivo: {backup_filename}
- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Formato: JSON comprimido en .gz
- Excluye: contenttypes, auth.permission

Para restaurar:
1. Descomprimir el archivo: gunzip backup_YYYYMMDD_HHMMSS.json.gz
2. Ejecutar: python manage.py loaddata backup_YYYYMMDD_HHMMSS.json

--
Sistema de Respaldos - Lino Saludable
"""

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email]
        )

        # Adjuntar el archivo comprimido
        with open(backup_gz_path, 'rb') as attachment:
            email.attach(
                backup_filename + '.gz',
                attachment.read(),
                'application/gzip'
            )

        # Enviar
        email.send(fail_silently=False)

    def _cleanup_old_backups(self, backups_dir):
        """
        Elimina backups más antiguos de 7 días
        """
        if not os.path.exists(backups_dir):
            return

        cutoff_date = datetime.now() - timedelta(days=7)
        deleted_count = 0

        for filename in os.listdir(backups_dir):
            if filename.startswith('backup_') and filename.endswith('.json.gz'):
                file_path = os.path.join(backups_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                if file_time < cutoff_date:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        self.stdout.write(f'  🗑️  Eliminado: {filename}')
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠️  No se pudo eliminar {filename}: {str(e)}')
                        )

        if deleted_count == 0:
            self.stdout.write('  ✅ Sin backups antiguos para eliminar')
        else:
            logger.info("Limpieza: %d backup(s) antiguo(s) eliminado(s)", deleted_count)
            self.stdout.write(
                self.style.SUCCESS(f'✅ {deleted_count} backup(s) antiguo(s) eliminado(s)')
            )
