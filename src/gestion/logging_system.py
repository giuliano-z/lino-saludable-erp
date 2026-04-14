"""
Sistema de logging personalizado para LINO SALUDABLE
Maneja todas las operaciones críticas de negocio con logging detallado
"""
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from django.contrib.auth.models import User

# ==================== CONFIGURACIÓN DE LOGGERS ====================
business_logger = logging.getLogger('lino.business')
ventas_logger = logging.getLogger('lino.ventas')
stock_logger = logging.getLogger('lino.stock')

class LinoLogger:
    """
    Clase centralizada para manejar todos los logs de negocio de LINO
    """

    # Atributos de clase para los loggers
    business_logger = business_logger
    ventas_logger = ventas_logger
    stock_logger = stock_logger

    @staticmethod
    def log_venta_creada(venta_id: int, producto_nombre: str, cantidad: int,
                        total: Decimal, usuario: Optional[User] = None):
        """Log cuando se crea una venta exitosa"""
        usuario_name = usuario.username if usuario else "Sistema"
        ventas_logger.info(
            f"VENTA CREADA - ID: {venta_id} | Producto: {producto_nombre} | "
            f"Cantidad: {cantidad} | Total: ${total} | Usuario: {usuario_name}"
        )

    @staticmethod
    def log_venta_error(producto_nombre: str, cantidad: int, error_msg: str,
                       usuario: Optional[User] = None):
        """Log cuando falla la creación de una venta"""
        usuario_name = usuario.username if usuario else "Sistema"
        ventas_logger.error(
            f"VENTA FALLIDA - Producto: {producto_nombre} | Cantidad: {cantidad} | "
            f"Error: {error_msg} | Usuario: {usuario_name}"
        )

    @staticmethod
    def log_stock_actualizado(producto_nombre: str, stock_anterior: int,
                             stock_nuevo: int, motivo: str, usuario: Optional[User] = None):
        """Log cuando se actualiza el stock de un producto"""
        usuario_name = usuario.username if usuario else "Sistema"
        diferencia = stock_nuevo - stock_anterior
        operacion = "INCREMENTO" if diferencia > 0 else "DECREMENTO"

        stock_logger.info(
            f"STOCK {operacion} - Producto: {producto_nombre} | "
            f"Stock Anterior: {stock_anterior} | Stock Nuevo: {stock_nuevo} | "
            f"Diferencia: {diferencia} | Motivo: {motivo} | Usuario: {usuario_name}"
        )

    @staticmethod
    def log_stock_critico(producto_nombre: str, stock_actual: int, stock_minimo: int):
        """Log cuando un producto llega a stock crítico"""
        stock_logger.warning(
            f"STOCK CRÍTICO - Producto: {producto_nombre} | "
            f"Stock Actual: {stock_actual} | Stock Mínimo: {stock_minimo} | "
            f"¡REQUIERE REPOSICIÓN INMEDIATA!"
        )

    @staticmethod
    def log_stock_agotado(producto_nombre: str):
        """Log cuando un producto se agota"""
        stock_logger.error(
            f"STOCK AGOTADO - Producto: {producto_nombre} | "
            f"¡PRODUCTO SIN STOCK - VENTAS BLOQUEADAS!"
        )

    @staticmethod
    def log_precio_actualizado(producto_nombre: str, precio_anterior: Decimal,
                              precio_nuevo: Decimal, usuario: Optional[User] = None):
        """Log cuando se actualiza el precio de un producto"""
        usuario_name = usuario.username if usuario else "Sistema"
        diferencia = precio_nuevo - precio_anterior
        porcentaje = (diferencia / precio_anterior * 100) if precio_anterior > 0 else 0

        business_logger.info(
            f"PRECIO ACTUALIZADO - Producto: {producto_nombre} | "
            f"Precio Anterior: ${precio_anterior} | Precio Nuevo: ${precio_nuevo} | "
            f"Diferencia: ${diferencia} | Cambio: {porcentaje:.2f}% | Usuario: {usuario_name}"
        )

    @staticmethod
    def log_compra_registrada(materia_prima_nombre: str, cantidad: Decimal,
                             precio_total: Decimal, proveedor: str, usuario: Optional[User] = None):
        """Log cuando se registra una compra de materia prima"""
        usuario_name = usuario.username if usuario else "Sistema"
        precio_unitario = precio_total / cantidad if cantidad > 0 else Decimal('0')

        business_logger.info(
            f"COMPRA REGISTRADA - Materia Prima: {materia_prima_nombre} | "
            f"Cantidad: {cantidad} | Precio Total: ${precio_total} | "
            f"Precio Unitario: ${precio_unitario} | Proveedor: {proveedor} | Usuario: {usuario_name}"
        )

    @staticmethod
    def log_error_critico(modulo: str, funcion: str, error_msg: str,
                         contexto: Optional[Dict[Any, Any]] = None):
        """Log para errores críticos del sistema"""
        contexto_str = f" | Contexto: {contexto}" if contexto else ""
        business_logger.error(
            f"ERROR CRÍTICO - Módulo: {modulo} | Función: {funcion} | "
            f"Error: {error_msg}{contexto_str}"
        )

    @staticmethod
    def log_login_usuario(usuario: User, ip_address: str = ""):
        """Log cuando un usuario inicia sesión"""
        business_logger.info(
            f"LOGIN EXITOSO - Usuario: {usuario.username} | "
            f"Email: {usuario.email} | IP: {ip_address} | "
            f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    @staticmethod
    def log_accion_admin(usuario: User, accion: str, modelo: str, objeto_id: int):
        """Log para acciones administrativas importantes"""
        business_logger.info(
            f"ACCIÓN ADMIN - Usuario: {usuario.username} | Acción: {accion} | "
            f"Modelo: {modelo} | ID: {objeto_id}"
        )

# ==================== DECORADOR PARA LOGGING AUTOMÁTICO ====================
def log_business_operation(operation_name: str, logger_type: str = 'business'):
    """
    Decorador para automatizar el logging de operaciones de negocio
    
    Args:
        operation_name: Nombre de la operación (ej: "crear_venta", "actualizar_stock")
        logger_type: Tipo de logger ('business', 'ventas', 'stock')
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Determinar el logger apropiado
            logger_map = {
                'business': business_logger,
                'ventas': ventas_logger,
                'stock': stock_logger
            }
            logger = logger_map.get(logger_type, business_logger)

            # Log del inicio de la operación
            logger.info(f"INICIANDO {operation_name.upper()} - Args: {args[1:]} | Kwargs: {kwargs}")

            try:
                # Ejecutar la función original
                result = func(*args, **kwargs)

                # Log del éxito
                logger.info(f"ÉXITO {operation_name.upper()} - Resultado: {type(result).__name__}")
                return result

            except Exception as e:
                # Log del error
                logger.error(f"ERROR {operation_name.upper()} - Excepción: {str(e)}")
                raise  # Re-lanzar la excepción

        return wrapper
    return decorator

# ==================== FUNCIÓN PARA VERIFICAR LOGS ====================
def verificar_logs_funcionando():
    """Función para verificar que el sistema de logging funciona correctamente"""
    try:
        business_logger.info("✅ Sistema de logging inicializado correctamente")
        ventas_logger.info("✅ Logger de ventas funcionando")
        stock_logger.info("✅ Logger de stock funcionando")

        print("🟢 Sistema de logging LINO configurado exitosamente")
        print("📁 Logs se guardan en: src/logs/")
        print("   - errors.log: Errores generales")
        print("   - business.log: Operaciones de negocio")
        print("   - ventas.log: Registro de ventas")
        print("   - stock.log: Movimientos de stock")

        return True

    except Exception as e:
        print(f"❌ Error configurando logging: {str(e)}")
        return False

# ==================== UTILES PARA DEBUGGING ====================
def get_request_info(request):
    """Extrae información útil de una request para logging"""
    return {
        'user': request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'Anónimo',
        'ip': request.META.get('REMOTE_ADDR', ''),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'method': request.method,
        'path': request.path,
    }
