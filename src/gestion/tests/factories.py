"""
Factories para crear datos de test reutilizables.
Evita repetir código setUp en cada test.
"""
from django.contrib.auth.models import User
from gestion.models import (
    MateriaPrima, Producto, ProductoMateriaPrima, Venta, VentaDetalle,
    Compra, Receta, RecetaMateriaPrima
)
from decimal import Decimal
from django.utils import timezone


class UserFactory:
    """Factory para crear usuarios de test."""
    
    @staticmethod
    def create_user_autenticado(username='testuser', password='testpass123'):
        """Crea usuario con permisos para agregar ventas y compras."""
        user = User.objects.create_user(
            username=username,
            email=f'{username}@test.local',
            password=password
        )
        # Agregar permisos básicos
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        ct_venta = ContentType.objects.get_for_model(Venta)
        ct_compra = ContentType.objects.get_for_model(Compra)
        
        # add_venta, delete_venta, export_venta (inventado)
        perm_add_venta = Permission.objects.filter(codename='add_venta', content_type=ct_venta).first()
        perm_delete_venta = Permission.objects.filter(codename='delete_venta', content_type=ct_venta).first()
        
        if perm_add_venta:
            user.user_permissions.add(perm_add_venta)
        if perm_delete_venta:
            user.user_permissions.add(perm_delete_venta)
        
        return user
    
    @staticmethod
    def create_user_sin_permisos(username='testuser_noperms'):
        """Crea usuario sin permisos especiales."""
        return User.objects.create_user(
            username=username,
            password='testpass123'
        )


class MateriaPrimaFactory:
    """Factory para crear materias primas de test."""
    
    @staticmethod
    def create_mp(nombre='Harina', unidad_medida='kg', stock=10, 
                  costo_unitario=Decimal('100'), stock_minimo=2):
        """Crea una materia prima con stock."""
        return MateriaPrima.objects.create(
            nombre=nombre,
            unidad_medida=unidad_medida,
            stock_actual=Decimal(str(stock)),
            costo_unitario=Decimal(str(costo_unitario)),
            stock_minimo=stock_minimo,
            proveedor='Proveedor Test'
        )
    
    @staticmethod
    def create_mp_sin_stock(nombre='Azúcar'):
        """Crea una materia prima sin stock."""
        return MateriaPrimaFactory.create_mp(nombre=nombre, stock=0)


class ProductoFactory:
    """Factory para crear productos de test."""
    
    @staticmethod
    def create_producto(nombre='Pan', precio=Decimal('100'), stock=5, 
                       stock_minimo=1, materia_prima_asociada=None):
        """Crea un producto con stock."""
        return Producto.objects.create(
            nombre=nombre,
            precio=Decimal(str(precio)),
            stock=stock,
            stock_minimo=stock_minimo,
            materia_prima_asociada=materia_prima_asociada,
            tipo_producto='SIMPLE'
        )
    
    @staticmethod
    def create_producto_sin_stock(nombre='Pan Sin Stock'):
        """Crea un producto sin stock."""
        return ProductoFactory.create_producto(nombre=nombre, stock=0)
    
    @staticmethod
    def create_producto_con_mp(nombre='Empanada', mp=None):
        """Crea un producto con materia prima asociada."""
        if not mp:
            mp = MateriaPrimaFactory.create_mp()
        
        producto = Producto.objects.create(
            nombre=nombre,
            precio=Decimal('50'),
            stock=3,
            stock_minimo=1,
            materia_prima_asociada=mp,
            tipo_producto='CON_MP'
        )
        return producto, mp


class RecetaFactory:
    """Factory para crear recetas de test."""
    
    @staticmethod
    def create_receta(nombre='Pastel Base', mp_ingredientes=None):
        """Crea una receta con ingredientes."""
        receta = Receta.objects.create(
            nombre=nombre,
            descripcion='Receta de test',
            tiempo_preparacion='30',
            tipo='postre'
        )
        
        if mp_ingredientes:
            for mp, cantidad in mp_ingredientes:
                RecetaMateriaPrima.objects.create(
                    receta=receta,
                    materia_prima=mp,
                    cantidad_necesaria=Decimal(str(cantidad))
                )
        
        return receta


class VentaFactory:
    """Factory para crear ventas de test."""
    
    @staticmethod
    def create_venta(usuario=None, cliente='Cliente Test', fecha=None):
        """Crea una venta sin detalles."""
        if not usuario:
            usuario = UserFactory.create_user_autenticado()
        if not fecha:
            fecha = timezone.now()
        
        return Venta.objects.create(
            usuario=usuario,
            cliente=cliente,
            fecha=fecha,
            total=Decimal('0.00'),
            eliminada=False
        )
    
    @staticmethod
    def create_venta_con_detalle(usuario=None, producto=None, cantidad=1, 
                                 precio_unitario=Decimal('100')):
        """Crea una venta con un detalle de producto."""
        if not usuario:
            usuario = UserFactory.create_user_autenticado()
        if not producto:
            producto = ProductoFactory.create_producto()
        
        venta = VentaFactory.create_venta(usuario=usuario)
        subtotal = Decimal(str(cantidad)) * Decimal(str(precio_unitario))
        
        detalle = VentaDetalle.objects.create(
            venta=venta,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=Decimal(str(precio_unitario)),
            subtotal=subtotal
        )
        
        venta.total = subtotal
        venta.save()
        
        return venta, detalle


class CompraFactory:
    """Factory para crear compras de test."""
    
    @staticmethod
    def create_compra(materia_prima=None, cantidad=Decimal('10'), 
                      precio_unitario=Decimal('100'), usuario=None):
        """Crea una compra de materia prima con detalles."""
        if not materia_prima:
            materia_prima = MateriaPrimaFactory.create_mp()
        if not usuario:
            usuario = UserFactory.create_user_autenticado()
        
        # Crear compra padre (sin detalles, son legacy compatible)
        compra = Compra.objects.create(
            materia_prima=materia_prima,
            cantidad_mayoreo=cantidad,
            precio_mayoreo=precio_unitario * cantidad,
            precio_unitario_mayoreo=precio_unitario,
            total=precio_unitario * cantidad,
            proveedor='Proveedor Test',
            usuario=usuario
        )
        
        return compra
