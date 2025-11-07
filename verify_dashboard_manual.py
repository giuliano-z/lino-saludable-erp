#!/usr/bin/env python3
"""
🔍 VERIFICACIÓN MANUAL GUIADA - DASHBOARD PRODUCCIÓN
Script interactivo para verificar visualmente el dashboard

Ejecutar:
    python verify_dashboard_manual.py
"""

import requests
from playwright.sync_api import sync_playwright
import time


# ==================== CONFIGURACIÓN ====================

BASE_URL = "https://web-production-b0ad1.up.railway.app"
USERNAME = "sister_emprendedora"
PASSWORD = "changeme"

# ==================== COLORES ====================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}  {text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}\n")


def print_step(number, text):
    print(f"\n{Colors.BOLD}{Colors.YELLOW}PASO {number}:{Colors.END} {text}")


def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def wait_user():
    input(f"\n{Colors.YELLOW}Presiona ENTER para continuar...{Colors.END}")


# ==================== VERIFICACIÓN MANUAL ====================

def verify_dashboard():
    """Verificación manual del dashboard con Playwright"""
    
    print_header("🔍 VERIFICACIÓN MANUAL DEL DASHBOARD")
    print_info(f"Servidor: {BASE_URL}")
    print_info(f"Usuario: {USERNAME}")
    print_info("Vamos a abrir el navegador y verificar juntos cada elemento")
    wait_user()
    
    try:
        with sync_playwright() as p:
            # Abrir browser en modo NO headless (visible)
            print_step(1, "Abriendo navegador Chrome...")
            browser = p.chromium.launch(
                headless=False,  # Mostrar el navegador
                slow_mo=1000     # Ralentizar para que puedas ver
            )
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            
            print_success("Navegador abierto")
            wait_user()
            
            # PASO 1: Ir a login
            print_step(2, "Navegando a página de login...")
            page.goto(f"{BASE_URL}/admin/login/")
            page.wait_for_load_state('networkidle')
            
            print_success(f"Login page cargada: {page.url}")
            print_info("¿Ves el formulario de login? (Username y Password)")
            wait_user()
            
            # PASO 2: Hacer login
            print_step(3, f"Haciendo login como {USERNAME}...")
            page.fill('input[name="username"]', USERNAME)
            page.fill('input[name="password"]', PASSWORD)
            page.click('input[type="submit"]')
            page.wait_for_load_state('networkidle')
            
            print_success(f"Login completado. URL actual: {page.url}")
            print_info("¿Lograste entrar al admin de Django?")
            wait_user()
            
            # PASO 3: Ir al dashboard
            print_step(4, "Navegando al dashboard principal...")
            page.goto(f"{BASE_URL}/gestion/")
            page.wait_for_load_state('networkidle')
            time.sleep(2)  # Esperar a que carguen los elementos dinámicos
            
            print_success(f"Dashboard cargado: {page.url}")
            print("")
            
            # VERIFICACIONES VISUALES
            print_header("📋 CHECKLIST DE VERIFICACIÓN VISUAL")
            
            # Check 1: KPIs
            print(f"{Colors.BOLD}1. KPIs (Tarjetas con métricas):{Colors.END}")
            print("   ¿Ves tarjetas/cards con números de:")
            print("   - Ventas del día/mes")
            print("   - Compras realizadas")
            print("   - Stock de productos")
            print("   - Alertas o notificaciones")
            resp = input(f"   {Colors.YELLOW}¿Se ven los KPIs? (s/n): {Colors.END}").lower()
            
            if resp == 's':
                print_success("KPIs visibles ✓")
                kpis_ok = True
            else:
                print_error("KPIs NO visibles - Investigar")
                kpis_ok = False
            
            # Check 2: Navegación
            print(f"\n{Colors.BOLD}2. Navegación (Sidebar/Header):{Colors.END}")
            print("   ¿Ves links/botones para:")
            print("   - Productos")
            print("   - Materias Primas")
            print("   - Compras")
            print("   - Ventas")
            print("   - Ajustes")
            print("   - Reportes")
            resp = input(f"   {Colors.YELLOW}¿Funciona la navegación? (s/n): {Colors.END}").lower()
            
            if resp == 's':
                print_success("Navegación visible ✓")
                nav_ok = True
            else:
                print_error("Navegación NO visible - Investigar")
                nav_ok = False
            
            # Check 3: Gráficos
            print(f"\n{Colors.BOLD}3. Gráficos (Chart.js):{Colors.END}")
            print("   ¿Ves gráficos como:")
            print("   - Gráfico de barras")
            print("   - Gráfico de líneas")
            print("   - Gráfico de torta/pie")
            resp = input(f"   {Colors.YELLOW}¿Se muestran gráficos? (s/n): {Colors.END}").lower()
            
            if resp == 's':
                print_success("Gráficos visibles ✓")
                charts_ok = True
            else:
                print_error("Gráficos NO visibles - Investigar")
                charts_ok = False
            
            # Check 4: Estilos CSS
            print(f"\n{Colors.BOLD}4. Estilos y Diseño:{Colors.END}")
            print("   ¿La página se ve:")
            print("   - Con colores (verde/natural)")
            print("   - Bien organizada")
            print("   - Con iconos")
            print("   - Responsive/adaptada")
            resp = input(f"   {Colors.YELLOW}¿Los estilos cargan bien? (s/n): {Colors.END}").lower()
            
            if resp == 's':
                print_success("Estilos CSS OK ✓")
                css_ok = True
            else:
                print_error("Estilos NO cargan bien")
                css_ok = False
            
            # PASO 5: Probar navegación
            print_step(5, "Probando navegación a módulos...")
            print_info("Vamos a hacer click en 'Productos'")
            wait_user()
            
            try:
                # Buscar link de productos (puede variar el selector)
                page.click('text=Productos', timeout=5000)
                page.wait_for_load_state('networkidle')
                
                print_success(f"Navegó a: {page.url}")
                print_info("¿Ves la lista de productos?")
                resp = input(f"   {Colors.YELLOW}¿Carga la lista? (s/n): {Colors.END}").lower()
                
                productos_ok = resp == 's'
            except Exception as e:
                print_error(f"No se pudo hacer click en Productos: {str(e)}")
                productos_ok = False
            
            # PASO 6: Screenshot
            print_step(6, "Tomando screenshot del dashboard...")
            page.goto(f"{BASE_URL}/gestion/")
            page.wait_for_load_state('networkidle')
            time.sleep(2)
            
            screenshot_path = "dashboard_production_screenshot.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print_success(f"Screenshot guardado: {screenshot_path}")
            
            # RESUMEN FINAL
            print_header("📊 RESUMEN DE VERIFICACIÓN MANUAL")
            
            checks = {
                'KPIs Visibles': kpis_ok,
                'Navegación Funcional': nav_ok,
                'Gráficos Chart.js': charts_ok,
                'Estilos CSS': css_ok,
                'Módulo Productos': productos_ok
            }
            
            total = len(checks)
            passed = sum(checks.values())
            percentage = (passed / total * 100)
            
            print(f"\nTotal verificaciones: {total}")
            print(f"{Colors.GREEN}✅ Verificaciones OK: {passed}{Colors.END}")
            print(f"{Colors.RED}❌ Verificaciones Fallidas: {total - passed}{Colors.END}")
            print(f"{Colors.BOLD}📈 Porcentaje: {percentage:.1f}%{Colors.END}\n")
            
            for check_name, check_result in checks.items():
                icon = "✅" if check_result else "❌"
                print(f"{icon} {check_name}")
            
            print("")
            print_info("Mantendré el navegador abierto por 30 segundos")
            print_info("Explora el dashboard libremente...")
            time.sleep(30)
            
            browser.close()
            print_success("Navegador cerrado")
            
            # Guardar resultados
            print_step(7, "Guardando resultados...")
            
            with open('dashboard_manual_verification.txt', 'w') as f:
                f.write("VERIFICACIÓN MANUAL DASHBOARD - PRODUCCIÓN\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"URL: {BASE_URL}/gestion/\n")
                f.write(f"Usuario: {USERNAME}\n\n")
                f.write("RESULTADOS:\n")
                f.write("-" * 60 + "\n")
                
                for check_name, check_result in checks.items():
                    status = "OK" if check_result else "FAIL"
                    f.write(f"{status:6} - {check_name}\n")
                
                f.write("-" * 60 + "\n")
                f.write(f"Total: {passed}/{total} ({percentage:.1f}%)\n")
            
            print_success("Resultados guardados: dashboard_manual_verification.txt")
            
            # Conclusión
            print_header("🎯 CONCLUSIÓN")
            
            if percentage >= 80:
                print(f"{Colors.GREEN}{Colors.BOLD}🎉 DASHBOARD FUNCIONANDO EXCELENTE!{Colors.END}")
            elif percentage >= 60:
                print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  DASHBOARD FUNCIONAL CON ADVERTENCIAS{Colors.END}")
            else:
                print(f"{Colors.RED}{Colors.BOLD}❌ DASHBOARD REQUIERE ATENCIÓN{Colors.END}")
            
    except Exception as e:
        print_error(f"Error durante verificación: {str(e)}")
        import traceback
        traceback.print_exc()


# ==================== MAIN ====================

def main():
    """Función principal"""
    print_header("🎯 VERIFICACIÓN MANUAL GUIADA - DASHBOARD LINO")
    print_info("Este script te guiará paso a paso para verificar el dashboard")
    print_info("El navegador se abrirá en modo visible para que puedas ver todo")
    print("")
    print(f"📍 {Colors.BOLD}Servidor:{Colors.END} {BASE_URL}")
    print(f"👤 {Colors.BOLD}Usuario:{Colors.END} {USERNAME}")
    print(f"🔑 {Colors.BOLD}Password:{Colors.END} {PASSWORD}")
    print("")
    print_info("Prepárate para interactuar con el navegador")
    wait_user()
    
    verify_dashboard()
    
    print_header("✅ VERIFICACIÓN COMPLETADA")
    print_info("Revisa:")
    print_info("  - dashboard_production_screenshot.png")
    print_info("  - dashboard_manual_verification.txt")


if __name__ == "__main__":
    main()
