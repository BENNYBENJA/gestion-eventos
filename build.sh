#!/usr/bin/env bash
# exit on error
set -o errexit

echo "==> Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Recolectando archivos estáticos para WhiteNoise..."
python manage.py collectstatic --no-input

echo "==> Aplicando migraciones de base de datos..."
python manage.py migrate --no-input

echo "==> Cargando datos de demostración iniciales (seed_demo)..."
python manage.py seed_demo

echo "==> Build finalizado exitosamente."
