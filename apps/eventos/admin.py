from django.contrib import admin
from .models import Evento

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha', 'hora', 'capacidad_maxima', 'activo']
    list_filter = ['activo', 'fecha']
    search_fields = ['nombre']
