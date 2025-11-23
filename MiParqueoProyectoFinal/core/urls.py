from django.urls import path
from . import views

urlpatterns = [
    # Vista home que redirige según el rol
    path('', views.home_view, name='home'),
    
    # URLs para CLIENTE
    path('cliente/disponibilidad/', views.cliente_disponibilidad, name='cliente_disponibilidad'),
    path('cliente/crear-reserva/<int:espacio_id>/', views.cliente_crear_reserva, name='cliente_crear_reserva'),
    path('cliente/reservas-activas/', views.cliente_reservas_activas, name='cliente_reservas_activas'),
    path('cliente/cancelar-reserva/<int:reserva_id>/', views.cliente_cancelar_reserva, name='cliente_cancelar_reserva'),
    path('cliente/historial/', views.cliente_historial, name='cliente_historial'),
    path('cliente/confirmacion/<int:reserva_id>/', views.cliente_confirmacion_reserva, name='cliente_confirmacion_reserva'),
    path('cliente/modificar-reserva/<int:reserva_id>/', views.cliente_modificar_reserva, name='cliente_modificar_reserva'),
    
    # URLs para VIGILANTE
    path('vigilante/validar-placa/', views.vigilante_validar_placa, name='vigilante_validar_placa'),
    path('vigilante/registrar-entrada/<int:reserva_id>/', views.vigilante_registrar_entrada, name='vigilante_registrar_entrada'),
    path('vigilante/salida/', views.vigilante_salida, name='vigilante_salida'),
    path('vigilante/registrar-salida/<int:reserva_id>/', views.vigilante_registrar_salida, name='vigilante_registrar_salida'),
    path('vigilante/ocupacion/', views.vigilante_ocupacion, name='vigilante_ocupacion'),
    
    # URLs para INCIDENCIAS (Vigilante y Admin)
    path('incidencias/registrar/', views.registrar_incidencia, name='registrar_incidencia'),
    path('incidencias/listar/', views.listar_incidencias, name='listar_incidencias'),
    
    # URLs para PANEL DE ADMINISTRACIÓN
    path('admin-panel/', views.admin_panel_dashboard, name='admin_panel_dashboard'),
    
    # Gestión de Usuarios
    path('admin-panel/usuarios/', views.admin_usuarios_listar, name='admin_usuarios_listar'),
    path('admin-panel/usuarios/crear/', views.admin_usuarios_crear, name='admin_usuarios_crear'),
    path('admin-panel/usuarios/editar/<int:user_id>/', views.admin_usuarios_editar, name='admin_usuarios_editar'),
    path('admin-panel/usuarios/toggle/<int:user_id>/', views.admin_usuarios_toggle_estado, name='admin_usuarios_toggle_estado'),
    
    # Gestión de Espacios
    path('admin-panel/espacios/', views.admin_espacios_listar, name='admin_espacios_listar'),
    path('admin-panel/espacios/crear/', views.admin_espacios_crear, name='admin_espacios_crear'),
    path('admin-panel/espacios/editar/<int:espacio_id>/', views.admin_espacios_editar, name='admin_espacios_editar'),
]


