"""
Script de verificación del sistema MiParqueo
Ejecutar con: python verificar_sistema.py
"""

import os
import sys
import django

# Configurar encoding para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_parqueo.settings')
django.setup()

from django.contrib.auth.models import User, Group
from core.models import EspacioParqueadero, Reserva, Incidencia

def verificar_sistema():
    print("=" * 70)
    print("VERIFICACION DEL SISTEMA MIPARQUEO")
    print("=" * 70)
    
    errores = []
    advertencias = []
    
    # 1. Verificar grupo VIGILANTE
    print("\n[1] Verificando grupo VIGILANTE...")
    try:
        grupo = Group.objects.get(name='VIGILANTE')
        print(f"    [OK] Grupo VIGILANTE existe (ID: {grupo.id})")
    except Group.DoesNotExist:
        error = "Grupo VIGILANTE no existe"
        print(f"    [ERROR] {error}")
        errores.append(error)
    
    # 2. Verificar superusuario
    print("\n[2] Verificando superusuario...")
    superusers = User.objects.filter(is_superuser=True)
    if superusers.exists():
        print(f"    [OK] {superusers.count()} superusuario(s) encontrado(s)")
        for su in superusers:
            print(f"         - {su.username}")
    else:
        adv = "No hay superusuario - Ejecute: python manage.py createsuperuser"
        print(f"    [AVISO] {adv}")
        advertencias.append(adv)
    
    # 3. Verificar usuarios vigilantes
    print("\n[3] Verificando usuarios vigilantes...")
    try:
        grupo = Group.objects.get(name='VIGILANTE')
        vigilantes = grupo.user_set.all()
        if vigilantes.exists():
            print(f"    [OK] {vigilantes.count()} vigilante(s) registrado(s)")
            for v in vigilantes:
                print(f"         - {v.username}")
        else:
            adv = "No hay usuarios vigilantes"
            print(f"    [AVISO] {adv}")
            advertencias.append(adv)
    except:
        pass
    
    # 4. Verificar usuarios clientes
    print("\n[4] Verificando usuarios clientes...")
    clientes = User.objects.filter(is_superuser=False, is_staff=False)
    if clientes.exists():
        print(f"    [OK] {clientes.count()} cliente(s) registrado(s)")
        for c in clientes[:5]:  # Mostrar solo los primeros 5
            print(f"         - {c.username}")
        if clientes.count() > 5:
            print(f"         ... y {clientes.count() - 5} mas")
    else:
        adv = "No hay usuarios clientes"
        print(f"    [AVISO] {adv}")
        advertencias.append(adv)
    
    # 5. Verificar espacios de parqueadero
    print("\n[5] Verificando espacios de parqueadero...")
    espacios = EspacioParqueadero.objects.all()
    if espacios.exists():
        print(f"    [OK] {espacios.count()} espacio(s) de parqueadero")
        
        carros = espacios.filter(tipo='CARRO').count()
        motos = espacios.filter(tipo='MOTO').count()
        discapacidad = espacios.filter(tipo='DISCAPACIDAD').count()
        
        print(f"         - Carros: {carros}")
        print(f"         - Motos: {motos}")
        print(f"         - Discapacidad: {discapacidad}")
        
        libres = espacios.filter(estado='LIBRE').count()
        ocupados = espacios.filter(estado='OCUPADO').count()
        reservados = espacios.filter(estado='RESERVADO').count()
        bloqueados = espacios.filter(estado='BLOQUEADO').count()
        
        print(f"         Estados: L:{libres} O:{ocupados} R:{reservados} B:{bloqueados}")
    else:
        error = "No hay espacios de parqueadero - Ejecute: python init_data.py"
        print(f"    [ERROR] {error}")
        errores.append(error)
    
    # 6. Verificar reservas
    print("\n[6] Verificando reservas...")
    reservas = Reserva.objects.all()
    print(f"    [INFO] {reservas.count()} reserva(s) en el sistema")
    
    if reservas.exists():
        estados = {}
        for estado in ['RESERVADA', 'COMPLETADA', 'CANCELADA', 'VENCIDA']:
            count = reservas.filter(estado=estado).count()
            if count > 0:
                estados[estado] = count
        
        if estados:
            print("         Estados:")
            for estado, count in estados.items():
                print(f"         - {estado}: {count}")
    
    # 7. Verificar incidencias
    print("\n[7] Verificando incidencias...")
    incidencias = Incidencia.objects.all()
    print(f"    [INFO] {incidencias.count()} incidencia(s) reportada(s)")
    
    # 8. Verificar archivos de templates
    print("\n[8] Verificando templates...")
    templates_necesarios = [
        'templates/base.html',
        'templates/login.html',
        'templates/cliente/disponibilidad.html',
        'templates/cliente/crear_reserva.html',
        'templates/cliente/reservas_activas.html',
        'templates/cliente/historial.html',
        'templates/vigilante/validar_placa.html',
        'templates/vigilante/salida.html',
        'templates/vigilante/ocupacion.html',
    ]
    
    templates_ok = 0
    for template in templates_necesarios:
        if os.path.exists(template):
            templates_ok += 1
        else:
            error = f"Template faltante: {template}"
            print(f"    [ERROR] {error}")
            errores.append(error)
    
    print(f"    [OK] {templates_ok}/{len(templates_necesarios)} templates encontrados")
    
    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE VERIFICACION")
    print("=" * 70)
    
    if errores:
        print(f"\n[!] {len(errores)} ERROR(ES) ENCONTRADO(S):")
        for i, error in enumerate(errores, 1):
            print(f"    {i}. {error}")
    
    if advertencias:
        print(f"\n[!] {len(advertencias)} ADVERTENCIA(S):")
        for i, adv in enumerate(advertencias, 1):
            print(f"    {i}. {adv}")
    
    if not errores and not advertencias:
        print("\n[OK] Sistema completamente verificado!")
        print("[OK] Todo esta listo para usar MiParqueo")
    elif not errores:
        print("\n[OK] Sistema funcional con advertencias menores")
    else:
        print("\n[ERROR] Hay errores criticos que deben corregirse")
    
    print("\n" + "=" * 70)
    print("Para iniciar el sistema, ejecute:")
    print("  python manage.py runserver")
    print("=" * 70)

if __name__ == '__main__':
    try:
        verificar_sistema()
    except Exception as e:
        print(f"\n[ERROR CRITICO] {str(e)}")
        import traceback
        traceback.print_exc()

