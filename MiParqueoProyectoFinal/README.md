# 🚗 MiParqueo - Sistema de Gestión de Parqueaderos Universitarios

Sistema web desarrollado en Django 5 para la gestión de reservas de espacios de parqueadero en una universidad.

## 📋 Características Principales

### Roles del Sistema
- **ADMINISTRADOR**: Gestiona el sistema mediante el panel de Django Admin
- **VIGILANTE**: Valida placas, registra entradas/salidas y controla la ocupación
- **CLIENTE**: Consulta disponibilidad, crea y gestiona reservas

### Funcionalidades por Rol

#### 👤 CLIENTE
- ✅ Consultar disponibilidad de espacios
- ✅ Crear reservas de parqueadero
- ✅ Cancelar reservas (antes de la entrada)
- ✅ Ver historial completo de reservas

#### 🛡️ VIGILANTE
- ✅ Validar reservas por placa
- ✅ Registrar entrada de vehículos
- ✅ Registrar salida de vehículos
- ✅ Ver ocupación actual del parqueadero

#### 🔧 ADMINISTRADOR
- ✅ Gestión completa de espacios
- ✅ Gestión de usuarios y grupos
- ✅ Gestión de reservas
- ✅ Visualización de incidencias

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.8+
- Django 5.2.8 (ya instalado en el venv)

### Configuración Inicial

1. **Activar el entorno virtual** (si no está activado):
```powershell
.\venv\Scripts\Activate.ps1
```

2. **Las migraciones ya están aplicadas**. Si necesita recrearlas:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Los datos iniciales ya están cargados** (vigilante, clientes y espacios). Si necesita recargarlos:
```bash
python init_data.py
```

4. **Crear un superusuario** (para acceder al panel de administración):
```bash
python manage.py createsuperuser
```

5. **Ejecutar el servidor**:
```bash
python manage.py runserver
```

6. **Acceder al sistema**:
- Sistema principal: http://127.0.0.1:8000/
- Panel Admin: http://127.0.0.1:8000/admin/

## 🔑 Credenciales de Prueba

### Vigilante
- **Usuario**: `vigilante`
- **Contraseña**: `vigilante123`
- **Acceso**: Será redirigido a la vista de validación de placas

### Clientes
- **Usuario**: `cliente1`, `cliente2` o `cliente3`
- **Contraseña**: `cliente123`
- **Acceso**: Serán redirigidos a la vista de disponibilidad de espacios

### Administrador
- Crear con: `python manage.py createsuperuser`
- **Acceso**: Será redirigido al panel de Django Admin

## 📁 Estructura del Proyecto

```
mi_parqueo/
│
├── mi_parqueo/              # Configuración del proyecto
│   ├── settings.py          # Configuración principal
│   ├── urls.py              # URLs principales
│   └── wsgi.py
│
├── core/                    # Aplicación principal
│   ├── models.py            # Modelos: EspacioParqueadero, Reserva, Incidencia
│   ├── views.py             # Vistas para Cliente y Vigilante
│   ├── urls.py              # URLs de la aplicación
│   ├── admin.py             # Configuración del admin
│   └── migrations/          # Migraciones de BD
│
├── templates/               # Plantillas HTML
│   ├── base.html            # Template base con Bootstrap
│   ├── login.html           # Página de login
│   ├── cliente/             # Templates del cliente
│   │   ├── disponibilidad.html
│   │   ├── crear_reserva.html
│   │   ├── reservas_activas.html
│   │   └── historial.html
│   └── vigilante/           # Templates del vigilante
│       ├── validar_placa.html
│       ├── salida.html
│       └── ocupacion.html
│
├── db.sqlite3               # Base de datos SQLite
├── manage.py                # Script de gestión de Django
├── init_data.py             # Script de inicialización de datos
└── README.md                # Este archivo
```

## 🗄️ Modelos de Datos

### EspacioParqueadero
- `numero`: Número único del espacio
- `tipo`: CARRO, MOTO o DISCAPACIDAD
- `estado`: LIBRE, RESERVADO, OCUPADO o BLOQUEADO

### Reserva
- Información de usuario y espacio
- Fechas y horarios (planificado y real)
- Datos del vehículo (tipo y placa)
- Estados del ciclo de vida: RESERVADA, CANCELADA, COMPLETADA, VENCIDA

### Incidencia
- Registro de situaciones irregulares
- Tipos: SIN_RESERVA, DAÑO_ESPACIO, OCUPACION_INDEBIDA, OTRO

## 🔄 Flujo de Uso del Sistema

