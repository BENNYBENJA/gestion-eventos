from django.apps import AppConfig

class ReservasConfig(AppConfig):
    name = 'apps.reservas'
    verbose_name = 'Reservas'
    
    def ready(self):
        import apps.reservas.signals  # Registra los observadores al arrancar
