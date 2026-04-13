# ✅ CHECKLIST DE LIMPIEZA Y DESPLIEGUE

## 🧹 FASE 1: LIMPIEZA (COMPLETADA)

### Archivos Eliminados
- [x] `Procfile` - Conflictivo con railway.toml
- [x] `server.js` - Node.js vacío innecesario
- [x] `package.json` - Node.js vacío innecesario
- [x] `run_migrations_railway.py` - Script temporal obsoleto
- [x] `migrate.sh` - Script bash redundante
- [x] `start.sh` - Script bash redundante
- [x] 17 archivos en `src/` (test_*.py, check_*.py, etc.)

### Archivos Creados
- [x] `railway.toml` - Configuración principal Railway
- [x] `.slugignore` - Exclusiones de build
- [x] `RAILWAY_DEPLOY_FINAL.md` - Documentación
- [x] `RESUMEN_LIMPIEZA.md` - Resumen de cambios
- [x] `CHECKLIST.md` - Este archivo
- [x] `commit_limpieza.sh` - Script de commit

### Archivos Mejorados
- [x] `nixpacks.toml` - Simplificado y optimizado
- [x] `createusers.py` - Variables de entorno + mejor logging

---

## 📦 FASE 2: GIT COMMIT & PUSH

### Preparación
- [ ] Revisar `git status` - ✅ Ya verificado arriba
- [ ] Verificar que railway.toml está incluido
- [ ] Verificar que .slugignore está incluido

### Ejecución
**OPCIÓN A: Script Automático (Recomendado)**
```bash
./commit_limpieza.sh
```

**OPCIÓN B: Manual**
```bash
git add .
git commit -m "🧹 Limpieza proyecto Railway - eliminados archivos conflictivos"
git push origin main
```

### Verificación
- [ ] Commit creado exitosamente
- [ ] Push completado sin errores
- [ ] Cambios visibles en GitHub

---

## 🚀 FASE 3: RAILWAY DEPLOY

### Monitoreo Inicial
- [ ] Abrir Railway Dashboard: https://railway.app
- [ ] Ir al proyecto LINO Saludable
- [ ] Verificar que inició auto-deploy tras push

### Logs a Buscar (Deploy Logs)

**1. Build Phase**
```
✓ Installing packages
✓ Collecting static files...
✓ Static files collected
```

**2. Deploy Phase - CRÍTICO**
```
✓ Running migrations...
✓ Operations to perform:
✓ Running migrations for auth, gestion, etc.
✓ Migrations completed

✓ Creating users...
✓ ✅ Usuario sister_emprendedora creado
✓ ✅ Usuario el_super_creador creado

✓ Starting gunicorn...
✓ Listening at: http://0.0.0.0:8080
```

### Verificación de Servicios
- [ ] Servicio `web` - Status: Running
- [ ] Servicio `postgres` - Status: Running
- [ ] URL pública accesible

---

## 🔍 FASE 4: VERIFICACIÓN FUNCIONAL

### Test 1: Página Principal
- [ ] Abrir: https://web-production-b0ad1.up.railway.app/
- [ ] Debe mostrar página sin error 500
- [ ] No debe haber errores de "relation does not exist"

### Test 2: Admin Panel
- [ ] Abrir: https://web-production-b0ad1.up.railway.app/admin/
- [ ] Debe mostrar login de Django admin
- [ ] **NO** debe mostrar error de base de datos

### Test 3: Login Superuser 1
- [ ] Username: `sister_emprendedora`
- [ ] Password: (ver variable ADMIN_PASSWORD_1 o default: `changeme`)
- [ ] Login exitoso
- [ ] Acceso a panel admin completo

### Test 4: Login Superuser 2
- [ ] Username: `el_super_creador`
- [ ] Password: (ver variable ADMIN_PASSWORD_2 o default: `changeme`)
- [ ] Login exitoso
- [ ] Acceso a panel admin completo

