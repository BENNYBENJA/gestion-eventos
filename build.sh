#!/usr/bin/env bash
# exit on error
set -o errexit

echo "==> Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r requirements.txt || pip install Django==5.1.4 python-decouple==3.8 gunicorn==23.0.0 whitenoise==6.8.2 sqlparse==0.5.3 asgiref==3.8.1 PyMySQL==1.1.1 cryptography==44.0.0

echo "==> Recolectando archivos estaticos..."
python manage.py collectstatic --no-input

echo "==> Aplicando migraciones de base de datos..."
python manage.py migrate --no-input

echo "==> Cargando datos de demostracion..."
python manage.py seed_demo

echo "==> Build finalizado exitosamente."
