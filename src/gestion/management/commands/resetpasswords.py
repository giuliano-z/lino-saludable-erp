import os
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Resetea las contraseñas de los usuarios principales desde variables de entorno'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.WARNING('🔑 RESETEANDO CONTRASEÑAS'))
        self.stdout.write(self.style.WARNING('=' * 60))

        usuarios = [
            {
                'username': 'sister_emprendedora',
                'env_var': 'ADMIN_PASSWORD_1',
                'email': '',
                'is_superuser': True,
            },
            {
                'username': 'el_super_creador',
                'env_var': 'ADMIN_PASSWORD_2',
                'email': '',
                'is_superuser': True,
            },
            {
                'username': 'admin_lino',
                'env_var': 'ADMIN_PASSWORD_3',
                'email': 'admin@lino.com',
                'is_superuser': True,
            },
        ]

        for u in usuarios:
            password = os.environ.get(u['env_var'])
            if not password:
                self.stdout.write(self.style.ERROR(
                    f"❌ Variable de entorno '{u['env_var']}' no configurada — omitiendo '{u['username']}'"
                ))
                continue

            try:
                user = User.objects.get(username=u['username'])
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"✅ Contraseña de '{u['username']}' reseteada"))
            except User.DoesNotExist:
                User.objects.create_superuser(
                    username=u['username'],
                    email=u['email'],
                    password=password,
                )
                self.stdout.write(self.style.SUCCESS(f"✅ Usuario '{u['username']}' creado"))

        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.SUCCESS('✅ PROCESO COMPLETADO'))
        self.stdout.write(self.style.WARNING('=' * 60))
