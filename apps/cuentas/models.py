from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROL_ADMIN = 'ADMIN'
    ROL_USUARIO = 'USUARIO'
    ROLES = [(ROL_ADMIN, 'Administrador'), (ROL_USUARIO, 'Usuario')]
    
    rol = models.CharField(max_length=10, choices=ROLES, default=ROL_USUARIO)
    email = models.EmailField(unique=True)
    intentos_fallidos = models.PositiveIntegerField(default=0, verbose_name="Intentos fallidos de login")
    bloqueado = models.BooleanField(default=False, verbose_name="Cuenta bloqueada por seguridad")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    @property
    def es_admin(self):
        return self.rol == self.ROL_ADMIN

    def registrar_intento_fallido(self, max_intentos=5):
        """OWASP: Bloquea la cuenta tras superar el umbral de intentos fallidos."""
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= max_intentos:
            self.bloqueado = True
            self.is_active = False
        self.save(update_fields=['intentos_fallidos', 'bloqueado', 'is_active'])
        return self.bloqueado

    def reiniciar_intentos(self):
        """Reinicia contador tras login exitoso."""
        if self.intentos_fallidos > 0:
            self.intentos_fallidos = 0
            self.save(update_fields=['intentos_fallidos'])
    
    def __str__(self):
        return f"{self.get_full_name() or self.email} ({self.get_rol_display()})"
