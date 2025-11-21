from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, date, timedelta
from .models import EspacioParqueadero, Reserva, Incidencia


# ============================================================
# VISTA DE LOGIN PERSONALIZADA Y REDIRECCIÓN POR ROL
# ============================================================

class CustomLoginView(LoginView):
    """
    Vista de login personalizada que redirige según el rol del usuario:
    - Superuser → home (puede acceder a /admin/ manualmente)
    - Vigilante → vista de validar placa
    - Cliente → vista de disponibilidad
    """
    template_name = 'login.html'
    
    def get_success_url(self):
        user = self.request.user
        
        # Si pertenece al grupo VIGILANTE
        if user.groups.filter(name='VIGILANTE').exists():
            return '/vigilante/validar-placa/'
        
        # Usuario normal (cliente) o superuser - ambos van a disponibilidad
        return '/cliente/disponibilidad/'


@login_required
def home_view(request):
    """
    Vista principal que redirige según el rol del usuario.
    Esta vista se ejecuta cuando se ingresa a LOGIN_REDIRECT_URL.
    Todos los usuarios (incluido superuser) van a la misma vista home.
    """
    user = request.user
    
    # Si pertenece al grupo VIGILANTE
    if user.groups.filter(name='VIGILANTE').exists():
        return redirect('vigilante_validar_placa')
    
    # Usuario normal (cliente) o superuser - ambos van a disponibilidad
    return redirect('cliente_disponibilidad')


# ============================================================
# VISTAS PARA CLIENTE
# ============================================================

@login_required
def cliente_disponibilidad(request):
    """
    HU 007 – Consultar disponibilidad de espacios
    Muestra todos los espacios con su estado actual.
    Solo los espacios LIBRES pueden ser reservados.
    """
    espacios = EspacioParqueadero.objects.all()
    
    context = {
        'espacios': espacios,
        'es_cliente': True,
    }
    return render(request, 'cliente/disponibilidad.html', context)


@login_required
def cliente_crear_reserva(request, espacio_id):
    """
    HU 008 – Crear reserva
    Formulario para crear una nueva reserva de espacio.
    Valida conflictos de horario y tipo de vehículo.
    """
    espacio = get_object_or_404(EspacioParqueadero, id=espacio_id)
    
    # Verificar que el espacio esté libre
    if espacio.estado != 'LIBRE':
        messages.error(request, 'El espacio seleccionado no está disponible.')
        return redirect('cliente_disponibilidad')
    
    if request.method == 'POST':
        # Obtener datos del formulario
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        tipo_vehiculo = request.POST.get('tipo_vehiculo')
        placa = request.POST.get('placa').upper()
        
        # Validaciones básicas
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            hora_inicio_obj = datetime.strptime(hora_inicio, '%H:%M').time()
            hora_fin_obj = datetime.strptime(hora_fin, '%H:%M').time()
            
            # Validar que la fecha sea hoy o futura
            if fecha_obj < date.today():
                messages.error(request, 'No se pueden hacer reservas para fechas pasadas.')
                return redirect('cliente_crear_reserva', espacio_id=espacio_id)
            
            # Validar que hora_fin sea mayor que hora_inicio
            if hora_inicio_obj >= hora_fin_obj:
                messages.error(request, 'La hora de fin debe ser posterior a la hora de inicio.')
                return redirect('cliente_crear_reserva', espacio_id=espacio_id)
            
            # Validar compatibilidad de vehículo con espacio
            if tipo_vehiculo == 'CARRO' and espacio.tipo == 'MOTO':
                messages.error(request, 'No se puede reservar un espacio de moto para un carro.')
                return redirect('cliente_crear_reserva', espacio_id=espacio_id)
            
            # Validar conflictos de horario para el mismo espacio
            reservas_conflicto = Reserva.objects.filter(
                espacio=espacio,
                fecha=fecha_obj,
                estado='RESERVADA'
            ).filter(
                Q(hora_inicio__lt=hora_fin_obj, hora_fin__gt=hora_inicio_obj)
            )
            
            if reservas_conflicto.exists():
                messages.error(request, 'Ya existe una reserva en ese horario para este espacio.')
                return redirect('cliente_crear_reserva', espacio_id=espacio_id)
            
            # Crear la reserva
            reserva = Reserva.objects.create(
                usuario=request.user,
                espacio=espacio,
                fecha=fecha_obj,
                hora_inicio=hora_inicio_obj,
                hora_fin=hora_fin_obj,
                tipo_vehiculo=tipo_vehiculo,
                placa=placa,
                estado='RESERVADA'
            )
            
            # Cambiar estado del espacio a RESERVADO
            espacio.estado = 'RESERVADO'
            espacio.save()
            
            messages.success(request, f'Reserva creada exitosamente para el espacio {espacio.numero}.')
            return redirect('cliente_reservas_activas')
            
        except Exception as e:
            messages.error(request, f'Error al crear la reserva: {str(e)}')
            return redirect('cliente_crear_reserva', espacio_id=espacio_id)
    
    context = {
        'espacio': espacio,
        'fecha_minima': date.today().isoformat(),
        'es_cliente': True,
    }
    return render(request, 'cliente/crear_reserva.html', context)


