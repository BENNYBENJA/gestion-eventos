"""
Comando para sembrar datos de demostración para el Sistema de Gestión de Eventos y Reservas.
"""
from datetime import date, time
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.eventos.models import Evento
from apps.reservas.models import Reserva

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Carga datos iniciales de demostración para evaluación académica'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Inicializando base de datos con datos de demostración...'))

        # 1. Limpieza de datos anteriores para evitar duplicados
        Reserva.objects.all().delete()
        Evento.objects.all().delete()
        Usuario.objects.filter(email__in=[
            'admin@demo.cl', 'usuario@demo.cl', 'diego@demo.cl'
        ]).delete()

        # 2. Creación de Usuarios con contraseñas hasheadas
        self.stdout.write('Creando usuarios del sistema...')

        admin = Usuario.objects.create_superuser(
            username='admin',
            email='admin@demo.cl',
            password='admin123',
            first_name='Laura',
            last_name='Administradora',
            rol=Usuario.ROL_ADMIN,
        )

        usuario1 = Usuario.objects.create_user(
            username='usuario',
            email='usuario@demo.cl',
            password='user123',
            first_name='María',
            last_name='González',
            rol=Usuario.ROL_USUARIO,
        )

        usuario2 = Usuario.objects.create_user(
            username='diego',
            email='diego@demo.cl',
            password='user123',
            first_name='Diego',
            last_name='Ramírez',
            rol=Usuario.ROL_USUARIO,
        )

        self.stdout.write(self.style.SUCCESS('  ✓ Usuarios creados con éxito.'))

        # 3. Creación de Eventos (Noviembre - Diciembre 2026)
        self.stdout.write('Creando catálogo de eventos...')

        # Evento 1: Taller de Huerto Comunitario
        huerto = Evento.objects.create(
            nombre='Taller de Huerto Comunitario',
            fecha=date(2026, 11, 22),
            hora=time(10, 0),
            duracion_min=120,
            capacidad_maxima=20,
            descripcion=(
                'Aprende a cultivar tus propios vegetales y hierbas aromáticas en casa. '
                'Taller práctico con entrega de kit de cultivo y sustrato orgánico.'
            ),
            activo=True,
        )

        # Evento 2: Clase abierta de yoga (Capacidad 60)
        yoga = Evento.objects.create(
            nombre='Clase Abierta de Yoga',
            fecha=date(2026, 11, 29),
            hora=time(9, 30),
            duracion_min=90,
            capacidad_maxima=60,
            descripcion=(
                'Sesión matutina de hatha yoga al aire libre para todos los niveles de experiencia. '
                'Traer esterilla personal y botella de agua reutilizable.'
            ),
            activo=True,
        )

        # Evento 3: Cine al aire libre (Casi lleno: 28/30 reservadas)
        cine = Evento.objects.create(
            nombre='Cine al Aire Libre: Noche Familiar',
            fecha=date(2026, 12, 5),
            hora=time(20, 30),
            duracion_min=140,
            capacidad_maxima=30,
            descripcion=(
                'Proyección de película para toda la familia en el anfiteatro central del centro. '
                'Se dispondrá de sillas y sector para mantas en el césped.'
            ),
            activo=True,
        )

        # Evento 4: Feria de Emprendedores
        feria = Evento.objects.create(
            nombre='Feria de Emprendedores Locales',
            fecha=date(2026, 12, 12),
            hora=time(11, 0),
            duracion_min=360,
            capacidad_maxima=100,
            descripcion=(
                'Muestra comercial y gastronómica con más de 30 expositores de la comunidad. '
                'Música en vivo, talleres relámpago y patio de comidas.'
            ),
            activo=True,
        )

        # Evento 5: Charla de Ciberseguridad (INACTIVO)
        ciber = Evento.objects.create(
            nombre='Charla de Ciberseguridad para Familias',
            fecha=date(2026, 12, 19),
            hora=time(18, 0),
            duracion_min=75,
            capacidad_maxima=40,
            descripcion=(
                'Buenas prácticas digitales, prevención de estafas en línea y protección de datos '
                'para jóvenes y adultos mayores. Evento suspendido temporalmente.'
            ),
            activo=False,  # INACTIVO
        )

        self.stdout.write(self.style.SUCCESS('  ✓ 5 eventos creados (1 inactivo, 1 casi lleno, 1 cap 60).'))

        # 4. Creación de Reservas vigentes y canceladas
        self.stdout.write('Creando reservas y registro de asistencia...')

        # Reservas Huerto: María 3 plazas (3 asistieron), Diego 2 plazas (asistencia pendiente)
        Reserva.objects.create(
            usuario=usuario1,
            evento=huerto,
            plazas=3,
            estado=Reserva.ESTADO_VIGENTE,
            asistentes=3,
        )
        Reserva.objects.create(
            usuario=usuario2,
            evento=huerto,
            plazas=2,
            estado=Reserva.ESTADO_VIGENTE,
            asistentes=None,
        )

        # Reservas Yoga: María 5 plazas (4 asistieron), Diego 10 plazas
        Reserva.objects.create(
            usuario=usuario1,
            evento=yoga,
            plazas=5,
            estado=Reserva.ESTADO_VIGENTE,
            asistentes=4,
        )
        Reserva.objects.create(
            usuario=usuario2,
            evento=yoga,
            plazas=10,
            estado=Reserva.ESTADO_VIGENTE,
            asistentes=None,
        )

        # Reservas Cine: CASI LLENO (18 + 10 = 28 de 30 plazas reservadas, quedan 2)
        Reserva.objects.create(
            usuario=usuario1,
            evento=cine,
            plazas=18,
            estado=Reserva.ESTADO_VIGENTE,
            asistentes=None,
        )
        Reserva.objects.create(
            usuario=usuario2,
            evento=cine,
            plazas=10,
            estado=Reserva.ESTADO_VIGENTE,
            asistentes=None,
        )

        # Reservas Feria: María 6 plazas VIGENTE; Diego 4 plazas CANCELADA
        Reserva.objects.create(
            usuario=usuario1,
            evento=feria,
            plazas=6,
            estado=Reserva.ESTADO_VIGENTE,
            asistentes=None,
        )
        Reserva.objects.create(
            usuario=usuario2,
            evento=feria,
            plazas=4,
            estado=Reserva.ESTADO_CANCELADA,
            cancelada_por=admin,
            fecha_cancelacion=timezone.now(),
        )

        self.stdout.write(self.style.SUCCESS('  ✓ 8 reservas creadas con éxito (7 vigentes, 1 cancelada).'))
        self.stdout.write(self.style.SUCCESS('\n======================================================='))
        self.stdout.write(self.style.SUCCESS('✅ DATOS DE DEMOSTRACIÓN CARGADOS EXITOSAMENTE'))
        self.stdout.write(self.style.SUCCESS('======================================================='))
        self.stdout.write('Credenciales de acceso:')
        self.stdout.write('  • Administrador: admin@demo.cl   /  admin123')
        self.stdout.write('  • Usuario 1:     usuario@demo.cl /  user123')
        self.stdout.write('  • Usuario 2:     diego@demo.cl   /  user123')
        self.stdout.write('=======================================================\n')
