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
]

