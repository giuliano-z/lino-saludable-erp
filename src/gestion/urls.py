from django.urls import path

from . import views
from .api import api_inventario, api_productos, api_ventas
from .views_compras import (
    api_costo_receta,
    crear_compra,
    detalle_compra,
    eliminar_compra,
    lista_compras,
)
from .views_productos import (
    crear_materia_prima,
    crear_producto,
    detalle_materia_prima,
    detalle_producto,
    editar_materia_prima,
    editar_producto,
    eliminar_producto,
    exportar_materias_primas_excel,
    exportar_productos,
    lista_inventario,
    lista_materias_primas,
    lista_productos,
    movimiento_materia_prima,
    reporte_costos_produccion,
    reporte_stock_materias_primas,
)

# ==================== IMPORTS DE MÓDULOS SEPARADOS ====================
from .views_recetas import (
    crear_receta,
    detalle_receta,
    editar_receta,
    eliminar_receta,
    lista_recetas,
)
from .views_ventas import (
    crear_venta,
    crear_venta_con_materias,
    detalle_venta,
    eliminar_venta,
    exportar_ventas,
    lista_ventas,
)

app_name = 'gestion'

urlpatterns = [
    # Dashboard principal - ahora usa la versión inteligente verde
    path('', views.dashboard_inteligente, name='panel_control'),
    # Versiones alternativas del dashboard
    path('dashboard-original/', views.panel_control_original, name='panel_control_original'),
    path('dashboard-clean/', views.panel_control_clean, name='panel_control_clean'),
    path('dashboard-minimal/', views.panel_control_minimal, name='panel_control_minimal'),
    path('dashboard-inteligente/', views.dashboard_inteligente, name='dashboard_inteligente'),

    # ==================== PRODUCTOS ====================
    path('productos/', lista_productos, name='lista_productos'),
    path('productos/crear/', crear_producto, name='crear_producto'),
    path('productos/<int:pk>/', detalle_producto, name='detalle_producto'),
    path('productos/<int:pk>/editar/', editar_producto, name='editar_producto'),
    path('productos/<int:pk>/eliminar/', eliminar_producto, name='eliminar_producto'),
    path('productos/exportar/', exportar_productos, name='exportar_productos'),

    # ==================== VENTAS ====================
    path('ventas/', lista_ventas, name='lista_ventas'),
    path('ventas/crear/', crear_venta, name='crear_venta'),
    path('ventas/<int:pk>/', detalle_venta, name='detalle_venta'),
    path('ventas/<int:pk>/eliminar/', eliminar_venta, name='eliminar_venta'),
    path('ventas/exportar/', exportar_ventas, name='exportar_ventas'),
    path('ventas/con-materias/', crear_venta_con_materias, name='crear_venta_con_materias'),

    # ==================== COMPRAS ====================
    path('compras/', lista_compras, name='lista_compras'),
    path('compras/crear/', crear_compra, name='crear_compra'),
    path('compras/<int:pk>/', detalle_compra, name='detalle_compra'),
    path('compras/<int:pk>/eliminar/', eliminar_compra, name='eliminar_compra'),

    # ==================== MATERIAS PRIMAS ====================
    path('materias-primas/', lista_materias_primas, name='lista_materias_primas'),
    path('materias-primas/crear/', crear_materia_prima, name='crear_materia_prima'),
    path('materias-primas/<int:pk>/editar/', editar_materia_prima, name='editar_materia_prima'),
    path('materias-primas/<int:pk>/detalle/', detalle_materia_prima, name='detalle_materia_prima'),
    path('materias-primas/<int:pk>/movimiento/', movimiento_materia_prima, name='movimiento_materia_prima'),
    path('inventario/', lista_inventario, name='lista_inventario'),

    # ==================== RECETAS ====================
    path('recetas/', lista_recetas, name='lista_recetas'),
    path('recetas/crear/', crear_receta, name='crear_receta'),
    path('recetas/<int:pk>/', detalle_receta, name='detalle_receta'),
    path('recetas/<int:pk>/editar/', editar_receta, name='editar_receta'),
    path('recetas/<int:pk>/eliminar/', eliminar_receta, name='eliminar_receta'),

    # ==================== REPORTES ====================
    path('reportes/', views.reportes_lino, name='reportes'),
    path('reportes/stock-materias-primas/', reporte_stock_materias_primas, name='reporte_stock_materias_primas'),
    path('reportes/costos-produccion/', reporte_costos_produccion, name='reporte_costos_produccion'),

    # ==================== EXPORTACIÓN ====================
    path('exportar/materias-primas/excel/', exportar_materias_primas_excel, name='exportar_materias_primas_excel'),
    path('exportar/reporte/<str:tipo_reporte>/pdf/', views.exportar_reporte_pdf, name='exportar_reporte_pdf'),

    # ==================== API ENDPOINTS ====================
    path('api/productos/<int:pk>/precio/', views.producto_precio, name='producto_precio'),
    path('api/verificar-stock/<int:producto_id>/', views.api_verificar_stock_producto, name='api_verificar_stock_producto'),
    path('api/receta/<int:pk>/costo/', api_costo_receta, name='api_costo_receta'),
    path('api/productos/', api_productos, name='api_productos'),
    path('api/inventario/', api_inventario, name='api_inventario'),
    path('api/ventas/', api_ventas, name='api_ventas'),

    # ==================== CONFIGURACIÓN ====================
    path('gastos-inversiones/', views.gastos_inversiones, name='gastos_inversiones'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('configuracion/negocio/', views.configuracion_negocio, name='configuracion_negocio'),

    # ==================== SISTEMA DE ALERTAS ====================
    path('alertas/', views.alertas_lista, name='alertas_lista'),
    path('api/alertas/count/', views.alertas_count_api, name='alertas_count'),
    path('api/alertas/no-leidas/', views.alertas_no_leidas_api, name='alertas_no_leidas'),
    path('api/alertas/<int:alerta_id>/marcar-leida/', views.marcar_alerta_leida, name='marcar_alerta_leida'),

    # ==================== RENTABILIDAD ====================
    path('rentabilidad/', views.dashboard_rentabilidad, name='dashboard_rentabilidad'),
    path('rentabilidad/producto/<int:producto_id>/', views.detalle_rentabilidad_producto, name='detalle_rentabilidad_producto'),
    path('api/alertas-rentabilidad/', views.alertas_rentabilidad_ajax, name='alertas_rentabilidad_ajax'),
    path('api/recomendaciones-precios/', views.recomendaciones_precios_ajax, name='recomendaciones_precios_ajax'),
    path('api/aplicar-precio/<int:producto_id>/', views.aplicar_precio_sugerido, name='aplicar_precio_sugerido'),

    # ==================== AJUSTES DE INVENTARIO ====================
    path('ajustes/', views.lista_ajustes, name='lista_ajustes'),
    path('ajustes/productos/crear/', views.crear_ajuste_producto, name='crear_ajuste_producto'),
    path('ajustes/productos/<int:producto_id>/crear/', views.crear_ajuste_producto, name='crear_ajuste_producto_directo'),
    path('ajustes/materias-primas/crear/', views.crear_ajuste_materia_prima, name='crear_ajuste_materia_prima'),
    path('ajustes/materias-primas/<int:mp_id>/crear/', views.crear_ajuste_materia_prima, name='crear_ajuste_mp_directo'),
    path('ajustes/<int:pk>/', views.detalle_ajuste, name='detalle_ajuste'),

    # ==================== VISTAS MIGRADAS/LINO V3 (LEGACY) ====================
    path('demo/componentes/', views.demo_componentes, name='demo_componentes'),
    path('productos/lino/', views.lista_productos_lino, name='lista_productos_lino'),
    path('ventas/lino/', views.lista_ventas_lino, name='lista_ventas_lino'),
    path('compras/lino/', views.lista_compras_lino, name='lista_compras_lino'),
]