@login_required
def cliente_reservas_activas(request):
    """
    HU 010 – Cancelar reserva
    Muestra las reservas activas del usuario que pueden ser canceladas.
    """
    # Obtener reservas activas (RESERVADA) del usuario
    reservas = Reserva.objects.filter(
        usuario=request.user,
        estado='RESERVADA'
    ).select_related('espacio')
    
    context = {
        'reservas': reservas,
        'es_cliente': True,
    }
    return render(request, 'cliente/reservas_activas.html', context)


@login_required
def cliente_cancelar_reserva(request, reserva_id):
    """
    HU 010 – Cancelar reserva
    Cancela una reserva activa (cambia estado a CANCELADA).
    """
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    
    # Validar que la reserva esté en estado RESERVADA
    if reserva.estado != 'RESERVADA':
        messages.error(request, 'Solo se pueden cancelar reservas activas.')
        return redirect('cliente_reservas_activas')
    
    # Validar que no haya iniciado (no tenga hora_entrada)
    if reserva.hora_entrada:
        messages.error(request, 'No se puede cancelar una reserva que ya ha iniciado.')
        return redirect('cliente_reservas_activas')
    
    # Cancelar la reserva
    reserva.estado = 'CANCELADA'
    reserva.save()
    
    # Liberar el espacio
    espacio = reserva.espacio
    espacio.estado = 'LIBRE'
    espacio.save()
    
    messages.success(request, f'Reserva #{reserva.id} cancelada exitosamente.')
    return redirect('cliente_reservas_activas')


@login_required
def cliente_historial(request):
    """
    HU 011 – Ver historial de reservas
    Muestra todas las reservas del usuario con todos los estados.
    """
    reservas = Reserva.objects.filter(
        usuario=request.user
    ).select_related('espacio').order_by('-fecha', '-hora_inicio')
    
    context = {
        'reservas': reservas,
        'es_cliente': True,
    }
    return render(request, 'cliente/historial.html', context)


# ============================================================
# VISTAS PARA VIGILANTE
# ============================================================

