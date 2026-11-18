from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class ServicioAutenticacion:
    @staticmethod
    def autenticar(request, email, password):
        """
        Autentica por email y contraseña.
        Cumple con OWASP:
        - Bloqueo de cuenta tras 5 intentos fallidos.
        - Mensaje neutro de credenciales inválidas para evitar enumeración de usuarios.
        """
        email_limpio = email.strip().lower()
        usuario_existente = Usuario.objects.filter(email__iexact=email_limpio).first()

        # Si el usuario ya está bloqueado
        if usuario_existente and (usuario_existente.bloqueado or not usuario_existente.is_active):
            return None, "bloqueado"

        usuario = authenticate(request, username=email_limpio, password=password)
        if usuario is not None and usuario.is_active:
            usuario.reiniciar_intentos()
            login(request, usuario)
            return usuario, "ok"

        # Si la contraseña fue errónea para un usuario existente
        if usuario_existente:
            bloqueado = usuario_existente.registrar_intento_fallido(max_intentos=5)
            if bloqueado:
                return None, "recien_bloqueado"
            intentos_restantes = 5 - usuario_existente.intentos_fallidos
            return None, f"intentos_{intentos_restantes}"

        return None, "invalido"
    
    @staticmethod
    def cerrar_sesion(request):
        """
        OWASP: Termina completamente con la sesión y destruye cookies e identificadores.
        """
        logout(request)
        request.session.flush()
