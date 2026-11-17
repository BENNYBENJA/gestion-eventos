#!/bin/bash
# ==============================================================================
# Script de Respaldo Automatizado de Base de Datos MySQL (RNF07)
# Genera un dump comprimido con gzip etiquetado con marca temporal
# ==============================================================================

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/backup_gestion_eventos_${TIMESTAMP}.sql.gz"

DB_CONTAINER="${DB_CONTAINER:-gestion_eventos_db}"
DB_NAME="${DB_NAME:-gestion_eventos}"
DB_USER="${DB_USER:-root}"
MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:-root_super_secure_password_2026}"

mkdir -p "${BACKUP_DIR}"

echo "=========================================================="
echo " [BACKUP] Iniciando respaldo de la base de datos MySQL..."
echo " Base de datos: ${DB_NAME}"
echo " Destino:       ${BACKUP_FILE}"
echo "=========================================================="

# Comprobar si el contenedor Docker de MySQL está en ejecución
if docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER}$"; then
    echo "→ Extrayendo volcado desde el contenedor Docker '${DB_CONTAINER}'..."
    docker exec "${DB_CONTAINER}" mysqldump \
        -u"${DB_USER}" \
        -p"${MYSQL_ROOT_PASSWORD}" \
        --single-transaction \
        --quick \
        --default-character-set=utf8mb4 \
        "${DB_NAME}" | gzip -9 > "${BACKUP_FILE}"
else
    echo "→ Contenedor no encontrado. Intentando mysqldump local..."
    DB_HOST="${DB_HOST:-127.0.0.1}"
    DB_PORT="${DB_PORT:-3306}"
    mysqldump \
        -h"${DB_HOST}" \
        -P"${DB_PORT}" \
        -u"${DB_USER}" \
        -p"${MYSQL_ROOT_PASSWORD}" \
        --single-transaction \
        --quick \
        --default-character-set=utf8mb4 \
        "${DB_NAME}" | gzip -9 > "${BACKUP_FILE}"
fi

FILE_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
echo "=========================================================="
echo " ✅ Respaldo completado exitosamente."
echo " Archivo: ${BACKUP_FILE} (${FILE_SIZE})"
echo "=========================================================="
