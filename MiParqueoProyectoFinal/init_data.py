"""
Script de inicialización de datos para MiParqueo
Ejecutar con: python init_data.py
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
from core.models import EspacioParqueadero

def crear_datos_iniciales():
    print("=" * 60)
    print("INICIALIZANDO DATOS DEL SISTEMA MIPARQUEO")
    print("=" * 60)
    
    # 1. Crear grupo VIGILANTE
    print("\n1. Creando grupo VIGILANTE...")
    grupo_vigilante, created = Group.objects.get_or_create(name='VIGILANTE')
    if created:
        print("   [OK] Grupo VIGILANTE creado exitosamente")
    else:
        print("   [INFO] Grupo VIGILANTE ya existe")
    
    # 2. Crear superusuario (si no existe)
    print("\n2. Verificando superusuario...")
    if not User.objects.filter(is_superuser=True).exists():
        print("   [AVISO] No hay superusuario en el sistema.")
        print("   [AVISO] Ejecute: python manage.py createsuperuser")
    else:
        admin = User.objects.filter(is_superuser=True).first()
        print(f"   [OK] Superusuario existe: {admin.username}")
    
    # 3. Crear usuario vigilante de prueba
    print("\n3. Creando usuario vigilante de prueba...")
    if not User.objects.filter(username='vigilante').exists():
        vigilante = User.objects.create_user(
            username='vigilante',
            password='vigilante123',
            email='vigilante@miparqueo.com',
            first_name='Juan',
            last_name='Vigilante'
        )
        vigilante.groups.add(grupo_vigilante)
        print("   [OK] Usuario 'vigilante' creado")
        print("     Usuario: vigilante")
        print("     Contraseña: vigilante123")
    else:
        vigilante = User.objects.get(username='vigilante')
        vigilante.groups.add(grupo_vigilante)
        print("   [INFO] Usuario 'vigilante' ya existe")
    
    # 4. Crear usuarios clientes de prueba
    print("\n4. Creando usuarios clientes de prueba...")
    clientes_data = [
        {'username': 'cliente1', 'password': 'cliente123', 'first_name': 'Maria', 'last_name': 'Gonzalez'},
        {'username': 'cliente2', 'password': 'cliente123', 'first_name': 'Carlos', 'last_name': 'Rodriguez'},
        {'username': 'cliente3', 'password': 'cliente123', 'first_name': 'Ana', 'last_name': 'Martinez'},
    ]
    
    for cliente_data in clientes_data:
        if not User.objects.filter(username=cliente_data['username']).exists():
            User.objects.create_user(
                username=cliente_data['username'],
                password=cliente_data['password'],
                email=f"{cliente_data['username']}@miparqueo.com",
                first_name=cliente_data['first_name'],
                last_name=cliente_data['last_name']
            )
            print(f"   [OK] Cliente '{cliente_data['username']}' creado")
        else:
            print(f"   [INFO] Cliente '{cliente_data['username']}' ya existe")
    
    print("\n   Todos los clientes tienen contraseña: cliente123")
    
    # 5. Crear espacios de parqueadero
    print("\n5. Creando espacios de parqueadero...")
    if EspacioParqueadero.objects.count() == 0:
        espacios = []
        
        # 20 espacios para carros (1-20)
        for i in range(1, 21):
            espacios.append(EspacioParqueadero(
                numero=i,
                tipo='CARRO',
                estado='LIBRE'
            ))
        
        # 10 espacios para motos (21-30)
        for i in range(21, 31):
            espacios.append(EspacioParqueadero(
                numero=i,
                tipo='MOTO',
                estado='LIBRE'
            ))
        
        # 3 espacios para discapacidad (31-33)
        for i in range(31, 34):
            espacios.append(EspacioParqueadero(
                numero=i,
                tipo='DISCAPACIDAD',
                estado='LIBRE'
            ))
        
        EspacioParqueadero.objects.bulk_create(espacios)
        print(f"   [OK] {len(espacios)} espacios de parqueadero creados")
        print("     - 20 espacios para CARRO (1-20)")
        print("     - 10 espacios para MOTO (21-30)")
        print("     - 3 espacios para DISCAPACIDAD (31-33)")
    else:
        print(f"   [INFO] Ya existen {EspacioParqueadero.objects.count()} espacios")
    
    print("\n" + "=" * 60)
    print("INICIALIZACION COMPLETADA")
    print("=" * 60)
    print("\nCREDENCIALES DE ACCESO:")
    print("\n[*] VIGILANTE:")
    print("   Usuario: vigilante")
    print("   Contraseña: vigilante123")
    print("\n[*] CLIENTES:")
    print("   Usuario: cliente1, cliente2, cliente3")
    print("   Contraseña: cliente123")
    print("\n[*] SUPERUSUARIO:")
    print("   Crear con: python manage.py createsuperuser")
    print("\n[*] Ejecute el servidor con: python manage.py runserver")
    print("=" * 60)

if __name__ == '__main__':
    crear_datos_iniciales()

