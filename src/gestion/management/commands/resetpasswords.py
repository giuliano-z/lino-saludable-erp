from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Resetea las contraseñas de los usuarios principales'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.WARNING('🔑 RESETEANDO CONTRASEÑAS'))
        self.stdout.write(self.style.WARNING('=' * 60))

        # Resetear contraseña de sister_emprendedora
        try:
            user1 = User.objects.get(username='sister_emprendedora')
            user1.set_password('changeme')
            user1.save()
            self.stdout.write(self.style.SUCCESS("✅ Contraseña de 'sister_emprendedora' reseteada"))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Usuario 'sister_emprendedora' no existe"))

        # Resetear contraseña de el_super_creador
        try:
            user2 = User.objects.get(username='el_super_creador')
            user2.set_password('changeme')
            user2.save()
            self.stdout.write(self.style.SUCCESS("✅ Contraseña de 'el_super_creador' reseteada"))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Usuario 'el_super_creador' no existe"))

        # Crear/resetear admin_lino
        try:
            user3 = User.objects.get(username='admin_lino')
            user3.set_password('changeme')
            user3.save()
            self.stdout.write(self.style.SUCCESS("✅ Contraseña de 'admin_lino' reseteada"))
        except User.DoesNotExist:
            User.objects.create_superuser(
                username='admin_lino',
                email='admin@lino.com',
                password='changeme'
            )
            self.stdout.write(self.style.SUCCESS("✅ Usuario 'admin_lino' creado"))

        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.SUCCESS('✅ PROCESO COMPLETADO'))
        self.stdout.write('')
        self.stdout.write('Credenciales actualizadas:')
        self.stdout.write('  Usuario: sister_emprendedora | Password: changeme')
        self.stdout.write('  Usuario: el_super_creador    | Password: changeme')
        self.stdout.write('  Usuario: admin_lino          | Password: changeme')
        self.stdout.write(self.style.WARNING('=' * 60))
