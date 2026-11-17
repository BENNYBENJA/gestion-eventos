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
        
        usuario = ServicioAutenticacion.autenticar(request, email, password)
        if usuario:
            messages.success(request, f'Bienvenido/a, {usuario.get_full_name() or usuario.email}')
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
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
