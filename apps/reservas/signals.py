"""
Patrón Observer: tras confirmar una reserva, se emite la señal 'reserva_confirmada'
y un observador registra la operación en el log de auditoría.
"""
import logging
from django.dispatch import Signal, receiver

logger = logging.getLogger(__name__)

# Señal personalizada: Observer
reserva_confirmada = Signal()
reserva_cancelada = Signal()

@receiver(reserva_confirmada)
def observador_log_reserva(sender, reserva, **kwargs):
    """Observador: registra en log cuando se confirma una reserva."""
    logger.info(
        f"[OBSERVER] Reserva confirmada | "
        f"ID: {reserva.pk} | "
        f"Usuario: {reserva.usuario.email} | "
        f"Evento: {reserva.evento.nombre} | "
        f"Plazas: {reserva.plazas}"
    )
    print(
        f"[OBSERVER] Nueva reserva confirmada: "
        f"#{reserva.pk} - {reserva.usuario.email} -> {reserva.evento.nombre}"
    )

@receiver(reserva_cancelada)
def observador_log_cancelacion(sender, reserva, cancelada_por, **kwargs):
    """Observador: registra en log cuando se cancela una reserva."""
    logger.info(
        f"[OBSERVER] Reserva cancelada | "
        f"ID: {reserva.pk} | "
        f"Cancelada por: {cancelada_por.email}"
    )
