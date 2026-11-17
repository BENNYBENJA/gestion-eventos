from django.contrib import admin
from .models import Reserva

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['pk', 'usuario', 'evento', 'plazas', 'estado', 'fecha_hora']
    list_filter = ['estado', 'evento']
    search_fields = ['usuario__email', 'evento__nombre']
