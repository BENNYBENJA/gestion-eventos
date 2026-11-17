#!/bin/bash
# ==============================================================================
# Script de Restauración de Base de Datos MySQL (RNF07)
# Restaura un dump comprimido con gzip sobre la base de datos
# ==============================================================================

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
BACKUP_FILE="${1:-}"

DB_CONTAINER="${DB_CONTAINER:-gestion_eventos_db}"
DB_NAME="${DB_NAME:-gestion_eventos}"
DB_USER="${DB_USER:-root}"
MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:-root_super_secure_password_2026}"

# Si no se pasó argumento, buscar el respaldo más reciente
if [ -z "${BACKUP_FILE}" ]; then
    if [ ! -d "${BACKUP_DIR}" ] || [ -z "$(ls -A "${BACKUP_DIR}"/*.sql.gz 2>/dev/null)" ]; then
        echo "❌ Error: No se encontraron archivos de respaldo en ${BACKUP_DIR}"
        echo "Uso: $0 [ruta_al_archivo_backup.sql.gz]"
        exit 1
    fi
    BACKUP_FILE=$(ls -t "${BACKUP_DIR}"/*.sql.gz | head -n 1)
    echo "→ No se especificó archivo. Usando el más reciente: ${BACKUP_FILE}"
fi

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "❌ Error: El archivo ${BACKUP_FILE} no existe."
    exit 1
fi

echo "=========================================================="
echo " [RESTORE] Iniciando restauración de base de datos..."
echo " Origen:        ${BACKUP_FILE}"
echo " Base de datos: ${DB_NAME}"
echo "=========================================================="

# Confirmación de seguridad
read -r -p "⚠️  ADVERTENCIA: Esta operación sobrescribirá los datos actuales en '${DB_NAME}'. ¿Continuar? [s/N] " response
case "$response" in
    [sS][iI]|[sS])
        ;;
    *)
        echo "Operación cancelada por el usuario."
        exit 0
        ;;
esac

if docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER}$"; then
    echo "→ Restaurando en contenedor Docker '${DB_CONTAINER}'..."
    gunzip -c "${BACKUP_FILE}" | docker exec -i "${DB_CONTAINER}" mysql \
        -u"${DB_USER}" \
        -p"${MYSQL_ROOT_PASSWORD}" \
        --default-character-set=utf8mb4 \
        "${DB_NAME}"
else
    echo "→ Contenedor no encontrado. Intentando mysql local..."
    DB_HOST="${DB_HOST:-127.0.0.1}"
    DB_PORT="${DB_PORT:-3306}"
    gunzip -c "${BACKUP_FILE}" | mysql \
        -h"${DB_HOST}" \
        -P"${DB_PORT}" \
        -u"${DB_USER}" \
        -p"${MYSQL_ROOT_PASSWORD}" \
        --default-character-set=utf8mb4 \
        "${DB_NAME}"
fi

echo "=========================================================="
echo " ✅ Base de datos restaurada exitosamente desde ${BACKUP_FILE}"
echo "=========================================================="
