# ==============================================================================
# Dockerfile Multi-Stage para Sistema de Gestión de Eventos y Reservas
# ==============================================================================

# STAGE 1: Builder
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Dependencias del sistema necesarias para compilar paquetes (como mysqlclient)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Compilar dependencias en un directorio local
RUN pip install --prefix=/install -r requirements.txt


# STAGE 2: Imagen Final de Producción (Slim + Usuario no root)
FROM python:3.12-slim-bookworm AS final

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# Instalar librerías de runtime necesarias para MySQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-mysql-client \
    libmariadb3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no root con UID explícito
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m -s /bin/bash appuser

WORKDIR /app

# Copiar dependencias instaladas desde la etapa builder
COPY --from=builder /install /usr/local

# Crear carpetas necesarias y asignar permisos
RUN mkdir -p /app/staticfiles /app/media /app/scripts && \
    chown -R appuser:appgroup /app

# Copiar código fuente del proyecto
COPY --chown=appuser:appgroup . /app/

# Dar permisos de ejecución al script entrypoint
RUN chmod +x /app/scripts/entrypoint.sh 2>/dev/null || true

USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["gunicorn", "gestion_eventos.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-"]
