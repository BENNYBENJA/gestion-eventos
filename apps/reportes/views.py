from django.shortcuts import render
from django.contrib import messages
from django.core.exceptions import ValidationError
from apps.cuentas.decorators import requiere_admin
from .services import ServicioReportes

@requiere_admin
def reportes_home(request):
    """Vista principal de reportes con filtros."""
    tipo = request.GET.get('tipo', 'ocupacion')
    evento_id = request.GET.get('evento') or None
    fecha_inicio_str = request.GET.get('fecha_inicio') or None
    fecha_fin_str = request.GET.get('fecha_fin') or None
    
    # Parsear fechas
    from datetime import date
    fecha_inicio = None
    fecha_fin = None
    
    try:
        if fecha_inicio_str:
            from datetime import datetime
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        if fecha_fin_str:
            from datetime import datetime
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, 'Formato de fecha inválido.')
    
    datos_reporte = None
    if tipo in ['ocupacion', 'asistencia']:
        try:
            datos_reporte = ServicioReportes.generar_reporte(
                tipo, evento_id, fecha_inicio, fecha_fin
            )
        except ValidationError as e:
            messages.error(request, str(e))
    
    eventos = ServicioReportes.listar_eventos()
    
    return render(request, 'reportes/reportes.html', {
        'tipo': tipo,
        'datos_reporte': datos_reporte,
        'eventos': eventos,
        'filtro_evento': evento_id,
        'fecha_inicio': fecha_inicio_str or '',
        'fecha_fin': fecha_fin_str or '',
    })
