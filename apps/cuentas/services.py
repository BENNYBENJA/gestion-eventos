from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class ServicioAutenticacion:
    @staticmethod
    def autenticar(request, email, password):
        """Autentica por email y contraseña. No revela cuál dato falló."""
        usuario = authenticate(request, username=email, password=password)
        if usuario is not None and usuario.is_active:
            login(request, usuario)
            return usuario
        return None
    
    @staticmethod
    def cerrar_sesion(request):
        logout(request)
