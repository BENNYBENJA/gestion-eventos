from django.conf import settings as django_settings

class ConfiguracionSistema:
    """
    Patrón Singleton: una única instancia de configuración por proceso.
    Se apoya en django.conf.settings como fuente de verdad.
    """
    _instancia = None
    
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia
    
    def _inicializar(self):
        self.nombre_sistema = "Sistema de Gestión de Eventos y Reservas"
        self.nombre_centro = "Centro Comunitario"
        self.debug = django_settings.DEBUG
        self.version = "1.0.0"
        self.zona_horaria = django_settings.TIME_ZONE
    
    @classmethod
    def obtener(cls):
        """Punto de acceso global a la instancia única."""
        return cls()
    
    def __repr__(self):
        return f"<ConfiguracionSistema singleton en {id(self)}>"
