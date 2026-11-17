from django.urls import path
from . import views

app_name = 'eventos'

urlpatterns = [
    path('', views.catalogo, name='catalogo'),  # /eventos/
    path('<int:pk>/', views.detalle_evento, name='detalle'),
    path('admin/', views.admin_eventos, name='admin_eventos'),
    path('admin/crear/', views.admin_crear_evento, name='admin_crear'),
    path('admin/<int:pk>/editar/', views.admin_editar_evento, name='admin_editar'),
    path('admin/<int:pk>/eliminar/', views.admin_eliminar_evento, name='admin_eliminar'),
    path('admin/<int:pk>/toggle/', views.admin_toggle_evento, name='admin_toggle'),
]
