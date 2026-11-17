"""
Suite completa de pruebas para Sistema de Gestión de Eventos y Reservas.
Pruebas de permisos, aislamiento, reglas de negocio y concurrencia multi-hilo.
"""
from datetime import date, time
import threading
from django.test import TestCase, Client, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.db.models import Sum

from apps.eventos.models import Evento
from apps.eventos.services import ServicioEventos
from apps.reservas.models import Reserva
from apps.reservas.services import ServicioReservas
from apps.reportes.services import ServicioReportes
from apps.reportes.factory import ReporteFactory, ReporteOcupacion, ReporteAsistencia

Usuario = get_user_model()


def crear_usuario(email, password='test_password123', rol=Usuario.ROL_USUARIO):
    username = email.split('@')[0]
    return Usuario.objects.create_user(
        username=username,
        email=email,
        password=password,
        rol=rol
    )


def crear_evento(nombre="Evento Test", capacidad=10, duracion=60, activo=True, fecha_evento=None):
    if fecha_evento is None:
        fecha_evento = date(2026, 12, 1)
    return Evento.objects.create(
        nombre=nombre,
        fecha=fecha_evento,
        hora=time(10, 0),
        duracion_min=duracion,
        capacidad_maxima=capacidad,
        descripcion="Descripción de prueba",
        activo=activo
    )


class TestPermisosPorRol(TestCase):
    """Verifica que las rutas administrativas estén restringidas en el servidor por rol."""

    def setUp(self):
        self.client = Client()
        self.admin = crear_usuario('admin@test.cl', rol=Usuario.ROL_ADMIN)
        self.usuario = crear_usuario('user@test.cl', rol=Usuario.ROL_USUARIO)
        self.evento = crear_evento()

    def test_admin_accede_a_vistas_gestion(self):
        self.client.force_login(self.admin)
        for url in ['/eventos/admin/', '/reservas/admin/', '/reportes/']:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Admin debería acceder a {url}")

    def test_usuario_comun_recibe_403_en_vistas_admin(self):
        self.client.force_login(self.usuario)
        for url in ['/eventos/admin/', '/reservas/admin/', '/reportes/']:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403, f"Usuario común debe recibir 403 en {url}")

    def test_visitante_anonimo_es_redirigido_a_login(self):
        response = self.client.get('/eventos/admin/')
        self.assertRedirects(response, '/cuentas/login/?next=/eventos/admin/', fetch_redirect_response=False)

    def test_login_credenciales_invalidas_no_revelan_campo(self):
        response = self.client.post('/cuentas/login/', {'email': 'inexistente@demo.cl', 'password': 'mala'})
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any('Credenciales inválidas' in str(m) for m in messages))


