from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from .services import ServicioAutenticacion

class LoginView(View):
    template_name = 'cuentas/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('eventos:catalogo')
        return render(request, self.template_name)
    
    def post(self, request):
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        if not email or not password:
            messages.error(request, 'Por favor ingresa tu correo y contraseña.')
            return render(request, self.template_name)
        
        usuario, estado = ServicioAutenticacion.autenticar(request, email, password)
        if usuario:
            messages.success(request, f'Bienvenido/a, {usuario.get_full_name() or usuario.email}')
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        elif estado == "bloqueado" or estado == "recien_bloqueado":
            messages.error(
                request,
                '🔒 Tu cuenta ha sido bloqueada temporalmente por seguridad tras alcanzar 5 intentos fallidos. '
                'Por favor contacta a la administración del centro comunitario.'
            )
            return render(request, self.template_name)
        elif estado.startswith("intentos_"):
            restantes = estado.split("_")[1]
            messages.error(
                request,
                f'Credenciales inválidas. Te quedan {restantes} intento(s) antes del bloqueo de seguridad.'
            )
            return render(request, self.template_name)
        else:
            messages.error(request, 'Credenciales inválidas. Verifica tus datos e intenta de nuevo.')
            return render(request, self.template_name)

class LogoutView(View):
    def get(self, request):
        ServicioAutenticacion.cerrar_sesion(request)
        messages.info(request, 'Has cerrado sesión correctamente.')
        return redirect('/')

    def post(self, request):
        ServicioAutenticacion.cerrar_sesion(request)
        messages.info(request, 'Has cerrado sesión correctamente.')
        return redirect('/')
