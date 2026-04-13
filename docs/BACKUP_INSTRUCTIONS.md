# 🔄 SISTEMA DE BACKUPS - LINO SALUDABLE

**Última actualización:** 10 de Abril de 2026  
**Tipo de implementación:** Híbrida (Local + Email)  
**Base de datos:** PostgreSQL (Railway) + SQLite (Desarrollo)

---

## 📚 ÍNDICE RÁPIDO

1. [Backup Local (Mac)](#backup-local)
2. [Backup con Email (Railway)](#backup-con-email)
3. [Configuración en Railway](#configuración-en-railway)
4. [Programar Cron Job](#programar-cron-job)
5. [Restaurar desde Backup](#restaurar-desde-backup)
6. [Troubleshooting](#troubleshooting)

---

## 🖥️ BACKUP LOCAL

### Uso en tu Mac (Desarrollo)

```bash
# Backup simple - guarda en backups/
python manage.py backup_db

# Ejemplo de salida:
# 🔍 Motor de BD detectado: django.db.backends.sqlite3
# 📦 Creando backup de SQLite...
# ✅ Backup SQLite creado: backup_20260410_143022.sqlite3 (2.45 MB)
# 🧹 Limpiando backups antiguos (manteniendo últimos 7 días)...
# 📁 Mantenidos 3 backups recientes
# 💾 Espacio total de backups: 7.23 MB
```

**Dónde se guarda:**
```
lino_saludable/
└── backups/
    ├── backup_20260410_143022.sqlite3
    ├── backup_20260409_120500.sqlite3
    └── backup_20260408_114300.sqlite3
```

**Retención:** Los últimos 7 días de backups (puedes cambiar con `--keep-days 14`)

---

## 📧 BACKUP CON EMAIL (Railway)

### Configuración en Railway (Una sola vez)

#### **PASO 1: Obtener App Password de Gmail**

1. Ve a [Google Account Security](https://myaccount.google.com/security)
2. Click en **"2-Step Verification"** (debe estar activado)
3. Click en **"App passwords"**
4. Selecciona:
   - Aplicación: **Mail**
   - Dispositivo: **Windows PC** (o similar)
5. Click **"Generate"**
6. ✅ Copiar la contraseña de **16 caracteres** (sin espacios)

**Ejemplo:**
```
abcd efgh ijkl mnop  →  abcdefghijklmnop
```

#### **PASO 2: Agregar Variables en Railway**

1. Railway Dashboard → Tu proyecto **web**
2. Click en pestaña **"Variables"**
3. Click **"+ New Variable"** y agregar:

| Variable | Valor |
|----------|-------|
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_HOST_USER` | `giulianodanielzulatto@gmail.com` |
| `EMAIL_HOST_PASSWORD` | `abcdefghijklmnop` (la que generaste) |

#### **PASO 3: Verificar Configuración**

```bash
# En tu Mac, verificar que email está configurado:
python manage.py shell
>>> from django.conf import settings
>>> settings.USE_EMAIL
True
>>> settings.EMAIL_HOST_USER
'giulianodanielzulatto@gmail.com'
```

---

## 🚀 PROGRAMAR CRON JOB EN RAILWAY

### Opción A: Usar Cron Job Task en Railway (RECOMENDADO)

Railway permite ejecutar comandos programados. **Necesitas plan Pro o usar alternativa.**

### Opción B: Usar Cron Job Local (Desarrollo)

En tu Mac:

```bash
# Abrir crontab
crontab -e

# Agregar esta línea para ejecutar backup DIARIAMENTE a las 2:00 AM:
0 2 * * * cd /Users/giulianozulatto/Proyectos/lino_saludable && python src/manage.py backup_db

# Para DIARIAMENTE con email a las 2:00 AM:
0 2 * * * cd /Users/giulianozulatto/Proyectos/lino_saludable && python src/manage.py backup_db --send-email

# Guardar: CTRL+X, Y, ENTER
```

**Verificar que funciona:**
```bash
# Ver crons activos
crontab -l

# Ver logs de cron
log stream --predicate 'process == "cron"' --level debug
```

### Opción C: Usar Scheduled Task (Railway + Webhook)

Si tienes plan Pro en Railway, puedes usar el "Cron Job" service:

1. Railway → New Service → **Cron Job**
2. Schedule: `0 2 * * *` (2:00 AM diario)
3. Command: 
   ```bash
   cd src && python manage.py backup_db --send-email
   ```

---

## 💾 RESTAURAR DESDE BACKUP

### Si usaste PostgreSQL (Railway):

```bash
# 1. Descargar el .sql.gz desde tu email
# 2. Descomprimir:
gunzip backup_20260410_143022.sql.gz

# 3. Restaurar en tu BD local (para pruebas):
PGPASSWORD='tu_password' psql -U postgres -d tu_database < backup_20260410_143022.sql

# 4. Para restaurar en Railway (necesitas credenciales de Railway):
PGPASSWORD='railway_password' psql \
  -h roundhouse.proxy.rlwy.net \
  -p 12345 \
  -U postgres \
  -d railway \
  < backup_20260410_143022.sql
```

### Si usaste SQLite (Desarrollo):

```bash
# 1. Copiar el archivo de backup a la ubicación actual:
cp backups/backup_20260410_143022.sqlite3 src/db.sqlite3

# 2. Listo, Django usará el backup como BD
python src/manage.py shell
>>> # Tu BD ahora tiene los datos del backup
```

---

## 🔧 TROUBLESHOOTING

### ❌ Error: "pg_dump not found"

**Problema:** PostgreSQL client tools no instalados

**Solución (Mac):**
```bash
# Instalar PostgreSQL client
brew install postgresql

# Verificar que pg_dump existe:
which pg_dump
```

### ❌ Error: "PGPASSWORD not recognized"

**Problema:** Contraseña incorrecta o credenciales vacías

**Solución:**
```bash
# Verificar credenciales en Railway
echo $DATABASE_URL
# Debe mostrar: postgresql://user:pass@host:port/dbname

# Si falta, agregar en Railway → Variables
```

### ❌ Error: "Email not configured"

**Problema:** Variables EMAIL_* no están en Railway

**Solución:**
```bash
# Verificar que existen en Railway:
# Variables → EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

# Test local:
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'tu-email@gmail.com', ['tu-email@gmail.com'])
```

### ⚠️ Email llegando a Spam

**Problema:** Gmail filtra el email como spam

**Solución:**
```
1. Revisar spam/promotions en Gmail
2. Marcar como "No es spam"
3. Crear filtro para que no vuelva a spam
4. Considerar usar un email específico para backups
```

---

## 📊 SEGURIDAD & BUENAS PRÁCTICAS

### ✅ QUÉ ESTÁ PROTEGIDO

- ✅ `.gitignore` excluye `backups/*.sql`, `backups/*.gz`
- ✅ Email + contraseña en variables de entorno (nunca en código)
- ✅ Archivo comprimido se elimina después de enviarlo
- ✅ Los backups enviados por email van a tu inbox (encriptados vía HTTPS)

### ❌ QUÉ NO ESTÁ PROTEGIDO

- ⚠️ Los backups locales en `backups/` son legibles en texto plano
- ⚠️ Email con datos sensibles en tu inbox (guardar seguro)
- ⚠️ Si pierdes el App Password de Gmail, necesitarás generar uno nuevo

### 🛡️ RECOMENDACIONES

1. **Revisar backups regularmente:** Al menos 1x por semana
2. **Guardar en Drive o Dropbox:** Descargar desde email y respaldar
3. **Testear restauro:** 1x al mes, restaurar en ambiente local
4. **Rotación:** Los últimos 7 días se mantienen automáticamente
5. **Monitoreo:** Revisar si llegas backups en email, si no → investigar error

---

## 📞 REFERENCIA RÁPIDA

```bash
# Backup local
python manage.py backup_db

# Backup con email
python manage.py backup_db --send-email

# Backup manteniendo últimos 14 días
python manage.py backup_db --keep-days 14

# Backup con email + mantener 14 días
python manage.py backup_db --send-email --keep-days 14

# Ver help
python manage.py backup_db --help
```

---

**Última revisión:** 10 de Abril de 2026  
**Estado:** ✅ Producción Ready
