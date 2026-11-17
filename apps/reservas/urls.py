from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    path('mis-inscripciones/', views.mis_inscripciones, name='mis_inscripciones'),
    path('<int:pk>/', views.detalle_reserva, name='detalle_reserva'),
    path('crear/<int:evento_id>/', views.crear_reserva, name='crear'),
    path('admin/', views.admin_reservas, name='admin_reservas'),
    path('admin/<int:pk>/cancelar/', views.admin_cancelar_reserva, name='admin_cancelar'),
    path('admin/<int:pk>/asistentes/', views.admin_registrar_asistentes, name='admin_asistentes'),
]
