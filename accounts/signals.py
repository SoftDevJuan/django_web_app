from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Profile

@receiver(post_save, sender=Profile)
def agregar_empleados(sender, instance, created, **kwargs):
    if created:
        try:
            grupo1 = Group.objects.get(name='Autorizacion-Pendiente')
        except Group.DoesNotExist:
            grupo1 = Group.objects.create(name='Autorizacion-Pendiente')
            grupo2 = Group.objects.create(name='Recepcion')
            grupo3 = Group.objects.create(name='Asesoria-Juridica')
            grupo4 = Group.objects.create(name='Ratificacion')
            grupo5 = Group.objects.create(name='Conciliacion')
            grupo6 = Group.objects.create(name='Pagos')
            grupo7 = Group.objects.create(name='Pantalla')
            grupo8 = Group.objects.create(name='Proveedores')
            grupo9 = Group.objects.create(name='Administrativos')
            grupo10 = Group.objects.create(name='Procuraduria')
            grupo10 = Group.objects.create(name='Comunicacion')
            grupo11 = Group.objects.create(name='Administrador')
            grupo12 = Group.objects.create(name='Auxiliar-Asistencias')
            grupo13 = Group.objects.create(name='Auxiliar-Coordinador')
            grupo14 = Group.objects.create(name='Coordinador')
        instance.user.groups.add(grupo1)