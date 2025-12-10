"""
Script para resetear contraseñas de usuarios en Railway
"""
from django.contrib.auth.models import User

print("🔑 RESETEANDO CONTRASEÑAS...")
print("=" * 60)

# Resetear contraseña de sister_emprendedora
try:
    user1 = User.objects.get(username='sister_emprendedora')
    user1.set_password('changeme')
    user1.save()
    print("✅ Contraseña de 'sister_emprendedora' reseteada")
except User.DoesNotExist:
    print("❌ Usuario 'sister_emprendedora' no existe")

# Resetear contraseña de el_super_creador
try:
    user2 = User.objects.get(username='el_super_creador')
    user2.set_password('changeme')
    user2.save()
    print("✅ Contraseña de 'el_super_creador' reseteada")
except User.DoesNotExist:
    print("❌ Usuario 'el_super_creador' no existe")

# Crear/resetear admin_lino
try:
    user3 = User.objects.get(username='admin_lino')
    user3.set_password('changeme')
    user3.save()
    print("✅ Contraseña de 'admin_lino' reseteada")
except User.DoesNotExist:
    User.objects.create_superuser(
        username='admin_lino',
        email='admin@lino.com',
        password='changeme'
    )
    print("✅ Usuario 'admin_lino' creado")

print("=" * 60)
print("✅ PROCESO COMPLETADO")
print("")
print("Credenciales actualizadas:")
print("  Usuario: sister_emprendedora | Password: changeme")
print("  Usuario: el_super_creador    | Password: changeme")
print("  Usuario: admin_lino          | Password: changeme")
print("=" * 60)
