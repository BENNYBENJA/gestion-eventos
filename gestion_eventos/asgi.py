"""
ASGI config for gestion_eventos project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_eventos.settings')

application = get_asgi_application()
