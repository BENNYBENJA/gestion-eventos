from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.core.exceptions import ValidationError
from apps.cuentas.decorators import requiere_admin
from .models import Evento
from .services import ServicioEventos

# ─── Catálogo público ───────────────────────────────────────────────
def catalogo(request):
    busqueda = request.GET.get('q', '').strip()
    fecha = request.GET.get('fecha', '') or None
    eventos = ServicioEventos.listar_eventos_publicos(busqueda, fecha)
    return render(request, 'eventos/catalogo.html', {
        'eventos': eventos,
        'busqueda': busqueda,
        'fecha': fecha,
    })

def detalle_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk, activo=True)
    return render(request, 'eventos/detalle.html', {'evento': evento})

# ─── Admin CRUD ───────────────────────────────────────────────────────
@requiere_admin
def admin_eventos(request):
    eventos = ServicioEventos.listar_todos_eventos()
    return render(request, 'eventos/admin_lista.html', {'eventos': eventos})

@requiere_admin
def admin_crear_evento(request):
    if request.method == 'POST':
        try:
            datos = {
                'nombre': request.POST['nombre'],
                'fecha': request.POST['fecha'],
                'hora': request.POST['hora'],
                'duracion_min': int(request.POST['duracion_min']),
                'capacidad_maxima': int(request.POST['capacidad_maxima']),
                'descripcion': request.POST.get('descripcion', ''),
                'activo': 'activo' in request.POST,
            }
            ServicioEventos.crear_evento(datos)
            messages.success(request, 'Evento creado correctamente.')
            return redirect('eventos:admin_eventos')
        except (ValidationError, ValueError, KeyError) as e:
            messages.error(request, f'Error al crear el evento: {e}')
    return render(request, 'eventos/admin_form.html', {'accion': 'Crear', 'evento': None})

@requiere_admin
def admin_editar_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == 'POST':
        try:
            datos = {
                'nombre': request.POST['nombre'],
                'fecha': request.POST['fecha'],
                'hora': request.POST['hora'],
                'duracion_min': int(request.POST['duracion_min']),
                'capacidad_maxima': int(request.POST['capacidad_maxima']),
                'descripcion': request.POST.get('descripcion', ''),
                'activo': 'activo' in request.POST,
            }
            ServicioEventos.actualizar_evento(pk, datos)
            messages.success(request, 'Evento actualizado correctamente.')
            return redirect('eventos:admin_eventos')
        except (ValidationError, ValueError) as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'eventos/admin_form.html', {'accion': 'Editar', 'evento': evento})

@requiere_admin
def admin_eliminar_evento(request, pk):
    if request.method == 'POST':
        resultado = ServicioEventos.eliminar_o_desactivar(pk)
        if resultado == 'eliminado':
            messages.success(request, 'Evento eliminado permanentemente.')
        else:
            messages.warning(request, 'El evento tiene reservas: fue desactivado en lugar de eliminado.')
        return redirect('eventos:admin_eventos')
    evento = get_object_or_404(Evento, pk=pk)
    return render(request, 'eventos/admin_confirmar_eliminar.html', {'evento': evento})

@requiere_admin
def admin_toggle_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    evento.activo = not evento.activo
    evento.save()
    estado = "activado" if evento.activo else "desactivado"
    messages.success(request, f'Evento {estado} correctamente.')
    return redirect('eventos:admin_eventos')