@login_required
def vigilante_validar_placa(request):
    """
    HU 015 – Validar reserva por placa
    El vigilante ingresa una placa y se muestra la reserva activa correspondiente.
    """
    reserva = None
    placa_buscada = None
    
    if request.method == 'POST':
        placa = request.POST.get('placa', '').upper().strip()
        placa_buscada = placa
        
        if placa:
            # Buscar reserva activa para la fecha de hoy
            hoy = date.today()
            reservas = Reserva.objects.filter(
                placa=placa,
                fecha=hoy,
                estado='RESERVADA'
            ).select_related('espacio', 'usuario')
            
            if reservas.exists():
                reserva = reservas.first()
                messages.success(request, f'Reserva encontrada para la placa {placa}.')
            else:
                messages.warning(request, f'No se encontró ninguna reserva activa para la placa {placa} en la fecha de hoy.')
        else:
            messages.error(request, 'Por favor ingrese una placa válida.')
    
    context = {
        'reserva': reserva,
        'placa_buscada': placa_buscada,
        'es_vigilante': True,
    }
    return render(request, 'vigilante/validar_placa.html', context)


@login_required
def vigilante_registrar_entrada(request, reserva_id):
    """
    HU 016 – Registrar entrada de vehículo
    Registra la hora de entrada real y cambia el estado del espacio a OCUPADO.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    # Validar que la reserva esté activa
    if reserva.estado != 'RESERVADA':
        messages.error(request, 'Esta reserva no está activa.')
        return redirect('vigilante_validar_placa')
    
    # Validar que no tenga ya una entrada registrada
    if reserva.hora_entrada:
        messages.warning(request, 'Esta reserva ya tiene una entrada registrada.')
        return redirect('vigilante_validar_placa')
    
    # Registrar hora de entrada
    now = timezone.localtime(timezone.now())
    reserva.hora_entrada = now.time()
    reserva.save()
    
    # Cambiar estado del espacio a OCUPADO
    espacio = reserva.espacio
    espacio.estado = 'OCUPADO'
    espacio.save()
    
    messages.success(request, f'Entrada registrada exitosamente para la placa {reserva.placa} a las {now.strftime("%H:%M")}.')
    return redirect('vigilante_validar_placa')


@login_required
def vigilante_salida(request):
    """
    HU 017 – Registrar salida de vehículo
    Muestra las reservas con entrada registrada y sin salida.
    Permite registrar la salida del vehículo.
    """
    # Obtener reservas con entrada pero sin salida
    reservas_en_uso = Reserva.objects.filter(
        estado='RESERVADA',
        hora_entrada__isnull=False,
        hora_salida__isnull=True
    ).select_related('espacio', 'usuario')
    
    context = {
        'reservas': reservas_en_uso,
        'es_vigilante': True,
    }
    return render(request, 'vigilante/salida.html', context)


@login_required
def vigilante_registrar_salida(request, reserva_id):
    """
    HU 017 – Registrar salida de vehículo
    Registra la salida, libera el espacio y completa la reserva.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    # Validar que tenga entrada registrada
    if not reserva.hora_entrada:
        messages.error(request, 'Esta reserva no tiene entrada registrada.')
        return redirect('vigilante_salida')
    
    # Validar que no tenga salida ya registrada
    if reserva.hora_salida:
        messages.warning(request, 'Esta reserva ya tiene salida registrada.')
        return redirect('vigilante_salida')
    
    # Registrar hora de salida
    now = timezone.localtime(timezone.now())
    reserva.hora_salida = now.time()
    reserva.estado = 'COMPLETADA'
    reserva.save()
    
    # Liberar el espacio
    espacio = reserva.espacio
    espacio.estado = 'LIBRE'
    espacio.save()
    
    messages.success(request, f'Salida registrada exitosamente para la placa {reserva.placa} a las {now.strftime("%H:%M")}.')
    return redirect('vigilante_salida')


@login_required
def vigilante_ocupacion(request):
    """
    HU 018 – Ver ocupación actual del parqueadero
    Muestra todos los espacios con su estado actual.
    """
    espacios = EspacioParqueadero.objects.all()
    
    # Estadísticas
    total = espacios.count()
    libres = espacios.filter(estado='LIBRE').count()
    ocupados = espacios.filter(estado='OCUPADO').count()
    reservados = espacios.filter(estado='RESERVADO').count()
    bloqueados = espacios.filter(estado='BLOQUEADO').count()
    
    context = {
        'espacios': espacios,
        'total': total,
        'libres': libres,
        'ocupados': ocupados,
        'reservados': reservados,
        'bloqueados': bloqueados,
        'es_vigilante': True,
    }
    return render(request, 'vigilante/ocupacion.html', context)


