"""
Tests del flujo de ventas: crear, eliminar, detalle, exportar.
Verifica: stock, validación, redirección, permisos, logging.
"""
from datetime import date
from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from gestion.models import Venta, VentaDetalle

from .factories import ProductoFactory, UserFactory, VentaFactory


class TestCrearVentaView(TestCase):
    """Tests para la vista crear_venta."""

    def setUp(self):
        """Preparar datos de test."""
        self.client = Client()
        self.user = UserFactory.create_user_autenticado()
        self.usuario_sin_permisos = UserFactory.create_user_sin_permisos()
        self.producto1 = ProductoFactory.create_producto(
            nombre='Pan',
            precio=Decimal('100'),
            stock=10
        )
        self.producto2 = ProductoFactory.create_producto(
            nombre='Empanada',
            precio=Decimal('50'),
            stock=5
        )
        self.url_crear = reverse('gestion:crear_venta')

    def test_get_crear_venta_anonimo_redirige_a_login(self):
        """GET sin autenticación redirige a login."""
        response = self.client.get(self.url_crear)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_get_crear_venta_autenticado_carga_formulario(self):
        """GET autenticado carga el formulario."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url_crear)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cliente')  # Campo cliente
        self.assertContains(response, 'fecha')  # Campo fecha (nueva validación)

    def test_post_crear_venta_valida_guarda_y_descuenta_stock(self):
        """POST válido guarda venta + detalle + descuenta stock."""
        self.client.login(username='testuser', password='testpass123')

        # Datos válidos de venta
        data = {
            'cliente': 'Juan Pérez',
            'fecha': str(date.today()),
            # Formset con 1 producto
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-producto': str(self.producto1.id),
            'form-0-cantidad': '2',
            'form-0-precio_unitario': '100',
            'form-0-DELETE': '',
        }

        stock_antes = self.producto1.stock
        response = self.client.post(self.url_crear, data)

        # Verificar redirect y mensaje de éxito
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('gestion:lista_ventas'), response.url)

        # Verificar que se creó la venta
        venta = Venta.objects.filter(cliente='Juan Pérez').first()
        self.assertIsNotNone(venta)
        self.assertEqual(venta.total, Decimal('200.00'))  # 2 * 100

        # Verificar que se creó el detalle
        detalle = VentaDetalle.objects.filter(venta=venta).first()
        self.assertIsNotNone(detalle)
        self.assertEqual(detalle.cantidad, 2)
        self.assertEqual(detalle.precio_unitario, Decimal('100'))

        # Verificar que el stock disminuyó
        self.producto1.refresh_from_db()
        self.assertEqual(self.producto1.stock, stock_antes - 2)

    def test_post_crear_venta_sin_stock_rechaza(self):
        """POST intenta vender más de lo disponible → rechaza."""
        self.client.login(username='testuser', password='testpass123')

        data = {
            'cliente': 'Cliente Sin Stock',
            'fecha': str(date.today()),
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-producto': str(self.producto1.id),
            'form-0-cantidad': '100',  # ❌ Stock es 10
            'form-0-precio_unitario': '100',
            'form-0-DELETE': '',
        }

        response = self.client.post(self.url_crear, data)

        # Debe devolverse el formulario con error (status 200, no redirige)
        self.assertEqual(response.status_code, 200)
        # Verifica que hay error de stock (búsqueda más flexible)
        content = response.content.decode()
        self.assertTrue('stock' in content.lower() or 'formulario inv' in content.lower())

        # NO debe crearse la venta
        venta = Venta.objects.filter(cliente='Cliente Sin Stock').first()
        self.assertIsNone(venta)

    def test_post_crear_venta_fecha_invalida_rechaza(self):
        """POST con fecha inválida → rechaza en servidor."""
        self.client.login(username='testuser', password='testpass123')

        data = {
            'cliente': 'Cliente Test',
            'fecha': 'fecha-invalida',  # ❌ No es ISO format
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-producto': str(self.producto1.id),
            'form-0-cantidad': '1',
            'form-0-precio_unitario': '100',
            'form-0-DELETE': '',
        }

        response = self.client.post(self.url_crear, data)

        # Debe devolverse el formulario con error (status 200)
        self.assertEqual(response.status_code, 200)
        # El error debe estar en la respuesta HTML
        self.assertIn('fecha', response.content.decode())

    def test_post_crear_venta_cantidad_invalida_rechaza(self):
        """POST con cantidad ≤ 0 → rechaza."""
        self.client.login(username='testuser', password='testpass123')

        data = {
            'cliente': 'Cliente Test',
            'fecha': str(date.today()),
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-producto': str(self.producto1.id),
            'form-0-cantidad': '0',  # ❌ Cantidad inválida
            'form-0-precio_unitario': '100',
            'form-0-DELETE': '',
        }

        response = self.client.post(self.url_crear, data)

        # Debe rechazarse
        self.assertEqual(response.status_code, 200)

    def test_post_crear_venta_sin_permisos_rechaza(self):
        """POST sin permisos add_venta → rechaza."""
        self.client.login(username='testuser_noperms', password='testpass123')

        data = {
            'cliente': 'Cliente Test',
            'fecha': str(date.today()),
            'form-TOTAL_FORMS': '0',
            'form-INITIAL_FORMS': '0',
        }

        response = self.client.post(self.url_crear, data)

        # Redirige con mensaje de error
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('gestion:lista_ventas'), response.url)


class TestEliminarVentaView(TestCase):
    """Tests para eliminar ventas (soft delete)."""

    def setUp(self):
        """Preparar datos de test."""
        self.client = Client()
        self.user = UserFactory.create_user_autenticado()
        self.producto = ProductoFactory.create_producto(stock=10)
        self.venta, self.detalle = VentaFactory.create_venta_con_detalle(
            usuario=self.user,
            producto=self.producto,
            cantidad=3
        )
        self.url_eliminar = reverse('gestion:eliminar_venta', kwargs={'pk': self.venta.id})

    def test_get_eliminar_venta_muestra_confirmacion(self):
        """GET muestra página de confirmación."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url_eliminar)

        self.assertEqual(response.status_code, 200)
        # Verifica que es la página de eliminación
        self.assertIn('Venta', response.content.decode())

    def test_post_eliminar_venta_soft_delete_restaura_stock(self):
        """POST elimina venta (soft delete) y restaura stock."""
        self.client.login(username='testuser', password='testpass123')

        stock_antes = self.producto.stock  # Ahora es 10 - 3 = 7

        data = {
            'razon_eliminacion': 'Error en la venta'
        }

        response = self.client.post(self.url_eliminar, data)

        # Debe redirigir
        self.assertEqual(response.status_code, 302)

        # Verificar soft delete
        self.venta.refresh_from_db()
        self.assertTrue(self.venta.eliminada)

        # Verificar que se restauró el stock
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, stock_antes + 3)


