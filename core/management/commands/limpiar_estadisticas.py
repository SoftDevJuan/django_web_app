from django.core.management.base import BaseCommand
from django.utils import timezone
from models import EstadisticasUsuario

class Command(BaseCommand):
    help = 'Elimina las estadísticas de usuarios con más de una semana de antigüedad'

    def handle(self, *args, **options):
        una_semana_atras = timezone.now() - timezone.timedelta(days=7)
        EstadisticasUsuario.objects.filter(fecha_inicio__lt=una_semana_atras).delete()
        self.stdout.write(self.style.SUCCESS('Estadísticas antiguas eliminadas con éxito'))