# ============================================================
# VISTAS PARA INCIDENCIAS (VIGILANTE Y ADMIN)
# ============================================================

@login_required
def registrar_incidencia(request):
    """
    Vista para registrar una nueva incidencia.
    Disponible para vigilantes y administradores.
    """
    # Verificar que el usuario sea vigilante o superuser
    es_vigilante = request.user.groups.filter(name='VIGILANTE').exists()
    es_admin = request.user.is_superuser
    
    if not (es_vigilante or es_admin):
        messages.error(request, 'No tiene permisos para registrar incidencias.')
        return redirect('home')
    
    espacios = EspacioParqueadero.objects.all().order_by('numero')
    
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        espacio_id = request.POST.get('espacio')
        descripcion = request.POST.get('descripcion', '').strip()
        
        # Validaciones
        if not tipo:
            messages.error(request, 'Debe seleccionar un tipo de incidencia.')
            return redirect('registrar_incidencia')
        
        if not descripcion:
            messages.error(request, 'Debe proporcionar una descripción.')
            return redirect('registrar_incidencia')
        
        # Obtener espacio si se seleccionó uno
        espacio = None
        if espacio_id:
            try:
                espacio = EspacioParqueadero.objects.get(id=espacio_id)
            except EspacioParqueadero.DoesNotExist:
                pass
        
        # Crear la incidencia
        incidencia = Incidencia.objects.create(
            tipo=tipo,
            espacio=espacio,
            descripcion=descripcion,
            reportado_por=request.user
        )
        
        messages.success(request, f'Incidencia #{incidencia.id} registrada exitosamente.')
        return redirect('listar_incidencias')
    
    context = {
        'espacios': espacios,
        'es_vigilante': es_vigilante or es_admin,  # Superuser también ve menú de vigilante
    }
    return render(request, 'vigilante/registrar_incidencia.html', context)


@login_required
def listar_incidencias(request):
    """
    Vista para listar todas las incidencias.
    Disponible para vigilantes y administradores.
    """
    # Verificar que el usuario sea vigilante o superuser
    es_vigilante = request.user.groups.filter(name='VIGILANTE').exists()
    es_admin = request.user.is_superuser
    
    if not (es_vigilante or es_admin):
        messages.error(request, 'No tiene permisos para ver incidencias.')
        return redirect('home')
    
    # Obtener todas las incidencias
    incidencias = Incidencia.objects.all().select_related('espacio', 'reportado_por').order_by('-fecha_hora')
    
    # Filtrar por tipo si se proporciona
    tipo_filtro = request.GET.get('tipo')
    if tipo_filtro:
        incidencias = incidencias.filter(tipo=tipo_filtro)
    
    # Estadísticas por tipo (usar todas las incidencias, no solo las filtradas)
    todas_incidencias = Incidencia.objects.all()
    stats = {
        'SIN_RESERVA': todas_incidencias.filter(tipo='SIN_RESERVA').count(),
        'DANIO_ESPACIO': todas_incidencias.filter(tipo='DANIO_ESPACIO').count(),
        'OCUPACION_INDEBIDA': todas_incidencias.filter(tipo='OCUPACION_INDEBIDA').count(),
        'OTRO': todas_incidencias.filter(tipo='OTRO').count(),
    }
    
    context = {
        'incidencias': incidencias,
        'tipo_filtro': tipo_filtro,
        'stats': stats,
        'es_vigilante': es_vigilante or es_admin,  # Superuser también ve menú de vigilante
    }
    return render(request, 'vigilante/listar_incidencias.html', context)
