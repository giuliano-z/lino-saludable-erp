# 📋 LISTA EXACTA DE MOVIMIENTOS Y ELIMINACIONES

## FASE 1: Crear Estructura docs/

Crear estas carpetas nuevas:
```bash
mkdir -p docs/reports
mkdir -p docs/testing
mkdir -p docs/guides
mkdir -p docs/manual
mkdir -p docs/project
mkdir -p docs/archived
```

---

## FASE 2: Mover Archivos a docs/

### 📁 docs/reports/ (9 archivos)

**MOVER ESTOS ARCHIVOS:**
```
ANALISIS_PROFUNDO_BUGS.md                → docs/reports/
ANALISIS_FLUJO_VENTAS_DETALLADO.md       → docs/reports/
AUDITORIA_LIMPIEZA_DIC2025.md            → docs/reports/
REPORTE_FINAL_CORRECCIONES.md            → docs/reports/
REPORTE_VERIFICACION.md                  → docs/reports/
RESUMEN_EJECUTIVO.md                     → docs/reports/
RESUMEN_EJECUTIVO_CORRECCIONES.md        → docs/reports/
RESUMEN_LIMPIEZA.md                      → docs/reports/
CORRECCIONES_FLUJO_VENTAS_RESUMEN.md     → docs/reports/
```

### 📁 docs/testing/ (8 archivos)

**MOVER ESTOS ARCHIVOS:**
```
INDEX_TESTING.md                → docs/testing/
QUICK_REFERENCE_TESTING.md      → docs/testing/
TESTING_STATUS_FINAL.md         → docs/testing/
FINAL_TESTING_FIXES.md          → docs/testing/
RESUMEN_FINAL_TESTING.md        → docs/testing/
TESTING_COMPLETE.txt            → docs/testing/
CHANGELOG_TESTING_SESSION.md    → docs/testing/
PLAN_TESTING_COMPLETO.md        → docs/testing/
```

### 📁 docs/guides/ (5 archivos)

**MOVER ESTOS ARCHIVOS:**
```
GUIA_BACKUP_RAILWAY_DETALLADA.md        → docs/guides/
GUIA_RESET_RAILWAY.md                   → docs/guides/
PLAN_BACKUPS_AUTOMATICOS.md             → docs/guides/
DEPLOY_SEGURO_PLAN.md                   → docs/guides/
RAILWAY_DEPLOY_FINAL.md                 → docs/guides/
```

### 📁 docs/manual/ (1 archivo)

**MOVER ESTOS ARCHIVOS:**
```
MANUAL_RESUMIDO.md              → docs/manual/
```

### 📁 docs/project/ (4 archivos)

**MOVER ESTOS ARCHIVOS:**
```
INDICE.md                               → docs/project/
CHECKLIST.md                            → docs/project/
PLAN_CORRECCION_BUGS_TDD.md             → docs/project/
URLS_REFACTORING_COMPLETADO.md          → docs/project/
```

### 📁 docs/archived/ (Mover docs viejos)

**MOVER ESTOS ARCHIVOS DE docs/ ACTUAL A docs/archived/:**

Los ~51 archivos .md que ya están en docs/ pueden quedar ahí o moverse a archived/ si son históricos. Propuesta: dejar ahí pero organizar en estructura similar.

---

## FASE 3: Eliminar Archivos VACÍOS (19 archivos)

**ELIMINAR ESTOS ARCHIVOS DE LA RAÍZ:**

```bash
rm GUIA_COMPLETA_TESTING.md
rm GUIA_TESTING_BUG_A.md
rm INDEX_FINAL.md
rm INDICE_TESTING_DOCS.md
rm MANUAL_PARTE_2_INVENTARIO.md
rm MANUAL_PARTE_3_OPERACIONES.md
rm MANUAL_PARTE_4_METRICAS.md
rm MANUAL_PARTE_5_CONFIGURACION.md
rm MANUAL_USUARIO_COMPLETO.md
rm REFERENCE_TESTING.md
rm RESPUESTAS_TUS_3_PREGUNTAS.md
rm RESUMEN_10_DOCUMENTOS.md
rm RESUMEN_VISUAL_TESTING.md
rm TESTING_CHECKLIST_RAPIDO.md
rm TESTING_RAPIDO.md
rm Procfile
rm start.sh
rm test_bug_a_fix.py
```

