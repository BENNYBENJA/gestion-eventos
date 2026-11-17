"""
Patrón Factory: ReporteFactory crea ReporteOcupacion o ReporteAsistencia.
Ambos heredan de ReporteBase e implementan la interfaz Reporte.
"""
from abc import ABC, abstractmethod
from django.db.models import Sum, Count, Q
from apps.eventos.models import Evento
from apps.reservas.models import Reserva


class Reporte(ABC):
    """Interfaz Reporte."""
    @abstractmethod
    def generar(self, filtros: dict) -> dict:
        pass


class ReporteBase(Reporte):
    """Clase base con utilidades comunes."""
    
    def _filtrar_eventos(self, filtros):
        qs = Evento.objects.all()
        if filtros.get('evento_id'):
            qs = qs.filter(pk=filtros['evento_id'])
        if filtros.get('fecha_inicio'):
            qs = qs.filter(fecha__gte=filtros['fecha_inicio'])
        if filtros.get('fecha_fin'):
            qs = qs.filter(fecha__lte=filtros['fecha_fin'])
        return qs


class ReporteOcupacion(ReporteBase):
    """
    Reporte de ocupación por evento.
    Ocupación = plazas_vigentes / capacidad × 100
    """
    
    def generar(self, filtros: dict) -> dict:
        eventos = self._filtrar_eventos(filtros)
        filas = []
        
        for evento in eventos.order_by('fecha'):
            plazas_vigentes = evento.reservas.filter(
                estado=Reserva.ESTADO_VIGENTE
            ).aggregate(total=Sum('plazas'))['total'] or 0
            
            # Evitar división por cero (Regla 7)
            if evento.capacidad_maxima > 0:
                porcentaje = round((plazas_vigentes / evento.capacidad_maxima) * 100, 1)
            else:
                porcentaje = 0
            
            filas.append({
                'evento': evento,
                'plazas_vigentes': plazas_vigentes,
                'capacidad': evento.capacidad_maxima,
                'disponibles': evento.capacidad_maxima - plazas_vigentes,
                'porcentaje': porcentaje,
            })
        
        return {
            'tipo': 'ocupacion',
            'titulo': 'Reporte de Ocupación',
            'filas': filas,
            'sin_datos': len(filas) == 0,
        }


class ReporteAsistencia(ReporteBase):
    """
    Reporte de asistencia por evento.
    Asistencia = suma de asistentes registrados, mostrando pendientes.
    """
    
    def generar(self, filtros: dict) -> dict:
        eventos = self._filtrar_eventos(filtros)
        filas = []
        
        for evento in eventos.order_by('fecha'):
            reservas_vigentes = evento.reservas.filter(estado=Reserva.ESTADO_VIGENTE)
            total_plazas = reservas_vigentes.aggregate(total=Sum('plazas'))['total'] or 0
            total_asistentes = reservas_vigentes.filter(
                asistentes__isnull=False
            ).aggregate(total=Sum('asistentes'))['total'] or 0
            pendientes_registro = reservas_vigentes.filter(asistentes__isnull=True).count()
            
            filas.append({
                'evento': evento,
                'total_plazas': total_plazas,
                'total_asistentes': total_asistentes,
                'pendientes_registro': pendientes_registro,
            })
        
        return {
            'tipo': 'asistencia',
            'titulo': 'Reporte de Asistencia',
            'filas': filas,
            'sin_datos': len(filas) == 0,
        }


class ReporteFactory:
    """
    Factory: devuelve el reporte correcto según el tipo solicitado.
    """
    _tipos = {
        'ocupacion': ReporteOcupacion,
        'asistencia': ReporteAsistencia,
    }
    
    @classmethod
    def crear(cls, tipo: str) -> Reporte:
        clase = cls._tipos.get(tipo)
        if clase is None:
            raise ValueError(f"Tipo de reporte desconocido: '{tipo}'. Opciones: {list(cls._tipos.keys())}")
        return clase()
    
    @classmethod
    def tipos_disponibles(cls):
        return list(cls._tipos.keys())
