from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Reserva(models.Model):
    ESTADO_VIGENTE = 'VIGENTE'
    ESTADO_CANCELADA = 'CANCELADA'
    ESTADOS = [
        (ESTADO_VIGENTE, 'Vigente'),
        (ESTADO_CANCELADA, 'Cancelada'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reservas', verbose_name='Usuario'
    )
    evento = models.ForeignKey(
        'eventos.Evento', on_delete=models.CASCADE,
        related_name='reservas', verbose_name='Evento'
    )
    plazas = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name='Plazas'
    )
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de reserva')
    estado = models.CharField(
        max_length=10, choices=ESTADOS, default=ESTADO_VIGENTE, verbose_name='Estado'
    )
    asistentes = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='Asistentes efectivos'
    )
    cancelada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='cancelaciones', verbose_name='Cancelada por'
    )
    fecha_cancelacion = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de cancelación')
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha_hora']
        constraints = [
            models.CheckConstraint(
                check=models.Q(plazas__gt=0),
                name='plazas_gt_0'
            ),
            models.CheckConstraint(
                check=models.Q(asistentes__isnull=True) | (
                    models.Q(asistentes__gte=0) & models.Q(asistentes__lte=models.F('plazas'))
                ),
                name='asistentes_entre_0_y_plazas'
            ),
        ]
    
    def __str__(self):
        return f"Reserva #{self.pk} - {self.usuario.email} en {self.evento.nombre}"
    
    @property
    def asistentes_validos(self):
        """Asistentes entre 0 y plazas confirmadas."""
        if self.asistentes is None:
            return None
        return max(0, min(self.asistentes, self.plazas))
    
    @property
    def es_vigente(self):
        return self.estado == self.ESTADO_VIGENTE
