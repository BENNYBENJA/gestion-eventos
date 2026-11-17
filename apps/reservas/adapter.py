import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ServicioCorreoInterface(ABC):
    """Interfaz para el servicio de correo (Patrón Adapter)."""
    
    @abstractmethod
    def enviar_confirmacion_reserva(self, reserva):
        pass
    
    @abstractmethod
    def enviar_cancelacion_reserva(self, reserva):
        pass


class AdaptadorCorreoConsola(ServicioCorreoInterface):
    """
    Adapter: implementa la interfaz ServicioCorreo usando la consola.
    Un fallo nunca revierte la reserva (swallows exceptions).
    """
    
    def enviar_confirmacion_reserva(self, reserva):
        try:
            print(f"[CORREO SIMULADO] Reserva confirmada:")
            print(f"  → Para: {reserva.usuario.email}")
            print(f"  → Evento: {reserva.evento.nombre} el {reserva.evento.fecha}")
            print(f"  → Plazas: {reserva.plazas}")
            print(f"  → Estado: {reserva.estado}")
            logger.info(f"Correo de confirmación enviado (simulado) para reserva #{reserva.pk}")
        except Exception as e:
            logger.warning(f"Error al enviar correo (ignorado): {e}")
    
    def enviar_cancelacion_reserva(self, reserva):
        try:
            print(f"[CORREO SIMULADO] Reserva cancelada:")
            print(f"  → Para: {reserva.usuario.email}")
            print(f"  → Evento: {reserva.evento.nombre}")
            logger.info(f"Correo de cancelación enviado (simulado) para reserva #{reserva.pk}")
        except Exception as e:
            logger.warning(f"Error al enviar correo (ignorado): {e}")


# Instancia global del adaptador activo
servicio_correo = AdaptadorCorreoConsola()