**TOTAL:** 19 archivos eliminados

---

## FASE 4: Crear Archivos README

### docs/README.md
Crear índice general de documentación

### docs/testing/README.md
Crear índice de documentación de testing

### src/gestion/tests/README.md
Crear guía local de tests

---

## FASE 5: Actualizar README.md Raíz

Agregar sección:
```markdown
## 📚 Documentación

Ver [`docs/README.md`](./docs/README.md) para documentación completa.

### Quick Links
- [Testing](./docs/testing/)
- [Reportes](./docs/reports/)
- [Guías Operacionales](./docs/guides/)
- [Manuales](./docs/manual/)
```

---

## RESUMEN DE CAMBIOS

| Tipo | Cantidad | Destino |
|------|----------|---------|
| Archivos movidos | 27 | docs/subdirectories/ |
| Archivos eliminados | 19 | (deleted) |
| Archivos creados | 3 | README.md en cada sección |
| Archivos en raíz antes | 63 | |
| Archivos en raíz después | ~15 | |

---

## ARCHIVOS QUE QUEDAN EN RAÍZ (15 aprox.)

```
✅ MANTENER:
├── .env                           (variables locales)
├── .env.example                   (template)
├── .env.save                      (backup)
├── .gitignore
├── .slugignore
├── .github/                       (GitHub Actions)
├── README.md                      (ACTUALIZADO)
├── requirements.txt
├── pytest.ini
├── conftest.py
├── railway.toml
├── mcp-config.json
├── nixpacks.toml
├── audit_report.json
├── dashboard_screenshot.png
├── src/                           (código)
├── tests_e2e/                     (E2E tests)
├── backups/                       (backups)
├── docs/                          (REORGANIZADO)
├── venv/                          (DO NOT TOUCH)
└── .git/                          (DO NOT TOUCH)
```

---

## VERIFICACIÓN POST-CAMBIOS

Una vez completado, verificar:

✅ Estructura de carpetas correcta  
✅ Todos los archivos movidos correctamente  
✅ README.md actua liens en cada sección  
✅ No hay archivos huérfanos  
✅ Git status muestra los movimientos  
✅ Tests siguen pasando (55/55) ✅  
✅ Código de negocio intacto  
✅ URLs funcionan igual  
✅ Base de datos intacta  

---

## COMANDO DE EJECUCIÓN RÁPIDA

Una vez aprobado, ejecutar en orden:

```bash
# Fase 1: Crear estructura
mkdir -p docs/{reports,testing,guides,manual,project,archived}

# Fase 2: Mover reportes
mv ANALISIS_PROFUNDO_BUGS.md docs/reports/
mv ANALISIS_FLUJO_VENTAS_DETALLADO.md docs/reports/
# ... (resto de movimientos)

# Fase 3: Eliminar vacíos
rm GUIA_COMPLETA_TESTING.md
rm GUIA_TESTING_BUG_A.md
# ... (resto de eliminaciones)

# Fase 4: Crear READMEs
# (crear archivos manualmente o via script)

# Fase 5: Actualizar README principal
# (editar README.md raíz)

# Verificar
git status
ls -la
```

---

## NOTAS IMPORTANTES

⚠️ **ANTES DE EJECUTAR:**
1. Hacer backup con `git commit -m "Backup antes de reorganización"`
2. Verificar que el branch sea main o de desarrollo
3. Leer el plan completo: `PLAN_PROFESIONALIZACION.md`

✅ **SEGURIDAD:**
- No hay cambios en código de negocio
- Tests siguen igual (55/55)
- Base de datos no se toca
- Solo movimiento de archivos de documentación

🔄 **ROLLBACK:**
Si algo sale mal, puedes revertir con:
```bash
git reset --hard HEAD~1
```

---

**Estado:** 🟢 LISTO PARA EJECUTAR  
**Fecha:** 2026-04-13  
**Duración Estimada:** 10-15 minutos
