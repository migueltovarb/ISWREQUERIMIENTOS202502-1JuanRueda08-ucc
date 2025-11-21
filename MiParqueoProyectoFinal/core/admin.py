from django.contrib import admin
from .models import EspacioParqueadero, Reserva, Incidencia


@admin.register(EspacioParqueadero)
class EspacioParqueaderoAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para los espacios de parqueadero.
    """
    list_display = ('numero', 'tipo', 'estado')
    list_filter = ('tipo', 'estado')
    search_fields = ('numero',)
    ordering = ('numero',)
    list_editable = ('estado',)
    
    fieldsets = (
        ('Información del Espacio', {
            'fields': ('numero', 'tipo', 'estado')
        }),
    )


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para las reservas.
    Muestra información completa y permite filtrar por diferentes criterios.
    """
    list_display = (
        'id', 
        'usuario', 
        'espacio', 
        'fecha', 
        'hora_inicio', 
        'hora_fin', 
        'placa',
        'tipo_vehiculo',
        'estado'
    )
    list_filter = ('estado', 'fecha', 'tipo_vehiculo')
    search_fields = ('usuario__username', 'placa', 'espacio__numero')
    ordering = ('-fecha', '-hora_inicio')
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información de la Reserva', {
            'fields': ('usuario', 'espacio', 'fecha')
        }),
        ('Horario', {
            'fields': ('hora_inicio', 'hora_fin')
        }),
        ('Información del Vehículo', {
            'fields': ('tipo_vehiculo', 'placa')
        }),
        ('Estado y Control', {
            'fields': ('estado', 'hora_entrada', 'hora_salida')
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('creado_en', 'actualizado_en')


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para las incidencias.
    """
    list_display = ('id', 'tipo', 'espacio', 'reportado_por', 'fecha_hora')
    list_filter = ('tipo', 'fecha_hora')
    search_fields = ('descripcion', 'reportado_por__username')
    ordering = ('-fecha_hora',)
    date_hierarchy = 'fecha_hora'
    
    fieldsets = (
        ('Información de la Incidencia', {
            'fields': ('tipo', 'espacio', 'descripcion')
        }),
        ('Reporte', {
            'fields': ('reportado_por', 'fecha_hora')
        }),
    )
    
    readonly_fields = ('fecha_hora',)
