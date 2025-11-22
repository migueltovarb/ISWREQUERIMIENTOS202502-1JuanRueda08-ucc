import re

# Leer el archivo
with open('templates/cliente/historial.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar el patrón problemático
# Buscar el patrón con saltos de línea y espacios
pattern = r'\{\{\s*reserva\.hora_inicio\|time:"H:i"\s*\}\}\s*-\s*\{\{\s*reserva\.hora_fin\|time:"H:i"\s*\}\}'
replacement = '{{ reserva.hora_inicio|time:"H:i" }} - {{ reserva.hora_fin|time:"H:i" }}'

content_fixed = re.sub(pattern, replacement, content)

# Guardar el archivo
with open('templates/cliente/historial.html', 'w', encoding='utf-8') as f:
    f.write(content_fixed)

print("Archivo corregido exitosamente!")
