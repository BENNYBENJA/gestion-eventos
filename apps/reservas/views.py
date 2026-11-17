from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError, PermissionDenied
from apps.cuentas.decorators import requiere_login, requiere_admin
from apps.eventos.models import Evento
from .models import Reserva
from .services import ServicioReservas

@requiere_login
def crear_reserva(request, evento_id):
    """RF04: Crear reserva."""
    evento = get_object_or_404(Evento, pk=evento_id, activo=True)
    
    if request.method == 'POST':
        try:
            plazas = int(request.POST.get('plazas', 0))
            reserva = ServicioReservas.crear_reserva(request.user, evento_id, plazas)
            messages.success(request, f'✅ Reserva confirmada: {plazas} plaza(s) para "{evento.nombre}".')
            return redirect('reservas:mis_inscripciones')
        except (ValidationError, ValueError) as e:
            messages.error(request, f'❌ {e}')
            return redirect('eventos:detalle', pk=evento_id)
    
    return render(request, 'reservas/confirmar_reserva.html', {
        'evento': evento,
        'max_plazas': evento.plazas_disponibles,
    })

@requiere_login
def mis_inscripciones(request):
    """RF05: Ver únicamente sus propias reservas."""
    reservas = ServicioReservas.listar_mis_reservas(request.user)
    return render(request, 'reservas/mis_inscripciones.html', {'reservas': reservas})

@requiere_login
def detalle_reserva(request, pk):
    """RF05: Un usuario no puede ver reservas ajenas (responder 403)."""
    reserva = get_object_or_404(Reserva, pk=pk)
    if not request.user.es_admin and reserva.usuario != request.user:
        raise PermissionDenied("No tienes permiso para ver esta reserva.")
    return render(request, 'reservas/detalle_reserva.html', {'reserva': reserva})

# ─── Admin ────────────────────────────────────────────────────────────
@requiere_admin
def admin_reservas(request):
    evento_id = request.GET.get('evento')
    usuario_email = request.GET.get('usuario', '').strip()
    fecha = request.GET.get('fecha', '') or None
    
    reservas = ServicioReservas.listar_todas_reservas(evento_id, usuario_email, fecha)
    eventos = Evento.objects.all().order_by('nombre')
    
    return render(request, 'reservas/admin_lista.html', {
        'reservas': reservas,
        'eventos': eventos,
        'filtro_evento': evento_id,
        'filtro_usuario': usuario_email,
        'filtro_fecha': fecha,
    })

@requiere_admin
def admin_cancelar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        try:
            ServicioReservas.cancelar_reserva(pk, request.user)
            messages.success(request, f'Reserva #{pk} cancelada correctamente. Plazas liberadas.')
        except ValidationError as e:
            messages.error(request, f'Error al cancelar reserva: {e}')
        return redirect('reservas:admin_reservas')
    return render(request, 'reservas/admin_confirmar_cancelar.html', {'reserva': reserva})

@requiere_admin
def admin_registrar_asistentes(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        try:
            cantidad = int(request.POST.get('asistentes', 0))
            ServicioReservas.registrar_asistentes(pk, cantidad)
            messages.success(request, f'Asistencia registrada exitosamente: {cantidad} persona(s).')
        except (ValidationError, ValueError) as e:
            messages.error(request, f'Error al registrar asistencia: {e}')
        return redirect('reservas:admin_reservas')
    return render(request, 'reservas/admin_asistentes.html', {'reserva': reserva})
