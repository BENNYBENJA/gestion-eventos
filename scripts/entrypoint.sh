#!/bin/sh
set -e

echo "=== [ENTRYPOINT] Iniciando Sistema de Gestión de Eventos y Reservas ==="

# Si el motor es MySQL, esperar a que el servidor esté listo
if [ "$DB_ENGINE" = "mysql" ] || [ "$DB_ENGINE" = "django.db.backends.mysql" ]; then
    echo "=== [ENTRYPOINT] Esperando a que el servicio MySQL ($DB_HOST:$DB_PORT) esté disponible..."
    
    python << 'EOF'
import sys
import time
import socket
import os

host = os.environ.get('DB_HOST', 'db')
port = int(os.environ.get('DB_PORT', '3306'))

start_time = time.time()
while True:
    try:
        with socket.create_connection((host, port), timeout=3):
            print(f"=== [ENTRYPOINT] Conexión TCP exitosa a MySQL en {host}:{port}")
            sys.exit(0)
    except Exception as e:
        if time.time() - start_time > 60:
            print(f"=== [ENTRYPOINT] ERROR: Tiempo de espera agotado conectando a MySQL ({e})")
            sys.exit(1)
        time.sleep(2)
EOF

fi

# Ejecutar migraciones automáticas
echo "=== [ENTRYPOINT] Aplicando migraciones de base de datos..."
python manage.py migrate --noinput

# Recolectar archivos estáticos para WhiteNoise / Caddy
echo "=== [ENTRYPOINT] Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "=== [ENTRYPOINT] Preparación completada. Arrancando servidor..."
exec "$@"