---

## 🔒 FASE 5: SEGURIDAD POST-DEPLOY

### Cambio de Contraseñas (URGENTE)
- [ ] Login como `sister_emprendedora`
- [ ] Ir a: Change Password
- [ ] Establecer contraseña segura nueva
- [ ] Guardar y verificar login con nueva contraseña

- [ ] Login como `el_super_creador`
- [ ] Ir a: Change Password
- [ ] Establecer contraseña segura nueva
- [ ] Guardar y verificar login con nueva contraseña

### Variables de Entorno (Opcional pero Recomendado)
- [ ] Ir a Railway → Service Settings → Variables
- [ ] Agregar `ADMIN_PASSWORD_1` con contraseña segura
- [ ] Agregar `ADMIN_PASSWORD_2` con contraseña segura
- [ ] Redeploy para aplicar cambios

### Verificación de Seguridad
- [ ] `DEBUG=false` en variables de entorno
- [ ] `SECRET_KEY` configurado (no el default)
- [ ] `ALLOWED_HOSTS` correctamente configurado
- [ ] Contraseñas cambiadas y documentadas de forma segura

---

## 📊 FASE 6: DOCUMENTACIÓN

### Actualizar Documentación
- [ ] Documentar contraseñas nuevas en lugar seguro (1Password, Bitwarden, etc.)
- [ ] Actualizar `docs/RAILWAY_ENV_VARS.md` si es necesario
- [ ] Marcar en docs que deploy fue exitoso

### Backup
- [ ] Verificar que existe backup automático de PostgreSQL en Railway
- [ ] Documentar URL de producción
- [ ] Guardar credenciales de acceso de forma segura

---

## ✅ CHECKLIST FINAL

### Estado del Proyecto
- [ ] ✅ Código limpio sin archivos innecesarios
- [ ] ✅ Configuración Railway optimizada
- [ ] ✅ Migraciones ejecutadas en producción
- [ ] ✅ Usuarios creados correctamente
- [ ] ✅ Aplicación accesible públicamente
- [ ] ✅ Admin panel funcional
- [ ] ✅ Contraseñas cambiadas
- [ ] ✅ Variables de entorno seguras

### Próximos Desarrollos
- [ ] Configurar dominio personalizado (opcional)
- [ ] Configurar email SMTP para recuperación de contraseñas
- [ ] Configurar backups automáticos adicionales
- [ ] Implementar monitoreo (Sentry, etc.)
- [ ] Configurar SSL/HTTPS (Railway lo hace automáticamente)

---

## 🆘 TROUBLESHOOTING

### Si las migraciones NO se ejecutan:

1. **Verificar logs completos:**
   ```bash
   railway logs --service web
   ```

2. **Ejecutar manualmente:**
   ```bash
   railway shell --service web
   cd src && python manage.py migrate --noinput
   python manage.py createusers
   exit
   ```

3. **Verificar DATABASE_URL:**
   ```bash
   railway variables --service web
   ```

### Si hay error 500:

1. Verificar logs: `railway logs --service web`
2. Buscar línea exacta de error
3. Verificar que PostgreSQL está corriendo
4. Verificar que tablas existen: `railway shell postgres`

### Si no puedes hacer login:

1. Verificar que usuarios fueron creados (logs)
2. Intentar crear manualmente:
   ```bash
   railway shell --service web
   cd src && python manage.py createsuperuser
   ```

---

## 📞 SOPORTE

**Railway Docs:** https://docs.railway.app  
**Django Docs:** https://docs.djangoproject.com  
**PostgreSQL Docs:** https://www.postgresql.org/docs/

---

**Fecha creación:** 6 de noviembre de 2025  
**Última actualización:** 6 de noviembre de 2025  
**Estado:** 🟡 Pendiente de deployment  
**Versión Python:** 3.13.0  
**Versión Django:** 5.2.4
