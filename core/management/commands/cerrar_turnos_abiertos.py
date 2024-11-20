from django.core.management.base import BaseCommand
from django.utils import timezone
from models import EstadisticasUsuario

class Command(BaseCommand):
    help = 'Cierra automáticamente los turnos que hayan quedado abiertos'

    def handle(self, *args, **options):
        hora_limite = timezone.now() - timezone.timedelta(hours=4)
        turnos_abiertos = EstadisticasUsuario.objects.filter(
            inicio_turno_actual__lt=hora_limite,
            fin_turno_actual__isnull=True
        )

        for estadistica in turnos_abiertos:
            estadistica.fin_turno_actual = estadistica.inicio_turno_actual + timezone.timedelta(hours=4)
            duracion_turno = estadistica.fin_turno_actual - estadistica.inicio_turno_actual
            estadistica.tiempo_total += duracion_turno
            estadistica.turnos_atendidos += 1
            estadistica.inicio_turno_actual = None
            estadistica.fin_turno_actual = None
            estadistica.save()

        self.stdout.write(self.style.SUCCESS(f'Se cerraron {turnos_abiertos.count()} turnos abiertos'))