from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Evento

class ServicioEventos:
    
    @staticmethod
    def listar_eventos_publicos(busqueda='', fecha=None):
        """RF01, RF02: Catálogo público con búsqueda y filtro."""
        qs = Evento.objects.filter(activo=True)
        if busqueda:
            qs = qs.filter(nombre__icontains=busqueda)
        if fecha:
            qs = qs.filter(fecha=fecha)
        return qs.order_by('fecha', 'hora')
    
    @staticmethod
    def listar_todos_eventos():
        """Admin: lista todos los eventos."""
        return Evento.objects.all().order_by('-id')
    
    @staticmethod
    @transaction.atomic
    def crear_evento(datos):
        """Crea un nuevo evento validando campos."""
        evento = Evento(**datos)
        evento.full_clean()
        evento.save()
        return evento
    
    @staticmethod
    @transaction.atomic
    def actualizar_evento(evento_id, datos):
        """
        Actualiza evento. Regla 3: no bajar capacidad por debajo de plazas vigentes.
        """
        from apps.reservas.models import Reserva
        from django.db.models import Sum
        evento = Evento.objects.select_for_update().get(pk=evento_id)
        nueva_capacidad = datos.get('capacidad_maxima', evento.capacidad_maxima)
        
        if nueva_capacidad != evento.capacidad_maxima:
            plazas_vigentes = evento.reservas.filter(
                estado=Reserva.ESTADO_VIGENTE
            ).aggregate(total=Sum('plazas'))['total'] or 0
            if nueva_capacidad < plazas_vigentes:
                raise ValidationError(
                    f'No se puede reducir la capacidad a {nueva_capacidad}. '
                    f'Ya hay {plazas_vigentes} plazas reservadas.'
                )
        
        for campo, valor in datos.items():
            setattr(evento, campo, valor)
        evento.full_clean()
        evento.save()
        return evento
    
    @staticmethod
    @transaction.atomic
    def eliminar_o_desactivar(evento_id):
        """
        Regla 4: Si tiene reservas, desactiva; si no, elimina físicamente.
        """
        from apps.reservas.models import Reserva
        evento = Evento.objects.select_for_update().get(pk=evento_id)
        tiene_reservas = evento.reservas.exists()
        if tiene_reservas:
            evento.activo = False
            evento.save()
            return 'desactivado'
        else:
            evento.delete()
            return 'eliminado'
    
    @staticmethod
    def obtener_evento(evento_id):
        return Evento.objects.get(pk=evento_id)
