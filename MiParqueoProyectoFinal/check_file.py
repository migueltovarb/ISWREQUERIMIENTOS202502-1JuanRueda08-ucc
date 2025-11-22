with open('templates/cliente/historial.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if 'Horario:' in line or 'hora_fin' in line:
            print(f'{i}: {line.rstrip()}')
