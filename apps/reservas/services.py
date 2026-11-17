from django.db import transaction
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Reserva
from .signals import reserva_confirmada, reserva_cancelada
from .adapter import servicio_correo

class ServicioReservas:
    
    @staticmethod
    @transaction.atomic
    def crear_reserva(usuario, evento_id, plazas):
        """
        RF04: Reservar plazas.
        Regla 1: select_for_update() antes de calcular disponibilidad.
        """
        from apps.eventos.models import Evento
        
        # Bloquear el evento para concurrencia
        evento = Evento.objects.select_for_update().get(pk=evento_id)
        
        # Validar evento activo
        if not evento.activo:
            raise ValidationError('Este evento no acepta reservas (inactivo).')
        
        # Validar plazas solicitadas
        if plazas <= 0:
            raise ValidationError('La cantidad de plazas debe ser mayor a cero.')
        
        # Calcular disponibilidad dentro de la transacción
        plazas_reservadas = evento.reservas.filter(
            estado=Reserva.ESTADO_VIGENTE
        ).aggregate(total=Sum('plazas'))['total'] or 0
        
        disponibles = evento.capacidad_maxima - plazas_reservadas
        
        if plazas > disponibles:
            raise ValidationError(
                f'No hay suficientes plazas. Disponibles: {disponibles}, solicitadas: {plazas}.'
            )
        
        # Crear la reserva
        reserva = Reserva.objects.create(
            usuario=usuario,
            evento=evento,
            plazas=plazas,
            estado=Reserva.ESTADO_VIGENTE,
        )
        
        # Emitir señal Observer (después de confirmar la transacción)
        transaction.on_commit(lambda: reserva_confirmada.send(
            sender=ServicioReservas, reserva=reserva
        ))
        
        # Enviar correo (Adapter - no revierte si falla)
        transaction.on_commit(lambda: servicio_correo.enviar_confirmacion_reserva(reserva))
        
        return reserva
    
    @staticmethod
    @transaction.atomic
    def cancelar_reserva(reserva_id, cancelada_por):
        """
        Regla 2: Cancelar libera plazas una sola vez.
        Regla 5: No cancelar si tiene asistencia registrada.
        """
        reserva = Reserva.objects.select_for_update().get(pk=reserva_id)
        
        # Regla 2: ya cancelada, no hace nada
        if reserva.estado == Reserva.ESTADO_CANCELADA:
            raise ValidationError('Esta reserva ya está cancelada.')
        
        # Regla 5: no cancelar con asistencia registrada
        if reserva.asistentes is not None:
            raise ValidationError(
                'No se puede cancelar una reserva que ya tiene asistencia registrada.'
            )
        
        reserva.estado = Reserva.ESTADO_CANCELADA
        reserva.cancelada_por = cancelada_por
        reserva.fecha_cancelacion = timezone.now()
        reserva.save()
        
        # Señal Observer
        transaction.on_commit(lambda: reserva_cancelada.send(
            sender=ServicioReservas, reserva=reserva, cancelada_por=cancelada_por
        ))
        
        # Correo (Adapter)
        transaction.on_commit(lambda: servicio_correo.enviar_cancelacion_reserva(reserva))
        
        return reserva
    
    @staticmethod
    @transaction.atomic
    def registrar_asistentes(reserva_id, cantidad):
        """
        Regla 6: Asistentes entre 0 y plazas. Corregir reemplaza (no suma).
        No registrar en reservas canceladas.
        """
        reserva = Reserva.objects.select_for_update().get(pk=reserva_id)
        
        if reserva.estado == Reserva.ESTADO_CANCELADA:
            raise ValidationError('No se puede registrar asistencia en una reserva cancelada.')
        
        if cantidad < 0 or cantidad > reserva.plazas:
            raise ValidationError(
                f'Los asistentes deben estar entre 0 y {reserva.plazas}.'
            )
        
        reserva.asistentes = cantidad  # Reemplaza, no suma
        reserva.save()
        return reserva
    
    @staticmethod
    def listar_mis_reservas(usuario):
        """RF05: Solo las reservas del usuario autenticado."""
        return Reserva.objects.filter(usuario=usuario).select_related('evento')
    
    @staticmethod
    def listar_todas_reservas(evento_id=None, usuario_email=None, fecha=None):
        """Admin: lista con filtros."""
        qs = Reserva.objects.select_related('usuario', 'evento', 'cancelada_por')
        if evento_id:
            qs = qs.filter(evento_id=evento_id)
        if usuario_email:
            qs = qs.filter(usuario__email__icontains=usuario_email)
        if fecha:
            qs = qs.filter(evento__fecha=fecha)
        return qs.order_by('-fecha_hora')
    
    @staticmethod
    def obtener_reserva(reserva_id):
        return Reserva.objects.select_related('usuario', 'evento').get(pk=reserva_id)
