# Sistema de Gestión de Eventos y Reservas

Prototipo web funcional y listo para producción para un Centro Comunitario, desarrollado con **Django 5 (Python)**, **MySQL 8**, arquitectura por capas y orquestación con **Docker**, **Gunicorn** y **Caddy**.

---

## 🏛️ Arquitectura del Sistema

El sistema implementa una arquitectura desacoplada por capas con responsabilidades estrictamente delimitadas:

```text
+---------------------------------------------------------------------------------+
|                                 USUARIO / NAVEGADOR                              |
+---------------------------------------+-----------------------------------------+
                                        | HTTP / HTTPS (Puertos 80, 443)
+---------------------------------------v-----------------------------------------+
|                    REVERSE PROXY: Caddy 2 (TLS Automático)                       |
+---------------------------------------+-----------------------------------------+
                                        | Proxy inverso (Puerto interno 8000)
+---------------------------------------v-----------------------------------------+
|                  SERVIDOR DE APLICACIÓN: Gunicorn (WSGI)                        |
|                                                                                 |
|   +-------------------------------------------------------------------------+   |
|   |                        CAPA DE PRESENTACIÓN (Vistas)                    |   |
|   |          apps.cuentas  |  apps.eventos  |  apps.reservas  |  apps.reportes|   |
|   +-----------------------------------+-------------------------------------+   |
|                                       | Invoca servicios                        |
|   +-----------------------------------v-------------------------------------+   |
|   |                     CAPA DE LÓGICA DE NEGOCIO (services.py)             |   |
|   |  - select_for_update() en transaction.atomic()                          |   |
|   |  - Cálculo dinámico de disponibilidad (Capacidad - Plazas Vigentes)     |   |
|   |  - Patrones de Diseño: Factory, Observer, Singleton, Adapter            |   |
|   +-----------------------------------+-------------------------------------+   |
|                                       | Acceso a datos ORM                      |
|   +-----------------------------------v-------------------------------------+   |
|   |                      CAPA DE PERSISTENCIA (Modelos Django)              |   |
|   |           Usuario (AbstractUser), Evento, Reserva, CheckConstraints     |   |
|   +-------------------------------------------------------------------------+   |
+---------------------------------------+-----------------------------------------+
                                        | TCP Socket interno (Puerto 3306)
+---------------------------------------v-----------------------------------------+
|                BASE DE DATOS: MySQL 8 (Aislada, sin puertos al host)            |
|                        Volumen Persistente: mysql_data                          |
+---------------------------------------------------------------------------------+
```

### Patrones de Diseño Implementados
1. **Factory (`apps.reportes.factory.ReporteFactory`)**: Devuelve instancias polimórficas de `ReporteOcupacion` o `ReporteAsistencia` que heredan de `ReporteBase` e implementan la interfaz `Reporte.generar(filtros)`.
2. **Observer (`apps.reservas.signals`)**: Al confirmarse atómicamente una reserva, `transaction.on_commit` emite la señal `reserva_confirmada`, la cual es capturada por observadores que registran la transacción en los logs de auditoría.
3. **Singleton (`apps.cuentas.singleton.ConfiguracionSistema`)**: Instancia única por proceso que centraliza la configuración del centro comunitario apoyándose en `django.conf.settings`.
4. **Adapter (`apps.reservas.adapter.AdaptadorCorreoConsola`)**: Interfaz `ServicioCorreoInterface` adaptada para notificaciones en consola; los fallos del correo son controlados y nunca revierten la reserva.

---

## 🔑 Credenciales de Demostración

| Rol | Correo Electrónico | Contraseña | Descripción |
|---|---|---|---|
| **Administrador** | `admin@demo.cl` | `admin123` | Acceso a panel de eventos, cancelación, registro de asistentes y reportes |
| **Usuario 1** | `usuario@demo.cl` | `user123` | Usuario estándar (María González), inscripciones y reservas |
| **Usuario 2** | `diego@demo.cl` | `user123` | Usuario estándar (Diego Ramírez), reservas independientes |

---

## 🚀 Instalación y Ejecución Local

### Opción A: Despliegue con Docker (Recomendado para Producción/Evaluación)

**Requisitos:** Docker Engine 20.10+ y Docker Compose v2+.

1. Clonar o descomprimir el proyecto en el servidor o equipo local.
2. Copiar el archivo de variables de entorno:
   ```bash
   cp .env.example .env
   ```
3. Construir y levantar los 3 contenedores (`db`, `web`, `caddy`):
   ```bash
   docker compose up -d --build
   ```
4. Sembrar los datos de prueba:
   ```bash
   docker compose exec web python manage.py seed_demo
   ```
