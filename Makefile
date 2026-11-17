# ==============================================================================
# Makefile para Sistema de Gestión de Eventos y Reservas
# ==============================================================================

.PHONY: help up down logs seed test backup restore shell check

help:
	@echo "Comandos disponibles:"
	@echo "  make up       - Construye y levanta todos los contenedores en segundo plano"
	@echo "  make down     - Detiene y remueve los contenedores"
	@echo "  make logs     - Muestra los logs en tiempo real de todos los servicios"
	@echo "  make seed     - Carga los datos de demostración en la base de datos"
	@echo "  make test     - Ejecuta la suite de pruebas unitarias y de concurrencia"
	@echo "  make backup   - Genera un respaldo comprimido de la base de datos MySQL"
	@echo "  make restore  - Restaura el respaldo más reciente de MySQL"
	@echo "  make shell    - Abre una consola interactiva dentro del contenedor Django"
	@echo "  make check    - Ejecuta ruff y verificaciones de calidad"

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

seed:
	docker compose exec web python manage.py seed_demo

test:
	docker compose exec web python manage.py test

backup:
	@chmod +x scripts/backup.sh 2>/dev/null || true
	./scripts/backup.sh

restore:
	@chmod +x scripts/restore.sh 2>/dev/null || true
	./scripts/restore.sh

shell:
	docker compose exec web python manage.py shell

check:
	ruff check .
