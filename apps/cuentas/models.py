from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROL_ADMIN = 'ADMIN'
    ROL_USUARIO = 'USUARIO'
    ROLES = [(ROL_ADMIN, 'Administrador'), (ROL_USUARIO, 'Usuario')]
    
    rol = models.CharField(max_length=10, choices=ROLES, default=ROL_USUARIO)
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    @property
    def es_admin(self):
        return self.rol == self.ROL_ADMIN
    
    def __str__(self):
        return f"{self.get_full_name() or self.email} ({self.get_rol_display()})"