5. Acceder en el navegador:
   - Aplicación Web: [http://localhost](http://localhost) (o [http://127.0.0.1](http://127.0.0.1))
   - El puerto de MySQL (3306) **no está expuesto al host** por razones de seguridad; la comunicación ocurre exclusivamente dentro de la red interna de Docker.

### Opción B: Ejecución Local Rápida (Python + SQLite)

**Requisitos:** Python 3.11+, pip.

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecutar migraciones y sembrar demo:
   ```bash
   python manage.py migrate
   python manage.py seed_demo
   ```
3. Iniciar el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```
4. Abrir [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## 🧪 Ejecución de Pruebas Automatizadas

El proyecto incluye una suite de **21 pruebas unitarias, de integración y de concurrencia**:

```bash
# Con Docker:
make test
# O directamente con Docker Compose:
docker compose exec web python manage.py test

# En entorno local:
python manage.py test
```

### Cobertura de Pruebas:
- **Permisos por Rol:** Acceso restringido en el servidor a administradores (403 para usuarios comunes, redirección a login para anónimos).
- **Aislamiento de Datos (RF05):** Un usuario regular no puede visualizar ni modificar reservas ajenas (responde 403 Forbidden incluso por URL directa).
- **Capacidad y Disponibilidad:** Rechazo atómico de solicitudes que excedan las plazas libres; eventos inactivos no admiten reservas.
- **Liberación Única:** Cancelar una reserva libera plazas una sola vez; reintentar la cancelación lanza error y no duplica plazas.
- **Protección de Asistencia:** No se puede cancelar una reserva con asistencia confirmada (Regla 5).
- **Asistencia Efectiva:** Reemplazo (no adición) de asistentes y validación entre 0 y el tope contratado.
- **Reportes:** Cálculo de ocupación (evitando división por cero) y rechazo de rangos de fecha invertidos.
- **Concurrencia Multi-hilo (`TransactionTestCase`):** 8 hilos ejecutando reservas simultáneas sobre la misma fila de evento; `select_for_update()` garantiza que el total reservado **nunca sobrepase la capacidad máxima**.

---

## 🛠️ Comandos Útiles del Makefile

```bash
make up       # Construye y levanta los servicios en segundo plano
make down     # Detiene los contenedores
make logs     # Muestra los logs en tiempo real
make seed     # Carga los datos de demostración
make test     # Corre la suite de pruebas completa
make backup   # Genera un respaldo comprimido .sql.gz de MySQL
make restore  # Restaura el respaldo más reciente
make check    # Ejecuta el linter Ruff
```

---

## ☁️ Guía de Despliegue en un Servidor Ubuntu en la Nube

Guía paso a paso para desplegar en una instancia limpia de **Ubuntu 22.04 / 24.04 LTS** (DigitalOcean, AWS EC2, Linode, Hetzner, etc.) sin depender de GitHub:

### Paso 1: Conectarse al servidor e instalar Docker
```bash
ssh usuario@IP_DEL_SERVIDOR

# Actualizar repositorios e instalar paquetes base
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg lsb-release ufw

# Instalar Docker oficial y Docker Compose
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```
*(Cierra y vuelve a abrir la sesión SSH para aplicar los permisos de grupo Docker).*

### Paso 2: Configurar el Firewall (UFW)
Solo deben quedar expuestos los puertos **SSH (22)**, **HTTP (80)** y **HTTPS (443)**. La base de datos MySQL permanece aislada en la red interna de contenedores:
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status verbose
```

### Paso 3: Copiar el proyecto al servidor por SCP o Rsync (Sin GitHub)
Desde tu máquina local (terminal de tu equipo de desarrollo):
```bash
# Usando rsync para copiar el código excluyendo temporales y git local:
rsync -avz --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' --exclude 'db.sqlite3' \
    ./ usuario@IP_DEL_SERVIDOR:/home/usuario/gestion_eventos/
```

### Paso 4: Configurar Variables de Entorno en el Servidor
En el servidor remoto:
```bash
cd /home/usuario/gestion_eventos
cp .env.example .env
nano .env
```
Ajusta los valores de producción:
```ini
SECRET_KEY=clave_secreta_de_produccion_muy_larga_y_aleatoria_2026
DEBUG=False
ALLOWED_HOSTS=midominio.cl,www.midominio.cl,IP_DEL_SERVIDOR
CSRF_TRUSTED_ORIGINS=https://midominio.cl,https://www.midominio.cl

# Base de datos MySQL
DB_ENGINE=mysql
DB_NAME=gestion_eventos
DB_USER=evento_user
DB_PASSWORD=contrasena_robusta_para_mysql_2026
MYSQL_ROOT_PASSWORD=contrasena_root_super_segura_2026

# Dominio y TLS automático con Caddy
DOMAIN=midominio.cl
ACME_EMAIL=admin@midominio.cl

# Ajustes de Seguridad HTTPS
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

### Paso 5: Apuntar el Dominio DNS
En el proveedor de DNS (Cloudflare, Namecheap, etc.), crea los siguientes registros apuntando a la IP pública del servidor:
- Tipo `A`: `@` &rarr; `IP_DEL_SERVIDOR`
- Tipo `A`: `www` &rarr; `IP_DEL_SERVIDOR`

### Paso 6: Levantar y Sembrar la Aplicación
```bash
cd /home/usuario/gestion_eventos

# Construir y arrancar servicios en segundo plano
docker compose up -d --build

# Verificar que los contenedores estén sanos (healthy)
docker compose ps

# Sembrar los datos de demostración
docker compose exec web python manage.py seed_demo
```
**Caddy obtendrá y renovará automáticamente los certificados SSL/TLS Let's Encrypt para tu dominio.** Tu sitio estará disponible de forma segura en `https://midominio.cl`.

### Paso 7: Configurar Respaldo Automático en Crontab (RNF07)
Para cumplir con la política de respaldos automáticos diarios a las 02:00 AM:
```bash
crontab -e
# Agregar la siguiente línea:
0 2 * * * /home/usuario/gestion_eventos/scripts/backup.sh >> /home/usuario/gestion_eventos/backups/backup.log 2>&1
```

---

## 📸 Catálogo de Pantallas para Evidencia
Consulta el documento completo [docs/EVIDENCIA.md](docs/EVIDENCIA.md) para ver la lista de URLs y pasos para capturar las evidencias de evaluación.
