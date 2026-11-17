from django.db import models
from django.core.validators import MinValueValidator

class Evento(models.Model):
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    fecha = models.DateField(verbose_name='Fecha')
    hora = models.TimeField(verbose_name='Hora')
    duracion_min = models.PositiveIntegerField(verbose_name='Duración (minutos)', validators=[MinValueValidator(1)])
    capacidad_maxima = models.PositiveIntegerField(verbose_name='Capacidad máxima', validators=[MinValueValidator(1)])
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['fecha', 'hora']
        constraints = [
            models.CheckConstraint(check=models.Q(capacidad_maxima__gt=0), name='capacidad_gt_0'),
            models.CheckConstraint(check=models.Q(duracion_min__gt=0), name='duracion_gt_0'),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.fecha})"
    
    @property
    def plazas_disponibles(self):
        """Calcula plazas disponibles: capacidad - suma de plazas VIGENTES."""
        from apps.reservas.models import Reserva
        plazas_reservadas = self.reservas.filter(
            estado=Reserva.ESTADO_VIGENTE
        ).aggregate(total=models.Sum('plazas'))['total'] or 0
        return max(0, self.capacidad_maxima - plazas_reservadas)
    
    @property
    def plazas_reservadas_vigentes(self):
        from apps.reservas.models import Reserva
        return self.reservas.filter(
            estado=Reserva.ESTADO_VIGENTE
        ).aggregate(total=models.Sum('plazas'))['total'] or 0
    
    @property
    def porcentaje_ocupacion(self):
        if self.capacidad_maxima == 0:
            return 0
        plazas_reservadas = self.plazas_reservadas_vigentes
        return min(100, round((plazas_reservadas / self.capacidad_maxima) * 100))
    
    @property
    def tiene_reservas(self):
        return self.reservas.exists()
