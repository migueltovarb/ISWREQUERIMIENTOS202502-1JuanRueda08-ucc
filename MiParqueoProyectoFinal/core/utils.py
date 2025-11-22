"""
Utilidades para la aplicación core.
Incluye funciones auxiliares como generación de códigos QR.
"""
import os
import uuid
import qrcode
from django.conf import settings


def generar_qr_reserva(reserva):
    """
    Genera un código QR único para una reserva.
    
    Args:
        reserva: Instancia del modelo Reserva
        
    Returns:
        str: Ruta relativa del archivo QR generado (ej: 'qr/abc123.png')
    """
    # Generar UUID único
    codigo_unico = str(uuid.uuid4())
    
    # Crear directorio qr si no existe
    qr_dir = os.path.join(settings.MEDIA_ROOT, 'qr')
    os.makedirs(qr_dir, exist_ok=True)
    
    # Generar código QR
    # El contenido del QR será un string con información de la reserva
    qr_data = f"RESERVA-{reserva.id}-{codigo_unico}"
    
    # Crear imagen QR
    qr = qrcode.QRCode(
        version=1,  # Tamaño del QR (1 es el más pequeño)
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Crear imagen
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar imagen con nombre basado en UUID
    filename = f"{codigo_unico}.png"
    filepath = os.path.join(qr_dir, filename)
    img.save(filepath)
    
    # Retornar ruta relativa para guardar en la base de datos
    return f"qr/{filename}"