class TestAislamientoReservas(TestCase):
    """Verifica que un usuario no pueda ver ni modificar reservas ajenas (RF05)."""

    def setUp(self):
        self.client = Client()
        self.u1 = crear_usuario('maria@test.cl')
        self.u2 = crear_usuario('diego@test.cl')
        self.evento = crear_evento(capacidad=20)
        self.reserva_u1 = ServicioReservas.crear_reserva(self.u1, self.evento.pk, plazas=3)

    def test_usuario_no_puede_ver_reserva_ajena_por_url_directa(self):
        self.client.force_login(self.u2)
        response = self.client.get(f'/reservas/{self.reserva_u1.pk}/')
        self.assertEqual(response.status_code, 403)

    def test_usuario_propietario_si_puede_ver_su_reserva(self):
        self.client.force_login(self.u1)
        response = self.client.get(f'/reservas/{self.reserva_u1.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_mis_inscripciones_solo_muestra_reservas_propias(self):
        reserva_u2 = ServicioReservas.crear_reserva(self.u2, self.evento.pk, plazas=2)
        self.client.force_login(self.u1)
        response = self.client.get('/reservas/mis-inscripciones/')
        self.assertEqual(response.status_code, 200)
        reservas_en_pantalla = list(response.context['reservas'])
        self.assertIn(self.reserva_u1, reservas_en_pantalla)
        self.assertNotIn(reserva_u2, reservas_en_pantalla)


class TestReglasDeNegocioReservas(TestCase):
    """Verifica reglas críticas: capacidad, cancelación, eliminación y asistencia."""

    def setUp(self):
        self.admin = crear_usuario('admin@test.cl', rol=Usuario.ROL_ADMIN)
        self.usuario = crear_usuario('user@test.cl')
        self.evento = crear_evento(capacidad=5)

    def test_rechazo_por_capacidad_insuficiente(self):
        # Intentar reservar 6 plazas en evento de 5
        with self.assertRaises(ValidationError) as ctx:
            ServicioReservas.crear_reserva(self.usuario, self.evento.pk, plazas=6)
        self.assertIn('No hay suficientes plazas', str(ctx.exception))
        self.assertEqual(self.evento.plazas_disponibles, 5)

    def test_evento_inactivo_no_admite_reservas(self):
        evento_inactivo = crear_evento(nombre="Suspendido", activo=False)
        with self.assertRaises(ValidationError) as ctx:
            ServicioReservas.crear_reserva(self.usuario, evento_inactivo.pk, plazas=1)
        self.assertIn('inactivo', str(ctx.exception))

    def test_cancelacion_libera_plazas_una_sola_vez(self):
        reserva = ServicioReservas.crear_reserva(self.usuario, self.evento.pk, plazas=3)
        self.assertEqual(self.evento.plazas_disponibles, 2)

        # Primera cancelación: debe liberar las 3 plazas
        ServicioReservas.cancelar_reserva(reserva.pk, cancelada_por=self.admin)
        self.assertEqual(self.evento.plazas_disponibles, 5)

        # Segunda cancelación: debe fallar y no volver a sumar plazas
        with self.assertRaises(ValidationError) as ctx:
            ServicioReservas.cancelar_reserva(reserva.pk, cancelada_por=self.admin)
        self.assertIn('ya está cancelada', str(ctx.exception))
        self.assertEqual(self.evento.plazas_disponibles, 5)

    def test_no_permitir_bajar_capacidad_bajo_plazas_vigentes(self):
        ServicioReservas.crear_reserva(self.usuario, self.evento.pk, plazas=4)
        # Intentar reducir capacidad a 3 teniendo 4 vigentes
        with self.assertRaises(ValidationError) as ctx:
            ServicioEventos.actualizar_evento(self.evento.pk, {'capacidad_maxima': 3})
        self.assertIn('No se puede reducir la capacidad', str(ctx.exception))

    def test_eliminar_evento_con_reservas_lo_desactiva(self):
        ServicioReservas.crear_reserva(self.usuario, self.evento.pk, plazas=2)
        resultado = ServicioEventos.eliminar_o_desactivar(self.evento.pk)
        self.assertEqual(resultado, 'desactivado')
        self.evento.refresh_from_db()
        self.assertFalse(self.evento.activo)

    def test_eliminar_evento_sin_reservas_lo_elimina_fisicamente(self):
        evento_vacio = crear_evento(nombre="Sin reservas")
        pk = evento_vacio.pk
        resultado = ServicioEventos.eliminar_o_desactivar(pk)
        self.assertEqual(resultado, 'eliminado')
        self.assertFalse(Evento.objects.filter(pk=pk).exists())

    def test_no_se_puede_cancelar_reserva_con_asistencia(self):
        reserva = ServicioReservas.crear_reserva(self.usuario, self.evento.pk, plazas=3)
        ServicioReservas.registrar_asistentes(reserva.pk, 2)
        with self.assertRaises(ValidationError) as ctx:
            ServicioReservas.cancelar_reserva(reserva.pk, cancelada_por=self.admin)
        self.assertIn('asistencia registrada', str(ctx.exception))

    def test_asistentes_debe_estar_entre_0_y_plazas(self):
        reserva = ServicioReservas.crear_reserva(self.usuario, self.evento.pk, plazas=4)
        with self.assertRaises(ValidationError):
            ServicioReservas.registrar_asistentes(reserva.pk, 5)
        with self.assertRaises(ValidationError):
            ServicioReservas.registrar_asistentes(reserva.pk, -1)

    def test_corregir_asistencia_reemplaza_no_suma(self):
        reserva = ServicioReservas.crear_reserva(self.usuario, self.evento.pk, plazas=4)
        ServicioReservas.registrar_asistentes(reserva.pk, 2)
        reserva.refresh_from_db()
        self.assertEqual(reserva.asistentes, 2)

        # Modificar a 4: debe ser 4, NO 6
        ServicioReservas.registrar_asistentes(reserva.pk, 4)
        reserva.refresh_from_db()
        self.assertEqual(reserva.asistentes, 4)


class TestReportesYFactory(TestCase):
    """Verifica el patrón Factory y las reglas de negocio de los reportes."""

    def setUp(self):
        self.admin = crear_usuario('admin@test.cl', rol=Usuario.ROL_ADMIN)
        self.usuario = crear_usuario('user@test.cl')
        self.evento = crear_evento(nombre="Taller Cocina", capacidad=10, fecha_evento=date(2026, 12, 10))
        self.reserva = ServicioReservas.crear_reserva(self.usuario, self.evento.pk, plazas=5)
        ServicioReservas.registrar_asistentes(self.reserva.pk, 4)

    def test_factory_devuelve_instancia_correcta(self):
        rep_ocup = ReporteFactory.crear('ocupacion')
        self.assertIsInstance(rep_ocup, ReporteOcupacion)

        rep_asist = ReporteFactory.crear('asistencia')
        self.assertIsInstance(rep_asist, ReporteAsistencia)

        with self.assertRaises(ValueError):
            ReporteFactory.crear('tipo_inexistente')

    def test_reporte_ocupacion_calcula_porcentaje_correcto(self):
        datos = ServicioReportes.generar_reporte('ocupacion', evento_id=self.evento.pk)
        self.assertEqual(len(datos['filas']), 1)
        fila = datos['filas'][0]
        self.assertEqual(fila['plazas_vigentes'], 5)
        self.assertEqual(fila['porcentaje'], 50.0)

    def test_reporte_asistencia_muestra_asistentes_y_pendientes(self):
        datos = ServicioReportes.generar_reporte('asistencia', evento_id=self.evento.pk)
        fila = datos['filas'][0]
        self.assertEqual(fila['total_asistentes'], 4)
        self.assertEqual(fila['pendientes_registro'], 0)

    def test_rango_fechas_invertido_es_rechazado(self):
        with self.assertRaises(ValidationError) as ctx:
            ServicioReportes.generar_reporte(
                'ocupacion',
                fecha_inicio=date(2026, 12, 31),
                fecha_fin=date(2026, 12, 1)
            )
        self.assertIn('invertido', str(ctx.exception))


class TestConcurrenciaReservas(TransactionTestCase):
    """Prueba de concurrencia real usando hilos sobre la base de datos."""

    def setUp(self):
        self.evento = crear_evento(nombre="Evento Concurrente", capacidad=6)
        self.usuarios = [crear_usuario(f'user_thread_{i}@demo.cl') for i in range(8)]
        self.exitos = []
        self.rechazados = []

    def test_concurrencia_no_sobrepasa_capacidad_maxima(self):
        """
        8 hilos intentan reservar 2 plazas cada uno en un evento de capacidad 6.
        Bajo ninguna circunstancia las reservas vigentes pueden exceder la capacidad (6).
        """
        import time
        from django.db import OperationalError

        def intentar_reserva(usuario):
            for intento in range(15):
                try:
                    ServicioReservas.crear_reserva(usuario, self.evento.pk, plazas=2)
                    self.exitos.append(usuario.email)
                    return
                except OperationalError:
                    time.sleep(0.05 * (intento + 1))
                    continue
                except ValidationError:
                    self.rechazados.append(usuario.email)
                    return
                except Exception:
                    pass

        hilos = [threading.Thread(target=intentar_reserva, args=(u,)) for u in self.usuarios]
        for h in hilos:
            h.start()
        for h in hilos:
            h.join()

        # Verificar en base de datos
        plazas_totales = Reserva.objects.filter(
            evento=self.evento,
            estado=Reserva.ESTADO_VIGENTE
        ).aggregate(total=Sum('plazas'))['total'] or 0

        # Regla crítica: la concurrencia NUNCA debe sobrepasar la capacidad
        self.assertLessEqual(
            plazas_totales,
            self.evento.capacidad_maxima,
            f"Se sobrepasó la capacidad máxima: {plazas_totales} > {self.evento.capacidad_maxima}"
        )
        self.assertGreater(plazas_totales, 0, "Al menos una reserva debió concretarse")
        self.assertTrue(len(self.exitos) >= 1)
        self.assertEqual(plazas_totales, len(self.exitos) * 2)
