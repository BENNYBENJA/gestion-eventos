from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def requiere_admin(view_func):
    """Decorador: requiere que el usuario tenga rol ADMIN."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/cuentas/login/?next={request.path}')
        if not request.user.es_admin:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

def requiere_login(view_func):
    """Decorador: requiere autenticación."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/cuentas/login/?next={request.path}')
        return view_func(request, *args, **kwargs)
    return wrapper
