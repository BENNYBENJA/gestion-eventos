# Guía de Capturas de Pantalla y Evidencia de Evaluación Académica

Este documento detalla cada una de las pantallas del **Sistema de Gestión de Eventos y Reservas**, sus URLs exactas, el rol necesario y los pasos para capturar las evidencias funcionales requeridas.

---

## Matriz de Evidencias y URLs

| ID | Pantalla / Funcionalidad | URL Local | Rol Requerido | Elementos a Destacar en la Captura |
|----|--------------------------|-----------|---------------|------------------------------------|
| **CAP-01** | Inicio de Sesión (Login) | `http://localhost/cuentas/login/` (o `:8000`) | Anónimo | Formulario limpio con correo y contraseña, caja con credenciales de demo, enlace al catálogo. |
| **CAP-02** | Catálogo con Búsqueda y Filtros | `http://localhost/` | Anónimo o Usuario | Buscador por nombre y fecha, cards de eventos, barras de ocupación con porcentaje y badge de estado (Disponible, Pocas plazas, LLENO). |
| **CAP-03** | Detalle de Evento y Formulario de Reserva | `http://localhost/eventos/1/` | Usuario (`usuario@demo.cl`) | Resumen del evento, fecha, horario, indicador de disponibilidad en tiempo real y botón "Hacer una reserva". |
| **CAP-04** | Reserva Exitosa | `http://localhost/reservas/crear/1/` | Usuario (`usuario@demo.cl`) | Mensaje flash verde de confirmación `✅ Reserva confirmada: X plaza(s)...` redirigiendo a Mis Inscripciones. |
| **CAP-05** | Reserva Rechazada (Capacidad Insuficiente) | `http://localhost/reservas/crear/3/` | Usuario (`usuario@demo.cl`) | Evento casi lleno (2 plazas disponibles). Intentar reservar 5 plazas: mensaje de error `❌ No hay suficientes plazas. Disponibles: 2, solicitadas: 5.` sin guardar registros parciales. |
| **CAP-06** | Mis Inscripciones (Aislamiento de Datos) | `http://localhost/reservas/mis-inscripciones/` | Usuario (`usuario@demo.cl`) | Tabla con únicamente las reservas del usuario autenticado, estado Vigente/Cancelada y botón de comprobante. |
| **CAP-07** | Intento de Acceso a Reserva Ajena (Seguridad 403) | `http://localhost/reservas/2/` | Usuario (`usuario@demo.cl`) | Acceso por URL directa a la reserva perteneciente a otro usuario (`diego@demo.cl`). Respuesta HTTP 403 Forbidden demostrando el control del lado del servidor. |
| **CAP-08** | Gestión de Eventos (CRUD Admin) | `http://localhost/eventos/admin/` | Admin (`admin@demo.cl`) | Tabla administrativa con todos los eventos (activos e inactivos), capacidades, ocupación, botones de activar/desactivar, editar y eliminar con protección de historial. |
| **CAP-09** | Gestión de Reservas con Cancelación y Asistencia | `http://localhost/reservas/admin/` | Admin (`admin@demo.cl`) | Filtros superiores por evento/email/fecha, reservas con badge Vigente y Cancelada, botones de Asistencia y Cancelar. |
| **CAP-10** | Registro de Asistentes Efectivos | `http://localhost/reservas/admin/1/asistentes/` | Admin (`admin@demo.cl`) | Formulario con validación entre 0 y el total de plazas contratadas, explicando el reemplazo del valor (Regla 6). |
| **CAP-11** | Confirmación de Cancelación de Reserva | `http://localhost/reservas/admin/2/cancelar/` | Admin (`admin@demo.cl`) | Advertencia de liberación de plazas única vez y bloqueo si ya cuenta con asistencia registrada. |
| **CAP-12** | Reporte de Ocupación | `http://localhost/reportes/?tipo=ocupacion` | Admin (`admin@demo.cl`) | Tabla con plazas vigentes, capacidad total, porcentaje calculado con fórmula `(plazas/capacidad)*100` y barras de progreso. |
| **CAP-13** | Reporte de Asistencia | `http://localhost/reportes/?tipo=asistencia` | Admin (`admin@demo.cl`) | Tabla con plazas confirmadas, asistentes efectivos registrados y conteo de reservas pendientes de pase de lista. |
| **CAP-14** | Validación de Rango de Fechas Invertido | `http://localhost/reportes/?tipo=ocupacion&fecha_inicio=2026-12-31&fecha_fin=2026-12-01` | Admin (`admin@demo.cl`) | Mensaje de validación: alerta roja indicando que la fecha de inicio no puede ser posterior a la fecha de término. |

---

## Procedimiento Paso a Paso para la Sesión de Capturas

1. **Cargar los datos iniciales:**
   ```bash
   python manage.py seed_demo
   ```
2. **Iniciar sesión como Usuario Regular:**
   - Navegar a `/cuentas/login/`
   - Ingresar con `usuario@demo.cl` / `user123`
   - Tomar capturas de: Catálogo (`/`), Intento de reserva con cupos excedidos, Reserva exitosa, Mis Inscripciones (`/reservas/mis-inscripciones/`).
3. **Comprobar la regla de aislamiento (RF05):**
   - Estando como `usuario@demo.cl`, intentar acceder a la reserva de Diego en `/reservas/2/`.
   - Se obtendrá la pantalla de error **403 Forbidden**.
4. **Iniciar sesión como Administrador:**
   - Cerrar sesión y acceder con `admin@demo.cl` / `admin123`.
   - Tomar capturas de:
     - `/eventos/admin/`
     - `/reservas/admin/`
     - `/reservas/admin/1/asistentes/`
     - `/reportes/?tipo=ocupacion`
     - `/reportes/?tipo=asistencia`