### Para Clientes
1. Ingresar con credenciales de cliente
2. Ver espacios disponibles
3. Seleccionar un espacio LIBRE y crear reserva
4. Proporcionar datos: fecha, horario, tipo de vehículo y placa
5. El sistema valida disponibilidad y crea la reserva
6. Puede cancelar antes de la hora de entrada
7. Vigilante valida placa al ingresar
8. Ver historial completo de reservas

### Para Vigilantes
1. Ingresar con credenciales de vigilante
2. Buscar reserva por placa
3. Si existe reserva activa, registrar entrada
4. El espacio cambia a estado OCUPADO
5. Cuando el vehículo sale, registrar salida
6. El espacio vuelve a LIBRE y reserva se marca COMPLETADA
7. Ver ocupación en tiempo real

### Para Administradores
1. Ingresar al panel admin con credenciales de superusuario
2. Gestionar espacios de parqueadero
3. Ver todas las reservas del sistema
4. Gestionar usuarios y asignar roles
5. Revisar incidencias reportadas

## 🎨 Interfaz de Usuario

- **Framework**: Bootstrap 5.3
- **Iconos**: Bootstrap Icons
- **Responsive**: Diseño adaptable a móviles y tablets
- **Accesibilidad**: Interfaz clara con códigos de color intuitivos:
  - 🟢 Verde: Espacios libres
  - 🟡 Amarillo: Espacios reservados
  - 🔴 Rojo: Espacios ocupados
  - ⚫ Gris: Espacios bloqueados

## 🔐 Seguridad

- ✅ Autenticación requerida para todas las vistas (`@login_required`)
- ✅ Protección CSRF en formularios
- ✅ Redirección automática según rol de usuario
- ✅ Validación de permisos en cada acción
- ✅ Contraseñas hasheadas con algoritmos de Django

## 📊 Datos de Prueba Incluidos

El sistema viene pre-cargado con:
- **1 vigilante**: Para probar funcionalidades de control de acceso
- **3 clientes**: Para probar el flujo de reservas
- **33 espacios**: 20 para carros, 10 para motos, 3 para discapacidad
- **Grupo VIGILANTE**: Configurado y listo para usar

## 🛠️ Comandos Útiles

### Gestión de la Base de Datos
```bash
# Ver datos en la base de datos
python manage.py dbshell

# Crear nuevo superusuario
python manage.py createsuperuser

# Resetear base de datos (¡CUIDADO!)
python manage.py flush
```

### Desarrollo
```bash
# Ejecutar servidor de desarrollo
python manage.py runserver

# Ejecutar en puerto específico
python manage.py runserver 8080

# Acceder desde otra máquina en red local
python manage.py runserver 0.0.0.0:8000
```

### Gestión de Usuarios
```bash
# Crear usuario desde shell
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.create_user('usuario', 'email@example.com', 'password')
```

## 📝 Notas Importantes

1. **Base de Datos**: El proyecto usa SQLite por defecto (ideal para desarrollo)
2. **Zona Horaria**: Configurada para `America/Bogota`
3. **Idioma**: Configurado en español de Colombia (`es-co`)
4. **Archivos Estáticos**: Se sirven automáticamente desde CDN (Bootstrap)
5. **DEBUG Mode**: Está activado (solo para desarrollo, desactivar en producción)

## 🐛 Solución de Problemas

### El servidor no inicia
```bash
# Verificar que el entorno virtual esté activado
.\venv\Scripts\Activate.ps1

# Verificar instalación de Django
python -m django --version
```

### No puedo iniciar sesión
- Verificar que los usuarios estén creados con `python init_data.py`
- Las credenciales son sensibles a mayúsculas

### Los espacios no aparecen
- Ejecutar `python init_data.py` para cargar datos de prueba
- Verificar en el admin que existan espacios: http://127.0.0.1:8000/admin/

## 🚀 Próximas Mejoras (Futuras)

- [ ] Sistema de notificaciones por email
- [ ] Reportes y estadísticas avanzadas
- [ ] API REST para integración con apps móviles
- [ ] Sistema de pagos para reservas
- [ ] Gestión completa de incidencias
- [ ] Dashboard con gráficos en tiempo real
- [ ] Exportación de reportes en PDF/Excel

## 👨‍💻 Desarrollo

- **Framework**: Django 5.2.8
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción recomendada)
- **Frontend**: Bootstrap 5.3 + Bootstrap Icons
- **Python**: 3.8+

## 📄 Licencia

Este proyecto fue desarrollado como parte de un sistema académico universitario.

---

**MiParqueo** - Sistema de Gestión de Parqueaderos Universitarios © 2025

