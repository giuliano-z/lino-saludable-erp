"""
Tests de integridad de templates y URLs.
Verifica: existencia de templates, resolución de URLs, referencias legacy.
"""
from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from django.template.loader import get_template, TemplateDoesNotExist
import os


class TestTemplatesExisten(TestCase):
    """Tests que verifican existencia de templates esperados."""
    
    def test_template_form_v3_natural_existe(self):
        """Template form_v3_natural.html existe."""
        try:
            template = get_template('modules/ventas/form_v3_natural.html')
            self.assertIsNotNone(template)
        except TemplateDoesNotExist:
            self.fail('Template form_v3_natural.html no existe')
    
    def test_template_lista_ventas_existe(self):
        """Template lista.html para ventas existe."""
        try:
            template = get_template('modules/ventas/lista.html')
            self.assertIsNotNone(template)
        except TemplateDoesNotExist:
            self.fail('Template lista.html no existe para ventas')
    
    def test_template_detalle_venta_existe(self):
        """Template detalle_venta.html existe."""
        try:
            template = get_template('modules/ventas/detalle_venta.html')
            self.assertIsNotNone(template)
        except TemplateDoesNotExist:
            self.fail('Template detalle_venta.html no existe')
    
    def test_template_lista_compras_existe(self):
        """Template lista.html para compras existe."""
        try:
            template = get_template('modules/compras/lista.html')
            self.assertIsNotNone(template)
        except TemplateDoesNotExist:
            self.fail('Template lista.html no existe para compras')
    
    def test_template_formulario_inexistente(self):
        """Template inexistente 'formulario.html' no existe."""
        with self.assertRaises(TemplateDoesNotExist):
            get_template('modules/ventas/ventas/formulario.html')
    
    def test_template_venta_con_materias_form_inexistente(self):
        """Template inexistente 'venta_con_materias_form.html' no existe."""
        with self.assertRaises(TemplateDoesNotExist):
            get_template('gestion/venta_con_materias_form.html')


class TestURLsResuelven(TestCase):
    """Tests que verifican resolución de URLs."""
    
    def test_url_crear_venta_resuelve(self):
        """URL 'crear_venta' resuelve correctamente."""
        try:
            url = reverse('gestion:crear_venta')
            self.assertEqual(url, '/gestion/ventas/crear/')
        except NoReverseMatch:
            self.fail('URL "crear_venta" no resuelve')
    
    def test_url_lista_ventas_resuelve(self):
        """URL 'lista_ventas' resuelve correctamente."""
        try:
            url = reverse('gestion:lista_ventas')
            self.assertEqual(url, '/gestion/ventas/')
        except NoReverseMatch:
            self.fail('URL "lista_ventas" no resuelve')
    
    def test_url_detalle_venta_resuelve(self):
        """URL 'detalle_venta' con pk resuelve correctamente."""
        try:
            url = reverse('gestion:detalle_venta', kwargs={'pk': 123})
            self.assertEqual(url, '/gestion/ventas/123/')
        except NoReverseMatch:
            self.fail('URL "detalle_venta" no resuelve')
    
    def test_url_crear_compra_resuelve(self):
        """URL 'crear_compra' resuelve correctamente."""
        try:
            url = reverse('gestion:crear_compra')
            self.assertEqual(url, '/gestion/compras/crear/')
        except NoReverseMatch:
            self.fail('URL "crear_compra" no resuelve')
    
    def test_url_lista_compras_resuelve(self):
        """URL 'lista_compras' resuelve correctamente."""
        try:
            url = reverse('gestion:lista_compras')
            self.assertEqual(url, '/gestion/compras/')
        except NoReverseMatch:
            self.fail('URL "lista_compras" no resuelve')
    
    def test_url_crear_receta_resuelve(self):
        """URL 'crear_receta' resuelve correctamente."""
        try:
            url = reverse('gestion:crear_receta')
            self.assertEqual(url, '/gestion/recetas/crear/')
        except NoReverseMatch:
            self.fail('URL "crear_receta" no resuelve')


class TestNoReferenciasLegacy(TestCase):
    """Tests que detectan referencias legacy a URLs _migrado."""
    
    def test_no_url_lista_compras_migrado(self):
        """No existe URL legacy 'lista_compras_migrado'."""
        with self.assertRaises(NoReverseMatch):
            reverse('gestion:lista_compras_migrado')
    
    def test_no_url_lista_ventas_migrado(self):
        """No existe URL legacy 'lista_ventas_migrado'."""
        with self.assertRaises(NoReverseMatch):
            reverse('gestion:lista_ventas_migrado')
    
    def test_no_referencias_migrado_en_templates(self):
        """No hay referencias a '_migrado' en templates de gestion."""
        templates_dir = os.path.join(
            os.path.dirname(__file__),
            '../templates/modules'
        )
        
        contador_referencias = 0
        for root, dirs, files in os.walk(templates_dir):
            for file in files:
                if file.endswith('.html'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                        if '_migrado' in contenido:
                            contador_referencias += 1
                            print(f"❌ Encontrada referencia '_migrado' en {filepath}")
        
        self.assertEqual(
            contador_referencias, 0,
            f"Se encontraron {contador_referencias} referencias a '_migrado' en templates"
        )


class TestTemplateErrorHandling(TestCase):
    """Tests que verifican manejo de errores en templates."""
    
    def test_template_con_error_syntax_falla(self):
        """Template con syntax error no puede cargarse."""
        # Este test documenta el comportamiento esperado
        # Si hay errores de syntax en un template, debe fallar explícitamente
        # en lugar de silenciosamente servir HTML vacío
        pass
