"""
URL configuration for gestion_eventos project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuentas/', include('apps.cuentas.urls')),
    path('eventos/', include('apps.eventos.urls')),
    path('reservas/', include('apps.reservas.urls')),
    path('reportes/', include('apps.reportes.urls')),
    path('', include('apps.eventos.urls_public')),  # Catálogo público en la raíz /
]
