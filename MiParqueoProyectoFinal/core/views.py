from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, date, timedelta
from .models import EspacioParqueadero, Reserva, Incidencia
from .utils import generar_qr_reserva


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
        
        # Si es superuser, va al panel de administración
        if user.is_superuser:
            return '/admin-panel/'
        
        # Si pertenece al grupo VIGILANTE
        if user.groups.filter(name='VIGILANTE').exists():
            return '/vigilante/validar-placa/'
        
        # Usuario normal (cliente)
        return '/cliente/disponibilidad/'


@login_required
def home_view(request):
    """
    Vista principal que redirige según el rol del usuario.
    Esta vista se ejecuta cuando se ingresa a LOGIN_REDIRECT_URL.
    """
    user = request.user
    
    # Si es superuser, va al panel de administración
    if user.is_superuser:
        return redirect('admin_panel_dashboard')
    
    # Si pertenece al grupo VIGILANTE
    if user.groups.filter(name='VIGILANTE').exists():
        return redirect('vigilante_validar_placa')
    
    # Usuario normal (cliente)
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
            
            # Generar código QR para la reserva
            try:
                ruta_qr = generar_qr_reserva(reserva)
                reserva.codigo_qr = ruta_qr
                reserva.save()
            except Exception as e:
                # Si falla la generación del QR, continuar sin QR
                # La reserva ya fue creada exitosamente
                print(f"Error al generar QR: {str(e)}")
            
            # Cambiar estado del espacio a RESERVADO
            espacio.estado = 'RESERVADO'
            espacio.save()
            
            messages.success(request, f'Reserva creada exitosamente para el espacio {espacio.numero}. Código QR generado.')
            return redirect('cliente_confirmacion_reserva', reserva_id=reserva.id)
            
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


@login_required
def cliente_confirmacion_reserva(request, reserva_id):
    """
    Vista de confirmación después de crear una reserva.
    Muestra el código QR generado y los detalles de la reserva.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    
    context = {
        'reserva': reserva,
        'es_cliente': True,
    }
    return render(request, 'cliente/confirmacion_reserva.html', context)


@login_required
def cliente_modificar_reserva(request, reserva_id):
    """
    Permite al cliente modificar una reserva existente.
    Reglas:
    1. Solo reservas propias y en estado RESERVADA.
    2. Modificación permitida solo si faltan > 15 minutos para el inicio.
    3. Nuevo horario no debe solaparse con otras reservas.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    
    # Validar estado
    if reserva.estado != 'RESERVADA':
        messages.error(request, 'Solo se pueden modificar reservas activas.')
        return redirect('cliente_historial')
    
    # Validar tiempo mínimo (15 min antes)
    ahora = timezone.now()
    inicio_reserva = timezone.make_aware(datetime.combine(reserva.fecha, reserva.hora_inicio))
    tiempo_restante = inicio_reserva - ahora
    
    if tiempo_restante.total_seconds() < 900:  # 15 minutos * 60 segundos
        messages.error(request, 'No puede modificar una reserva a menos de 15 minutos de su inicio.')
        return redirect('cliente_historial')
        
    if request.method == 'POST':
        nueva_fecha_str = request.POST.get('fecha')
        nueva_hora_inicio_str = request.POST.get('hora_inicio')
        nueva_hora_fin_str = request.POST.get('hora_fin')
        
        try:
            nueva_fecha = datetime.strptime(nueva_fecha_str, '%Y-%m-%d').date()
            nueva_hora_inicio = datetime.strptime(nueva_hora_inicio_str, '%H:%M').time()
            nueva_hora_fin = datetime.strptime(nueva_hora_fin_str, '%H:%M').time()
            
            # Re-validar tiempo mínimo con la fecha original (por seguridad)
            if tiempo_restante.total_seconds() < 900:
                messages.error(request, 'El tiempo límite para modificar ha expirado.')
                return redirect('cliente_historial')
                
            # Validar que la nueva fecha/hora sea futura
            nuevo_inicio = timezone.make_aware(datetime.combine(nueva_fecha, nueva_hora_inicio))
            if nuevo_inicio <= ahora:
                messages.error(request, 'La nueva fecha y hora deben ser futuras.')
            else:
                # Validar solapamiento (excluyendo la reserva actual)
                solapamiento = Reserva.objects.filter(
                    espacio=reserva.espacio,
                    fecha=nueva_fecha,
                    estado='RESERVADA'
                ).exclude(id=reserva.id).filter(
                    Q(hora_inicio__lt=nueva_hora_fin) & Q(hora_fin__gt=nueva_hora_inicio)
                ).exists()
                
                if solapamiento:
                    messages.error(request, 'El espacio no está disponible en el nuevo horario seleccionado.')
                else:
                    # Todo válido, guardar cambios
                    reserva.fecha = nueva_fecha
                    reserva.hora_inicio = nueva_hora_inicio
                    reserva.hora_fin = nueva_hora_fin
                    
                    # Regenerar QR con los nuevos datos
                    try:
                        ruta_qr = generar_qr_reserva(reserva)
                        reserva.codigo_qr = ruta_qr
                    except Exception as e:
                        print(f"Error al regenerar QR: {str(e)}")
                        
                    reserva.save()
                    messages.success(request, 'Reserva modificada exitosamente.')
                    return redirect('cliente_historial')
                    
        except ValueError:
            messages.error(request, 'Formato de fecha u hora inválido.')
            
    context = {
        'reserva': reserva,
        'fecha_actual_iso': reserva.fecha.strftime('%Y-%m-%d'),
        'hora_inicio_iso': reserva.hora_inicio.strftime('%H:%M'),
        'hora_fin_iso': reserva.hora_fin.strftime('%H:%M'),
        'min_date': date.today().strftime('%Y-%m-%d'),
    }
    return render(request, 'cliente/modificar_reserva.html', context)


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