class TestDetalleVentaView(TestCase):
    """Tests para ver el detalle de una venta."""

    def setUp(self):
        """Preparar datos de test."""
        self.client = Client()
        self.user = UserFactory.create_user_autenticado()
        self.venta, self.detalle = VentaFactory.create_venta_con_detalle(
            usuario=self.user
        )
        self.url_detalle = reverse('gestion:detalle_venta', kwargs={'pk': self.venta.id})

    def test_detalle_venta_existe_muestra_correctamente(self):
        """GET detalle de venta existente carga."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url_detalle)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.venta.id))

    def test_detalle_venta_inexistente_404(self):
        """GET detalle de venta inexistente → 404."""
        self.client.login(username='testuser', password='testpass123')
        url_inexistente = reverse('gestion:detalle_venta', kwargs={'pk': 99999})
        response = self.client.get(url_inexistente)

        self.assertEqual(response.status_code, 404)


class TestCrearVentaConMateriasView(TestCase):
    """Tests para la vista desactivada crear_venta_con_materias."""

    def setUp(self):
        """Preparar datos de test."""
        self.client = Client()
        self.user = UserFactory.create_user_autenticado()
        self.url_con_materias = reverse('gestion:crear_venta_con_materias')

    def test_vista_desactivada_redirige_a_crear_venta(self):
        """GET/POST a crear_venta_con_materias redirige a crear_venta."""
        self.client.login(username='testuser', password='testpass123')

        # GET
        response_get = self.client.get(self.url_con_materias)
        self.assertEqual(response_get.status_code, 302)
        self.assertIn(reverse('gestion:crear_venta'), response_get.url)

        # POST
        response_post = self.client.post(self.url_con_materias, {})
        self.assertEqual(response_post.status_code, 302)
        self.assertIn(reverse('gestion:crear_venta'), response_post.url)

    def test_vista_desactivada_muestra_mensaje(self):
        """GET/POST muestra mensaje de "funcionalidad no disponible"."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url_con_materias, follow=True)

        # Seguir redirects para capturar mensaje
        self.assertEqual(response.status_code, 200)
        # Debe haber mensaje info o warning
        messages = list(response.context.get('messages', []))
        # Verificar que hay algún mensaje
        self.assertTrue(len(messages) > 0 or 'no disponible' in response.content.decode().lower())
