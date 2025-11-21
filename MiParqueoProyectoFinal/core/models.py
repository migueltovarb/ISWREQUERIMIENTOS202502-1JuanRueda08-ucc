from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class EspacioParqueadero(models.Model):
    """
    Modelo que representa un espacio de parqueadero en la universidad.
    Cada espacio tiene un número único, tipo y estado actual.
    """
    TIPO_CHOICES = [
        ('CARRO', 'Carro'),
        ('MOTO', 'Moto'),
        ('DISCAPACIDAD', 'Discapacidad'),
    ]
    
    ESTADO_CHOICES = [
        ('LIBRE', 'Libre'),
        ('RESERVADO', 'Reservado'),
        ('OCUPADO', 'Ocupado'),
        ('BLOQUEADO', 'Bloqueado'),
    ]
    
    numero = models.IntegerField(unique=True, verbose_name='Número de espacio')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo de espacio')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='LIBRE', verbose_name='Estado')
    
    class Meta:
        verbose_name = 'Espacio de Parqueadero'
        verbose_name_plural = 'Espacios de Parqueadero'
        ordering = ['numero']
    
    def __str__(self):
        return f"Espacio {self.numero} - {self.tipo} ({self.estado})"


class Reserva(models.Model):
    """
    Modelo que representa una reserva de espacio de parqueadero.
    Gestiona todo el ciclo de vida de una reserva desde su creación hasta su finalización.
    """
    TIPO_VEHICULO_CHOICES = [
        ('CARRO', 'Carro'),
        ('MOTO', 'Moto'),
    ]
    
    ESTADO_CHOICES = [
        ('RESERVADA', 'Reservada'),
        ('CANCELADA', 'Cancelada'),
        ('COMPLETADA', 'Completada'),
        ('VENCIDA', 'Vencida'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    espacio = models.ForeignKey(EspacioParqueadero, on_delete=models.CASCADE, verbose_name='Espacio')
    fecha = models.DateField(verbose_name='Fecha de reserva')
    hora_inicio = models.TimeField(verbose_name='Hora de inicio')
    hora_fin = models.TimeField(verbose_name='Hora de fin')
    tipo_vehiculo = models.CharField(max_length=10, choices=TIPO_VEHICULO_CHOICES, verbose_name='Tipo de vehículo')
    placa = models.CharField(max_length=10, verbose_name='Placa del vehículo')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='RESERVADA', verbose_name='Estado')
    
    # Campos para registrar entrada y salida del vehículo
    hora_entrada = models.TimeField(null=True, blank=True, verbose_name='Hora de entrada real')
    hora_salida = models.TimeField(null=True, blank=True, verbose_name='Hora de salida real')
    
    # Campos de auditoría
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Creado en')
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name='Actualizado en')
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha', '-hora_inicio']
    
    def __str__(self):
        return f"Reserva {self.id} - {self.usuario.username} - Espacio {self.espacio.numero} ({self.estado})"
    
    def clean(self):
        """
        Validación personalizada para evitar conflictos de horario
        """
        # Validar que hora_fin sea mayor que hora_inicio
        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de fin debe ser posterior a la hora de inicio.')
        
        # Validar que el tipo de vehículo sea compatible con el espacio
        if self.tipo_vehiculo == 'CARRO' and self.espacio.tipo == 'MOTO':
            raise ValidationError('No se puede reservar un espacio de moto para un carro.')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Incidencia(models.Model):
    """
    Modelo para registrar incidencias y situaciones irregulares en el parqueadero.
    Permite al vigilante reportar problemas diversos.
    """
    TIPO_CHOICES = [
        ('SIN_RESERVA', 'Vehículo sin reserva'),
        ('DANIO_ESPACIO', 'Daño en espacio'),
        ('OCUPACION_INDEBIDA', 'Ocupación indebida'),
        ('OTRO', 'Otro'),
    ]
    
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name='Tipo de incidencia')
    espacio = models.ForeignKey(
        EspacioParqueadero, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Espacio relacionado'
    )
    descripcion = models.TextField(verbose_name='Descripción')
    reportado_por = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Reportado por')
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora del reporte')
    
    class Meta:
        verbose_name = 'Incidencia'
        verbose_name_plural = 'Incidencias'
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"Incidencia {self.id} - {self.tipo} ({self.fecha_hora.strftime('%Y-%m-%d %H:%M')})"
