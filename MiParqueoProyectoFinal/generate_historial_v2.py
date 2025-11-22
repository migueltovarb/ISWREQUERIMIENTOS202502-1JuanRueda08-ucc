
content = """{% extends 'base.html' %}

{% block title %}Historial de Reservas - MiParqueo{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-12">
        <h1 class="display-6">
            <i class="bi bi-clock-history text-primary"></i> 
            Historial de Reservas
        </h1>
        <p class="text-muted">Todas sus reservas registradas en el sistema</p>
    </div>
</div>

<div class="row mb-3">
    <div class="col-12">
        <a href="{% url 'cliente_disponibilidad' %}" class="btn btn-primary">
            <i class="bi bi-calendar-plus"></i> Nueva Reserva
        </a>
        <a href="{% url 'cliente_reservas_activas' %}" class="btn btn-outline-primary">
            <i class="bi bi-calendar-check"></i> Ver Reservas Activas
        </a>
    </div>
</div>

<div class="row">
    <div class="col-12">
        {% if reservas %}
        <div class="table-responsive">
            <table class="table table-hover table-striped">
                <thead class="table-dark">
                    <tr>
                        <th><i class="bi bi-hash"></i> ID</th>
                        <th><i class="bi bi-car-front"></i> Espacio</th>
                        <th><i class="bi bi-calendar"></i> Fecha</th>
                        <th><i class="bi bi-clock"></i> Horario Reservado</th>
                        <th><i class="bi bi-clock-fill"></i> Hora Real</th>
                        <th><i class="bi bi-truck"></i> Vehículo</th>
                        <th><i class="bi bi-tag"></i> Placa</th>
                        <th><i class="bi bi-info-circle"></i> Estado</th>
                        <th><i class="bi bi-qr-code"></i> Código QR</th>
                        <th><i class="bi bi-gear"></i> Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {% for reserva in reservas %}
                    <tr>
                        <td><strong>#{{ reserva.id }}</strong></td>
                        <td>
                            <span class="badge bg-secondary">
                                {{ reserva.espacio.numero }}
                            </span>
                        </td>
                        <td>{{ reserva.fecha|date:"d/m/Y" }}</td>
                        <td class="text-nowrap">
                            {{ reserva.hora_inicio|time:"H:i" }} - {{ reserva.hora_fin|time:"H:i" }}
                        </td>
                        <td class="text-nowrap">
                            {% if reserva.hora_entrada %}
                                <small>
                                    <i class="bi bi-box-arrow-in-right text-success"></i>
                                    {{ reserva.hora_entrada|time:"H:i" }}
                                </small>
                                <br>
                            {% endif %}
                            {% if reserva.hora_salida %}
                                <small>
                                    <i class="bi bi-box-arrow-right text-danger"></i>
                                    {{ reserva.hora_salida|time:"H:i" }}
                                </small>
                            {% endif %}
                            {% if not reserva.hora_entrada %}
                                <small class="text-muted">-</small>
                            {% endif %}
                        </td>
                        <td>{{ reserva.get_tipo_vehiculo_display }}</td>
                        <td><code>{{ reserva.placa }}</code></td>
                        <td>
                            {% if reserva.estado == 'RESERVADA' %}
                                <span class="badge bg-success">{{ reserva.get_estado_display }}</span>
                            {% elif reserva.estado == 'COMPLETADA' %}
                                <span class="badge bg-primary">{{ reserva.get_estado_display }}</span>
                            {% elif reserva.estado == 'CANCELADA' %}
                                <span class="badge bg-secondary">{{ reserva.get_estado_display }}</span>
                            {% elif reserva.estado == 'VENCIDA' %}
                                <span class="badge bg-warning text-dark">{{ reserva.get_estado_display }}</span>
                            {% else %}
                                <span class="badge bg-info">{{ reserva.get_estado_display }}</span>
                            {% endif %}
                        </td>
                        <td class="text-center">
                            {% if reserva.codigo_qr %}
                                <img src="/media/{{ reserva.codigo_qr }}" alt="QR Code" style="width: 80px; height: 80px; cursor: pointer;" class="img-thumbnail qr-clickable" data-bs-toggle="modal" data-bs-target="#qrModal{{ reserva.id }}" title="Click para ver en grande">
                            {% else %}
                                <small class="text-muted">QR no disponible</small>
                            {% endif %}
                        </td>
                        <td class="text-center">
                            {% if reserva.estado == 'RESERVADA' %}
                                <a href="{% url 'cliente_modificar_reserva' reserva.id %}" class="btn btn-sm btn-warning" title="Modificar Reserva">
                                    <i class="bi bi-pencil-square"></i>
                                </a>
                                <a href="{% url 'cliente_cancelar_reserva' reserva.id %}" class="btn btn-sm btn-danger" title="Cancelar Reserva" onclick="return confirm('¿Está seguro de cancelar esta reserva?')">
                                    <i class="bi bi-x-circle"></i>
                                </a>
                            {% else %}
                                <small class="text-muted">-</small>
                            {% endif %}
                        </td>
                    </tr>
                    
                    {% if reserva.codigo_qr %}
                    <div class="modal fade" id="qrModal{{ reserva.id }}" tabindex="-1" aria-labelledby="qrModalLabel{{ reserva.id }}" aria-hidden="true">
                        <div class="modal-dialog modal-dialog-centered">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="qrModalLabel{{ reserva.id }}">
                                        <i class="bi bi-qr-code"></i> Código QR - Reserva #{{ reserva.id }}
                                    </h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body text-center">
                                    <img src="/media/{{ reserva.codigo_qr }}" alt="QR Code" class="img-fluid" style="max-width: 100%;">
                                    <div class="mt-3">
                                        <p><strong>Espacio:</strong> {{ reserva.espacio.numero }}</p>
                                        <p><strong>Fecha:</strong> {{ reserva.fecha|date:"d/m/Y" }}</p>
                                        <p><strong>Horario:</strong> {{ reserva.hora_inicio|time:"H:i" }} - {{ reserva.hora_fin|time:"H:i" }}</p>
                                        <p><strong>Placa:</strong> <code>{{ reserva.placa }}</code></p>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endif %}
                    
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="alert alert-light mt-3">
            <strong>Total de reservas:</strong> {{ reservas.count }}
        </div>
        {% else %}
        <div class="alert alert-info">
            <i class="bi bi-info-circle-fill"></i>
            No tiene reservas registradas en el sistema.
            <a href="{% url 'cliente_disponibilidad' %}" class="alert-link">
                Crear su primera reserva
            </a>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}

{% block extra_css %}
<style>
    .qr-clickable:hover {
        transform: scale(1.05);
        transition: transform 0.2s;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
{% endblock %}
"""

with open('templates/cliente/historial.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Archivo generado correctamente")
