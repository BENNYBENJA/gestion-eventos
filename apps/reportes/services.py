from datetime import date
from django.core.exceptions import ValidationError
from apps.eventos.models import Evento
from .factory import ReporteFactory

class ServicioReportes:
    
    @staticmethod
    def generar_reporte(tipo, evento_id=None, fecha_inicio=None, fecha_fin=None):
        """
        Genera un reporte usando ReporteFactory.
        Regla 7: valida que el rango no esté invertido.
        """
        # Validar rango de fechas
        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise ValidationError(
                    'El rango de fechas está invertido: la fecha de inicio debe ser anterior a la fecha de fin.'
                )
        
        filtros = {
            'evento_id': evento_id or None,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
        }
        
        reporte = ReporteFactory.crear(tipo)
        return reporte.generar(filtros)
    
    @staticmethod
    def listar_eventos():
        return Evento.objects.all().order_by('nombre')
