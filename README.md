# Gestión de Eventos

Sistema de gestión de eventos desarrollado con Django 5.1.4.

## Requisitos

- Python 3.10+
- pip

## Instalación

```bash
# Clonar o descomprimir el proyecto
cd gestion_eventos

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Copiar configuración de entorno
copy .env.example .env
# Editar .env con tus valores reales

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

## Estructura del proyecto

```
gestion_eventos/
├── apps/
│   ├── cuentas/        # Autenticación y usuarios
│   ├── eventos/        # Gestión de eventos
│   ├── reservas/       # Reservas de asistentes
│   └── reportes/       # Reportes y estadísticas
├── gestion_eventos/    # Configuración Django (settings, urls, wsgi)
├── templates/          # Plantillas HTML globales
│   └── partials/       # Fragmentos reutilizables
├── static/
│   └── css/            # Hojas de estilo
├── manage.py
├── requirements.txt
└── .env.example
```

## Apps

| App        | Descripción                                               |
|------------|-----------------------------------------------------------|
| `cuentas`  | Modelo de usuario personalizado, login, registro, perfil  |
| `eventos`  | CRUD de eventos, catálogo público, estado (VIGENTE/CANCELADA) |
| `reservas` | Alta y cancelación de reservas, control de cupos          |
| `reportes` | Estadísticas de asistencia, exportación de datos          |

## Base de datos

Por defecto usa **SQLite** (ideal para desarrollo). Para MySQL, edita `.env`:

```
DB_ENGINE=django.db.backends.mysql
DB_NAME=gestion_eventos
DB_USER=root
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=3306
```

Y actualiza `DATABASES` en `gestion_eventos/settings.py` según los comentarios incluidos.

## Variables de entorno (.env)

| Variable      | Descripción                        | Default                     |
|---------------|------------------------------------|-----------------------------|
| `SECRET_KEY`  | Clave secreta de Django            | valor inseguro de desarrollo |
| `DEBUG`       | Modo debug                         | `True`                      |
| `DB_ENGINE`   | Motor de base de datos             | sqlite3                     |
| `DB_NAME`     | Nombre de la base de datos         | db.sqlite3                  |
| `DB_USER`     | Usuario de la base de datos        | —                           |
| `DB_PASSWORD` | Contraseña de la base de datos     | —                           |
| `DB_HOST`     | Host de la base de datos           | localhost                   |
| `DB_PORT`     | Puerto de la base de datos         | 3306                        |

## Comandos útiles

```bash
# Crear migraciones después de cambiar modelos
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Verificar configuración
python manage.py check

# Shell interactivo
python manage.py shell

# Ejecutar tests
python manage.py test
```

## Licencia

Proyecto académico — Ingeniería de Software.