# ============================================================
# VISTAS PARA PANEL DE ADMINISTRACIÓN
# ============================================================

from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import user_passes_test

def es_superuser(user):
    """Verifica que el usuario sea superuser"""
    return user.is_superuser

@login_required
@user_passes_test(es_superuser)
def admin_panel_dashboard(request):
    """
    Dashboard principal del panel de administración.
    Muestra estadísticas generales del sistema.
    """
    # Estadísticas
    total_usuarios = User.objects.count()
    usuarios_activos = User.objects.filter(is_active=True).count()
    usuarios_inactivos = User.objects.filter(is_active=False).count()
    
    total_espacios = EspacioParqueadero.objects.count()
    espacios_disponibles = EspacioParqueadero.objects.filter(estado='DISPONIBLE').count()
    espacios_ocupados = EspacioParqueadero.objects.filter(estado='OCUPADO').count()
    
    total_reservas = Reserva.objects.count()
    reservas_activas = Reserva.objects.filter(estado='RESERVADA').count()
    reservas_completadas = Reserva.objects.filter(estado='COMPLETADA').count()
    
    context = {
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'usuarios_inactivos': usuarios_inactivos,
        'total_espacios': total_espacios,
        'espacios_disponibles': espacios_disponibles,
        'espacios_ocupados': espacios_ocupados,
        'total_reservas': total_reservas,
        'reservas_activas': reservas_activas,
        'reservas_completadas': reservas_completadas,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@user_passes_test(es_superuser)
def admin_usuarios_listar(request):
    """
    Lista todos los usuarios con búsqueda y filtros.
    """
    usuarios = User.objects.all().order_by('-date_joined')
    
    # Búsqueda
    search = request.GET.get('search', '')
    if search:
        usuarios = usuarios.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Filtro por estado
    estado = request.GET.get('estado', '')
    if estado == 'activo':
        usuarios = usuarios.filter(is_active=True)
    elif estado == 'inactivo':
        usuarios = usuarios.filter(is_active=False)
    
    # Filtro por rol
    rol = request.GET.get('rol', '')
    if rol == 'vigilante':
        usuarios = usuarios.filter(groups__name='VIGILANTE')
    elif rol == 'cliente':
        usuarios = usuarios.exclude(groups__name='VIGILANTE').exclude(is_superuser=True)
    elif rol == 'admin':
        usuarios = usuarios.filter(is_superuser=True)
    
    # Pre-calcular roles para evitar lógica compleja en el template
    usuarios_con_rol = []
    for usuario in usuarios:
        if usuario.is_superuser:
            usuario.rol_display = 'admin'
        elif usuario.groups.filter(name='VIGILANTE').exists():
            usuario.rol_display = 'vigilante'
        else:
            usuario.rol_display = 'cliente'
        usuarios_con_rol.append(usuario)
    
    context = {
        'usuarios': usuarios_con_rol,
        'search': search,
        'estado': estado,
        'rol': rol,
    }
    return render(request, 'admin_panel/usuarios/listar.html', context)


@login_required
@user_passes_test(es_superuser)
def admin_usuarios_crear(request):
    """
    Crea un nuevo usuario.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        rol = request.POST.get('rol')
        
        # Validaciones
        if not all([username, email, password, password_confirm]):
            messages.error(request, 'Todos los campos obligatorios deben ser completados.')
        elif password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado.')
        else:
            # Crear usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Asignar rol
            if rol == 'vigilante':
                grupo_vigilante, _ = Group.objects.get_or_create(name='VIGILANTE')
                user.groups.add(grupo_vigilante)
            elif rol == 'admin':
                user.is_superuser = True
                user.is_staff = True
                user.save()
            
            messages.success(request, f'Usuario {username} creado exitosamente.')
            return redirect('admin_usuarios_listar')
    
    return render(request, 'admin_panel/usuarios/crear.html')


@login_required
@user_passes_test(es_superuser)
def admin_usuarios_editar(request, user_id):
    """
    Edita un usuario existente.
    """
    usuario = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        usuario.username = request.POST.get('username')
        usuario.email = request.POST.get('email')
        usuario.first_name = request.POST.get('first_name')
        usuario.last_name = request.POST.get('last_name')
        
        # Cambiar contraseña solo si se proporciona
        new_password = request.POST.get('new_password')
        if new_password:
            usuario.set_password(new_password)
        
        # Actualizar rol
        rol = request.POST.get('rol')
        usuario.groups.clear()
        
        if rol == 'vigilante':
            grupo_vigilante, _ = Group.objects.get_or_create(name='VIGILANTE')
            usuario.groups.add(grupo_vigilante)
            usuario.is_superuser = False
            usuario.is_staff = False
        elif rol == 'admin':
            usuario.is_superuser = True
            usuario.is_staff = True
        else:  # cliente
            usuario.is_superuser = False
            usuario.is_staff = False
        
        usuario.save()
        messages.success(request, f'Usuario {usuario.username} actualizado exitosamente.')
        return redirect('admin_usuarios_listar')
    
    # Determinar rol actual
    if usuario.is_superuser:
        rol_actual = 'admin'
    elif usuario.groups.filter(name='VIGILANTE').exists():
        rol_actual = 'vigilante'
    else:
        rol_actual = 'cliente'
    
    context = {
        'usuario': usuario,
        'rol_actual': rol_actual,
    }
    return render(request, 'admin_panel/usuarios/editar.html', context)


@login_required
@user_passes_test(es_superuser)
def admin_usuarios_toggle_estado(request, user_id):
    """
    Activa o desactiva un usuario.
    """
    usuario = get_object_or_404(User, id=user_id)
    
    # No permitir desactivar al propio usuario
    if usuario.id == request.user.id:
        messages.error(request, 'No puedes desactivar tu propia cuenta.')
        return redirect('admin_usuarios_listar')
    
    usuario.is_active = not usuario.is_active
    usuario.save()
    
    estado = 'activado' if usuario.is_active else 'desactivado'
    messages.success(request, f'Usuario {usuario.username} {estado} exitosamente.')
    
    return redirect('admin_usuarios_listar')


# ============================================================
# GESTIÓN DE ESPACIOS DE PARQUEADERO (ADMIN)
# ============================================================

@login_required
@user_passes_test(es_superuser)
def admin_espacios_listar(request):
    """
    Lista todos los espacios de parqueadero con búsqueda y filtros.
    """
    espacios = EspacioParqueadero.objects.all().order_by('numero')
    
    # Búsqueda por número
    search = request.GET.get('search', '')
    if search:
        espacios = espacios.filter(numero__icontains=search)
    
    # Filtro por estado
    estado = request.GET.get('estado', '')
    if estado:
        espacios = espacios.filter(estado=estado)
    
    context = {
        'espacios': espacios,
        'search': search,
        'estado': estado,
    }
    return render(request, 'admin_panel/espacios/listar.html', context)


@login_required
@user_passes_test(es_superuser)
def admin_espacios_crear(request):
    """
    Crea un nuevo espacio de parqueadero.
    """
    if request.method == 'POST':
        numero = request.POST.get('numero')
        estado = request.POST.get('estado', 'DISPONIBLE')
        
        # Validaciones
        if not numero:
            messages.error(request, 'El número de espacio es obligatorio.')
        elif EspacioParqueadero.objects.filter(numero=numero).exists():
            messages.error(request, f'El espacio {numero} ya existe.')
        else:
            # Crear espacio
            EspacioParqueadero.objects.create(
                numero=numero,
                estado=estado
            )
            messages.success(request, f'Espacio {numero} creado exitosamente.')
            return redirect('admin_espacios_listar')
    
    return render(request, 'admin_panel/espacios/crear.html')


@login_required
@user_passes_test(es_superuser)
def admin_espacios_editar(request, espacio_id):
    """
    Edita un espacio de parqueadero existente.
    """
    espacio = get_object_or_404(EspacioParqueadero, id=espacio_id)
    
    if request.method == 'POST':
        numero = request.POST.get('numero')
        estado = request.POST.get('estado')
        
        # Validar que el número no esté en uso por otro espacio
        if EspacioParqueadero.objects.filter(numero=numero).exclude(id=espacio_id).exists():
            messages.error(request, f'El número {numero} ya está en uso por otro espacio.')
        else:
            espacio.numero = numero
            espacio.estado = estado
            espacio.save()
            
            messages.success(request, f'Espacio {numero} actualizado exitosamente.')
            return redirect('admin_espacios_listar')
    
    context = {
        'espacio': espacio,
    }
    return render(request, 'admin_panel/espacios/editar.html', context)

