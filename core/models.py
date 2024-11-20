import os
import json
import qrcode
import datetime
from PIL import Image
from io import BytesIO
from datetime import date, timedelta
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.core.files import File
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User, Group, Permission
from django.dispatch import receiver
from django.db.models.signals import post_save

#modelo audiencias api
class AudienciaAPI(models.Model):
    STATUS_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Llamando', 'Llamando'),
        ('En audiencia', 'En audiencia'),
        ('Concluida', 'Concluida'),
        ('Archivada', 'Archivada'),
    ]

    expediente = models.CharField(max_length=100)
    fecha_audiencia = models.DateField(default=timezone.now)
    hora_audiencia = models.TimeField()
    sala_audiencia = models.CharField(max_length=200, null=True, blank=True)
    conciliador_audiencia = models.CharField(max_length=200, null=True, blank=True)
    auxiliar_audiencia = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audiencias_api_auxiliar')
    auxiliar_asignado_el = models.DateTimeField(null=True, blank=True)
    status_changed_at = models.DateTimeField(null=True, blank=True)
    status_audiencia = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendiente')
    _original_status = None
    hora_inicio_audiencia = models.DateTimeField(null=True, blank=True)
    hora_fin_audiencia = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Conciliador', null=True)
    auxiliar = models.CharField(max_length=100, verbose_name='Auxiliar', null=True)
    asistencia = models.BooleanField(null=True)
    atendiendo = models.BooleanField(null=True)
    mensaje = models.CharField(max_length=200, null=True)
    folio_audiencia = models.CharField(max_length=100, null=True, blank=True)
    folio_soli = models.CharField(max_length=100, null=True, blank=True)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    conciliador = models.CharField(max_length=255, null=True, blank=True)
    estatus = models.CharField(max_length=50, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = self.status_audiencia
        self._original_auxiliar = self.auxiliar_audiencia

    def save(self, *args, **kwargs):
        if self._original_status != 'Llamando' and self.status_audiencia == 'Llamando':
            # Crear la notificación si el status cambia a 'Llamando'
            NotificacionAPI.objects.create(
                audiencia=self,
                mensaje=f"El estatus de la audiencia {self.expediente} ha cambiado a {self.status_audiencia}"
            )

        # Guardar el nuevo estado
        super().save(*args, **kwargs)
        self._original_status = self.status_audiencia

    def __str__(self):
        return f'AudienciaAPI {self.expediente} - {self.fecha_audiencia}'

class NotificacionAPI(models.Model):
    audiencia = models.ForeignKey(AudienciaAPI, on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=255)
    creada_el = models.DateTimeField(auto_now_add=True)
    se_leyo = models.BooleanField(default=False)

    def __str__(self):
        return f'Notificación para {self.audiencia.expediente}'

class SolicitanteAPI(models.Model):
    audiencia = models.ForeignKey(AudienciaAPI, related_name='solicitantes', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=1000)
    asistencia = models.BooleanField(default=False)
    hora_asistencia = models.DateTimeField(verbose_name='Hora de Asistencia', null=True, blank=True)

class CitadoAPI(models.Model):
    audiencia = models.ForeignKey(AudienciaAPI, related_name='citados', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=1000)
    asistencia = models.BooleanField(default=False)
    hora_asistencia = models.DateTimeField(verbose_name='Hora de Asistencia', null=True, blank=True)


#modelo Audiencias
class Audiencia(models.Model):
    STATUS_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Llamando', 'Llamando'),
        ('En audiencia', 'En audiencia'),
        ('Concluida', 'Concluida'),
        ('Archivada', 'Archivada'),
    ]

    expediente = models.CharField(max_length=100)
    fecha_audiencia = models.DateField(default=timezone.now)
    hora_audiencia = models.TimeField()
    sala_audiencia = models.CharField(max_length=200)
    conciliador_audiencia = models.CharField(max_length=200)
    auxiliar_audiencia = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audiencias_auxiliar')
    auxiliar_asignado_el = models.DateTimeField(null=True, blank=True)
    status_audiencia = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendiente')
    _original_status = None
    status_changed_at = models.DateTimeField(null=True, blank=True)
    hora_inicio_audiencia = models.DateTimeField(null=True, blank=True)
    hora_fin_audiencia = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Conciliador', null= True)
    asistencia = models.BooleanField(null=True)
    mensaje = models.CharField(max_length=200, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = self.status_audiencia
        self._original_auxiliar = self.auxiliar_audiencia

    def save(self, *args, **kwargs):
        if self._original_status != 'Llamando' and self.status_audiencia == 'Llamando':
            # Crear la notificación si el status cambia a 'Llamando'
            Notificacion.objects.create(
                audiencia=self,
                mensaje=f"El estatus de la audiencia {self.expediente} ha cambiado a {self.status_audiencia}"
            )

        if self.pk:  # Si el objeto ya existe
            old_status = Audiencia.objects.get(pk=self.pk).status_audiencia
            if old_status != self.status_audiencia:
                self.status_changed_at = timezone.now()
        else:
            self.status_changed_at = timezone.now()

        # Guardar el nuevo estado
        super().save(*args, **kwargs)
        self._original_status = self.status_audiencia

class Notificacion(models.Model):
    audiencia = models.ForeignKey(Audiencia, on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=255)
    creada_el = models.DateTimeField(auto_now_add=True)
    se_leyo = models.BooleanField(default=False)

class justificaciones(models.Model):
    audiencia = models.ForeignKey(Audiencia, on_delete=models.CASCADE, null=True)
    mensaje = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Conciliador', null= True)
    fecha = models.DateTimeField(null=True)



class mesadeayuda(models.Model):
    expediente = models.CharField(max_length=100, null=True)
    mensaje = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Conciliador', null= True)
    fecha = models.DateTimeField(null=True)
    audiencia = models.CharField(max_length=100, null=True)
    solicitud = models.CharField(max_length=1000, null=True)
    peticion = models.CharField(max_length=1000)
    status = models.CharField(max_length=15)
    hora_inicio = models.DateTimeField(null=True)
    hora_fin = models.DateTimeField(null=True)





def identificacionFrente(instance, filename):
    nombreArchivo, extension = os.path.splitext(filename)
    nombreReemplazo = "Identificacion_Frente_"+instance.curp_rfc
    nuevoNombre = f"{nombreReemplazo}{extension}"

    return os.path.join('identificacion/', nuevoNombre)

def identificacionReverso(instance, filename):
    nombreArchivo, extension = os.path.splitext(filename)
    nombreReemplazo = "Identificacion_Reverso_"+instance.curp_rfc
    nuevoNombre = f"{nombreReemplazo}{extension}"

    return os.path.join('identificacion/', nuevoNombre)

class contadorRegistros(models.Model):
    contador = models.IntegerField(default=1)
    registro_comun = models.IntegerField(null=True, blank=True)
    

class RegistroActivo(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    registro_actual = models.CharField(max_length=100)  # El tipo de campo puede variar según tus necesidades
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Registro activo para {self.usuario.username}: {self.registro_actual}"



# ciudadano modelo
class ciudadanos(models.Model):
    nombre = models.CharField( verbose_name='Nombre Completo')
    sexo = models.CharField(max_length=10, verbose_name='Sexo', null=True)
    correo = models.EmailField(verbose_name='Correo', blank=True, null=True)
    municipio = models.CharField(max_length=255, verbose_name='Municipio')  
    curp_rfc = models.CharField(max_length=18, unique=False, verbose_name='CURP o RFC', blank=True, null=True)
    tipo_persona = models.CharField(max_length=50, null=True)
    documento_1 = models.ImageField(upload_to=identificacionFrente, blank=True, null=True)
    documento_2 = models.ImageField(upload_to=identificacionReverso, blank=True, null=True)
    codigo_ciudadano = models.CharField(max_length=30, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    registro = models.CharField(max_length=100,verbose_name='Número de Registro', null=True)
    asistencia = models.BooleanField(verbose_name='Asistencia',default=False,null=True)
    expediente = models.ForeignKey(Audiencia,verbose_name='Expediente',on_delete=models.CASCADE,null=True)
    hora_asistencia = models.DateTimeField(verbose_name='Hora de Asistencia', null=True, blank=True)

    def __str__(self):
        return f'{self.nombre} {self.sexo} {self.correo} {self.municipio} {self.curp_rfc} {self.tipo_persona} {self.documento_1} {self.documento_2} {self.codigo_ciudadano} {self.registro}'

    def save(self, *args, **kwargs):
        qr_data = f'Tipo: {self.tipo_persona}\nNombre: {self.nombre}\nCURP: {self.curp_rfc}\nSexo: {self.sexo}\nCorreo: {self.correo}\nMunicipio: {self.municipio}\nIdentificacion_Frente: {self.documento_1}\nIdentificacion_Reverso: {self.documento_2}\nCódigo Ciudadano: {self.codigo_ciudadano}\nNúmero de Registro: {self.registro}'
        qr = qrcode.make(qr_data)
        qr_io = BytesIO()
        qr.save(qr_io, 'PNG')
        qr_img = File(qr_io, name=f'{self.nombre}_{self.tipo_persona}_qr.png')
        self.qr_code = qr_img
        # Si la asistencia se marca como True y no hay hora registrada, guarda la hora actual
        if self.asistencia and self.hora_asistencia is None:
            self.hora_asistencia = timezone.now()

        super().save(*args, **kwargs)

class testigos(models.Model):
    registro = models.CharField(max_length=100,verbose_name='Número de Registro')
    codigo_ciudadano = models.TextField(verbose_name='Codigo de Ciudadano')
    curp_rfc_testigo_1 = models.CharField(max_length=18, unique=False, blank=True, null=True, verbose_name='CURP o RFC del Testigo 1')
    municipio_testigo_1 = models.CharField(max_length=255, verbose_name='Municipio del Testigo 1', blank=True, null=True)
    curp_rfc_testigo_2 = models.CharField(max_length=18, unique=False, blank=True, null=True, verbose_name='CURP o RFC del Testigo 2')
    municipio_testigo_2 = models.CharField(max_length=255, verbose_name='Municipio del Testigo 2', blank=True, null=True)
    curp_rfc_ciudadano = models.CharField(max_length=18, unique=False, blank=True, null=True, verbose_name='CURP o RFC del Ciudadano 2')
    documento_3 = models.ImageField(upload_to='testigos/', blank=True, null=True)
    documento_4 = models.ImageField(upload_to='testigos/', blank=True, null=True)
    documento_5 = models.ImageField(upload_to='testigos/', blank=True, null=True)
    documento_6 = models.ImageField(upload_to='testigos/', blank=True, null=True)

    def __str__(self):
        return f'{self.registro} {self.codigo_ciudadano} {self.curp_rfc_testigo_1}  {self.municipio_testigo_1} {self.curp_rfc_testigo_2} {self.municipio_testigo_2} {self.curp_rfc_ciudadano} {self.documento_3} {self.documento_4} {self.documento_5} {self.documento_6}'
    
    class Meta:
        verbose_name = 'Testigo'
        verbose_name_plural = 'Testigos'
        
class fuentesdetrabajo(models.Model):
    razon_social = models.CharField(max_length=100, unique=True,verbose_name='Número de Registro')


    def __str__(self):
        return f'{self.razon_social} {self.nombre_comercial}'
    
    class Meta:
        verbose_name = 'Fuentedetrabajo'
        verbose_name_plural = 'Fuentesdetrabajo'

# turno modelo
class turnos(models.Model):
    RATIFICACION = 1
    CONCILIACION = 2
    ASESORIA_JURIDICA = 3
    PROCURADURIA = 4
    PAGOS = 5
    OTRA = 6
    
    AREA_CHOICES = [
        (RATIFICACION, 'Ratificación'),
        #(CONCILIACION, 'Conciliación'),
        (ASESORIA_JURIDICA, 'Asesoría jurídica'),
        #(PROCURADURIA, 'Procuraduría'),
        #(PAGOS, 'Pagos'),
        #(OTRA, 'Otra'),
    ]
    preferente = models.BooleanField(verbose_name='Turno', default=False)
    area = models.IntegerField(choices=AREA_CHOICES, verbose_name='Área asignada')
    turno = models.CharField(max_length=30, verbose_name='Turno')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario', null= True, blank=True)
    mesa = models.CharField(max_length=30,verbose_name='Mesa asignada', blank=True, null=True)
    fecha= models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora de creacion del turno')
    registro = models.CharField(max_length=100, verbose_name='Número de Registro')
    codigo_ciudadano = models.TextField(verbose_name='Codigo de Ciudadano')
    notificacion = models.BooleanField(default=False, verbose_name='Notificación')
    hora_notificacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora de la notificacion',null=True)
    status_choices = [
        ('PEN', 'Pendiente'),
        ('PRO', 'Proceso'),
        ('FIN', 'Finalizado'),
        ('CAN', 'Cancelado'),
    ]
    status = models.CharField(max_length=3, choices=status_choices, default='PEN', verbose_name='Estatus')
    hora_inicio_turno = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora del inicio de la asesoria',null=True)
    hora_fin_turno = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora del fin de la asesoria',null=True)
    estado_revisado = models.BooleanField(default=False, blank=True, null=True)
    
    def __str__(self):
        return f"ID de Cita: {self.id}"  
    
class contadorTurnos(models.Model):
    prefijo = models.CharField(max_length=10, unique=True)
    numero = models.PositiveIntegerField(default=0)
    fecha = models.DateField(auto_now_add=True)

class area(models.Model):
    RATIFICACION = 1
    CONCILIACION = 2
    ASESORIA_JURIDICA = 3
    PROCURADURIA = 4
    PAGOS = 5
    
    AREA_CHOICES = [
        (RATIFICACION, 'Ratificación'),
        (CONCILIACION, 'Conciliación'),
        (ASESORIA_JURIDICA, 'Asesoría jurídica'),
        (PROCURADURIA, 'Procuraduría'),
        (PAGOS, 'Pagos'),
    ]
    area = models.IntegerField(choices=AREA_CHOICES, verbose_name='Área asignada')

    def __str__(self):
        return self.get_area_display()  

    class Meta:
        verbose_name = 'Area'
        verbose_name_plural = 'Areas'

class mesa(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario', null=True)
    mesa = models.CharField(max_length=50,verbose_name='Mesa')
    RATIFICACION = 1
    CONCILIACION = 2
    ASESORIA_JURIDICA = 3
    PROCURADURIA = 4
    PAGOS = 5

    AREA_CHOICES = [
        (RATIFICACION, 'Ratificación'),
        (CONCILIACION, 'Conciliación'),
        (ASESORIA_JURIDICA, 'Asesoría jurídica'),
        (PROCURADURIA, 'Procuraduría'),
        (PAGOS, 'Pagos'),
    ]
    
    area = models.IntegerField(choices=AREA_CHOICES, verbose_name='Área asignada')
    def __str__(self):
        return f'{self.area} - {self.user} - {self.mesa}'

    class Meta:
        verbose_name ='Mesa'
        verbose_name_plural = 'Mesas'   

class sala(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario')
    sala = models.IntegerField(verbose_name='Sala')

    RATIFICACION = 1
    CONCILIACION = 2
    ASESORIA_JURIDICA = 3
    PROCURADURIA = 4
    PAGOS = 5

    AREA_CHOICES = [
        (RATIFICACION, 'Ratificación'),
        (CONCILIACION, 'Conciliación'),
        (ASESORIA_JURIDICA, 'Asesoría jurídica'),
        (PROCURADURIA, 'Procuraduría'),
        (PAGOS, 'Pagos'),
    ]

    area = models.IntegerField(choices=AREA_CHOICES, verbose_name='Área')
    def __str__(self):
        return f'{self.area} - {self.user} - {self.sala}'

def get_current_time():
    return datetime.datetime.now().time()    

class operacionArea(models.Model):
    operacion_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario') 
    idCiudadano = models.ForeignKey (ciudadanos, on_delete=models.CASCADE, verbose_name='Ciudadano', null=True)
    turno_id = models.ForeignKey (turnos, on_delete=models.CASCADE, verbose_name='Turno')
    observaciones = models.CharField(max_length=100, verbose_name='Observaciones', null=True)
    documentacion = models.FileField(blank=True, null=True)
    opciones = [
        ('Concluido', 'Concluido'),
        ('Otra Area', 'Se va a otra area'),
        ('No Inicio Solicitud', 'No inicio solicitud'),
    ]
    finalizacion = models.CharField(max_length=20, choices=opciones, verbose_name='Finalización', null=True)
    hora_entrada = models.TimeField(default=get_current_time, null=True)
    hora_salida = models.TimeField(default=get_current_time, null=True)
    cita_id = models.IntegerField(null=True)
    mesa_id = models.IntegerField(null=True)
    area_id = models.IntegerField(null=True)
    folio_sinacol = models.CharField(max_length=255, null=True)

    class Meta:
        abstract = True


class AyudaAsesor(models.Model):
    mesa = models.ForeignKey(mesa, on_delete=models.CASCADE,  null=True)
    asesor =  models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Asesores')
    mensaje = models.CharField(max_length=100, null=True)
    atendiendo = models.BooleanField(null=True)
    activo = models.BooleanField(null=True)
    auxiliar = models.CharField(max_length=50, null=True) 
    fecha = models.DateField(null=True)
    hora = models.TimeField(null=True)
    


class asesoriaJuridica(operacionArea):
    mesa = models.ForeignKey(mesa, on_delete=models.CASCADE, null=True)
    cantidadPersonas = models.IntegerField(verbose_name='Cantidad de Personas', null=True)
    personasFinal = models.IntegerField(verbose_name='Personas Final', null=True)
    empresa = models.CharField(max_length=200, verbose_name='razon social', null=True)
    registro = models.CharField(max_length=100,verbose_name='registro', null=False)
    

    def __str__(self):
        return f'{self.mesa} - {self.cantidadPersonas} {self.personasFinal} {self.empresa} {self.registro}'

    class Meta:
        verbose_name ='Asesoria Juridica'
        verbose_name_plural = 'Asesorias Juridicas'  


class conclusion(models.Model):
    id_ciudadano = models.ForeignKey(ciudadanos, on_delete=models.CASCADE, verbose_name='Ciudadano')
    id_asesoria =models.ForeignKey(asesoriaJuridica,on_delete=models.CASCADE,verbose_name='Asesoria ID')
    conclusion_exitosa = models.CharField(max_length=20,verbose_name='Conclusion')

    def __str__(self):
        return f'{self.id_ciudadano} - {self.id_asesoria}'

    class Meta:
        verbose_name ='Conclusion Exitosa'
        verbose_name_plural = 'Conclusiones Exitosas'  
        verbose_name_plural = 'Conclusiones Exitosas'


class pagos(operacionArea):
    mesa = models.CharField(max_length=255)
    empleador = models.CharField(max_length=255)
    empleado = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.turno_id} - {self.idCiudadano}'

    class Meta:
        verbose_name ='Pagos'
        verbose_name_plural = 'Pagos'

class conciliacion(operacionArea):
    sala = models.CharField(max_length=255)
    expediente = models.CharField(max_length=100, verbose_name='Expediente')
    cantidadPersonas = models.IntegerField(verbose_name='Cantidad de Personas')
    personasFinal = models.IntegerField(verbose_name='Personas Final')

    def __str__(self):
        return f'{self.turno_id} - {self.idCiudadano}'

    class Meta:
        verbose_name ='Conciliacion'
        verbose_name_plural = 'Conciliaciones'

class procuraduria(operacionArea):
    mesa = models.CharField(max_length=255)
    cantidadPersonas = models.IntegerField(verbose_name='Cantidad de Personas')
    personasFinal = models.IntegerField(verbose_name='Personas Final')
    def __str__(self):
        return f'{self.turno_id} - {self.idCiudadano}'

    class Meta:
        verbose_name ='Procuraduria'
        verbose_name_plural = 'Procuraduria'  

class ratificacion(operacionArea):
    folio_sinacol_solicitud = models.CharField(max_length=255, null=True)
    folio_sinacol_expediente = models.CharField(max_length=255, null=True)
    mesa = models.ForeignKey(mesa, on_delete=models.CASCADE, verbose_name='Mesa', null=True)
    cantidadPersonas = models.IntegerField(verbose_name='Cantidad de Personas', null=True)
    personasFinal = models.IntegerField(verbose_name='Personas Final', null=True)
    empresa = models.CharField(max_length=200, verbose_name='razon social', null=True)
    registro = models.CharField(max_length=100,verbose_name='registro', null=False)
    

    def __str__(self):
        return f'{self.mesa} - {self.cantidadPersonas} {self.personasFinal} {self.empresa} {self.registro}'

    class Meta:
        verbose_name ='Ratificacion'
        verbose_name_plural = 'Ratificaciones'


class conclusionratificaciones(models.Model):
    id_ciudadano = models.ForeignKey(ciudadanos, on_delete=models.CASCADE, verbose_name='Ciudadano')
    id_ratificacion =models.ForeignKey(ratificacion,on_delete=models.CASCADE,verbose_name='Ratificacion ID')
    conclusion = models.CharField(max_length=20,verbose_name='Conclusion')

    def __str__(self):
        return f'{self.id_ciudadano} - {self.id_ratificacion}'

    class Meta:
        verbose_name ='Conclusion'
        verbose_name_plural = 'Conclusiones'  
        verbose_name_plural = 'Conclusiones'


class proveedor(models.Model):
    empresa = models.DateField(verbose_name='Nombre de la Empresa')
    DIRECCION_GENERAL = 1
    DIRECCION_TECNOLOGIAS = 2
    DIRECCION_DESARROLLO = 3
    DIRECCION_ADMINISTRACION = 4
    COORDINACION_RH = 5
    COORDINACION_FINANZAS = 6
    
    AREAS = [
        (DIRECCION_GENERAL, 'Dirección General'),
        (DIRECCION_TECNOLOGIAS, 'Dirección de Tecnologías'),
        (DIRECCION_DESARROLLO, 'Dirección de Desarrollo Institucional'),
        (DIRECCION_ADMINISTRACION, 'Dirección de Administración'),
        (COORDINACION_RH, 'Coordinación de Recursos Humanos'),
        (COORDINACION_FINANZAS, 'Coordinación de Finanzas'),
    ]
    area = models.IntegerField(choices=AREAS, verbose_name='Area a la que se Dirige')
    trabajadorCCL = models.CharField(max_length=100, verbose_name='Nombre del Trabajador del CCL con Quien Va')
    idCiudadano = models.CharField(max_length=200, verbose_name='Ciudadano')

    def __str__(self):
        return f'{self.empresa} - {self.trabajadorCCL} {self.area} {self.idCiudadano} '

    class Meta:
        verbose_name ='Proveedor'
        verbose_name_plural = 'Proveedores'     

class administrativo(models.Model):
    DIRECCION_GENERAL = 1
    DIRECCION_TECNOLOGIAS = 2
    DIRECCION_DESARROLLO = 3
    DIRECCION_ADMINISTRACION = 4
    COORDINACION_RH = 5
    COORDINACION_FINANZAS = 6
    
    AREAS = [
        (DIRECCION_GENERAL, 'Dirección General'),
        (DIRECCION_TECNOLOGIAS, 'Dirección de Tecnologías'),
        (DIRECCION_DESARROLLO, 'Dirección de Desarrollo Institucional'),
        (DIRECCION_ADMINISTRACION, 'Dirección de Administración'),
        (COORDINACION_RH, 'Coordinación de Recursos Humanos'),
        (COORDINACION_FINANZAS, 'Coordinación de Finanzas'),
    ]
    area = models.IntegerField(choices=AREAS, verbose_name='Area a la que se Dirige')
    idCiudadano = models.CharField(max_length=200, verbose_name='Ciudadano')

    def __str__(self):
        return f'{self.area} - {self.idCiudadano}'

    class Meta:
        verbose_name ='Administrativo'
        verbose_name_plural = 'Administrativos' 

class asignacion(models.Model):
    encargado = models.CharField(max_length=100, verbose_name='Encargado')
    area = models.ForeignKey (area, on_delete=models.CASCADE, verbose_name='Area')
    status = models.ForeignKey (turnos, on_delete=models.CASCADE, verbose_name='Status') 

    def __str__(self):
        return f'{self.encargado} - {self.area} {self.status}'

    class Meta:
        verbose_name ='Asignacion'
        verbose_name_plural = 'Asignaciones'
        
class Documentos(models.Model):
    empleador_id = models.URLField(blank=True, null=True)
    empleador_actac = models.URLField(blank=True, null=True)
    empleador_actar = models.URLField(blank=True, null=True)
    empleador_csf = models.URLField(blank=True, null=True)
    
    trabajador_id = models.URLField(blank=True, null=True)
    trabajador_curp = models.URLField(blank=True, null=True)
    trabajador_comprobante = models.URLField(blank=True, null=True) 
    
class trabajadora(models.Model):
    comprobantePago = models.FileField(upload_to='comprobantePago/', blank=True, verbose_name='Comprobante de Pago')
    conceptoPagar = models.FileField(upload_to='conceptoPagar/', blank=True, verbose_name='Concepto a Pagar')
    folioSinacol = models.CharField(max_length=100, blank=True, verbose_name='Folio de Sinacol')
    solicitudSinacol = models.FileField(upload_to='solicitudSinacol/', blank=True, verbose_name='Solicitud de Sinacol') 
    idCiudadano = models.ForeignKey (ciudadanos, on_delete=models.CASCADE, verbose_name='Ciudadano')
    def __str__(self):
        return f'{self.comprobantePago}, {self.conceptoPagar}, {self.folioSinacol}, {self.solicitudSinacol}'
    
class empleadoraFisica(models.Model):
    constanciaSF = models.FileField(upload_to='CSFEmpleadorFisico/', blank=True, verbose_name='Comprobante de Pago')
    actaConstitutiva = models.FileField(upload_to='actaConstitutivaEmpleadorFisico/', blank=True, verbose_name='Concepto a Pagar')
    actaRepresentacion = models.FileField(upload_to='actaRepresentacionEmpleadorFisico/', blank=True, verbose_name='Folio de Sinacol')
    solicitudSinacol = models.FileField(upload_to='solicitudSinacolEmpleadorFisico/', blank=True, verbose_name='Solicitud de Sinacol')
    idCiudadano = models.ForeignKey (ciudadanos, on_delete=models.CASCADE, verbose_name='Ciudadano')
    def __str__(self):
        return f'{self.constanciaSF}, {self.actaConstitutiva}, {self.actaRepresentacion}, {self.solicitudSinacol}'
    
class empleadoraJuridica(models.Model):
    constanciaSF = models.FileField(upload_to='CSFEmpleadorJuridico/', blank=True, verbose_name='Comprobante de Pago')
    actaConstitutiva = models.FileField(upload_to='actaConstitutivaEmpleadorJuridico/', blank=True, verbose_name='Concepto a Pagar')
    actaRepresentacion = models.FileField(upload_to='actaRepresentacionEmpleadorJuridico/', blank=True, verbose_name='Folio de Sinacol')
    solicitudSinacol = models.FileField(upload_to='solicitudSinacolEmpleadorJuridico/', blank=True, verbose_name='Solicitud de Sinacol')
    idCiudadano = models.ForeignKey (ciudadanos, on_delete=models.CASCADE, verbose_name='Ciudadano')
    def __str__(self):
        return f'{self.constanciaSF}, {self.actaConstitutiva}, {self.actaRepresentacion}, {self.solicitudSinacol}'

class recepcion(models.Model):
    cita = models.CharField(max_length=100, verbose_name='Cita')
    cantidadPersonas = models.IntegerField(verbose_name='Cantidad de Personas')
    area = models.ForeignKey (area, on_delete=models.CASCADE, verbose_name='Area')
    fechaEntrada = models.DateTimeField(auto_now_add=True, verbose_name='Fecha Entrada')
    fechaSalida = models.DateTimeField(auto_now_add=True, verbose_name='Fecha Salida')
    idCiudadano = models.ForeignKey (ciudadanos, on_delete=models.CASCADE, verbose_name='Ciudadano')
    turno_id = models.ForeignKey (turnos, on_delete=models.CASCADE, verbose_name='Turno')
    def __str__(self):
        return f'{self.cantidadPersonas} {self.area} {self.fechaEntrada} {self.fechaSalida} {self.idCiudadano}'

    class Meta:
        verbose_name ='Recepción'
        verbose_name_plural = 'Recepción'
    
class CodificaciónCaraDeUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='face_encoding')
    encoding = models.BinaryField(null=True, blank=True)

    def __str__(self):
        return f"Cara de {self.user.username}, codificada"
    
"""class Estadisticas(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuario')
    turnos_atendidos = models.IntegerField(default=0, verbose_name='Cantidad de turnos atendidos')
    turnos_cancelados = models.IntegerField(default=0, verbose_name='Cantidad de turnos cancelados')
    promedio_turnos_atendidos = models.FloatField(default=0.0, verbose_name='Promedio de turnos atendidos')
    promedio_turnos_cancelados = models.FloatField(default=0.0, verbose_name='Promedio de turnos cancelados')
    pagos_realizados = models.IntegerField(default=0, verbose_name='Cantidad de pagos realizados')
    pagos_no_realizados = models.IntegerField(default=0, verbose_name='Cantidad de pagos no realizados por incomparecencia')
    pagos_por_dia = models.IntegerField(default=0, verbose_name='Cantidad de pagos por día')
    promedio_pagos_realizados = models.FloatField(default=0.0, verbose_name='Promedio de pagos realizados')
    promedio_pagos_no_realizados = models.FloatField(default=0.0, verbose_name='Promedio de pagos no realizados')
    solicitudes_confirmadas = models.IntegerField(default=0, verbose_name='Solicitudes confirmadas')
    solicitudes_no_confirmadas = models.IntegerField(default=0, verbose_name='Solicitudes no confirmadas')
    solicitudes_por_dia = models.IntegerField(default=0, verbose_name='Solicitudes por día')
    promedio_solicitudes_confirmadas = models.FloatField(default=0.0, verbose_name='Promedio de solicitudes confirmadas')
    promedio_solicitudes_no_confirmadas = models.FloatField(default=0.0, verbose_name='Promedio de solicitudes no confirmadas')
    conciliaciones_exitosas = models.IntegerField(default=0, verbose_name='Conciliaciones exitosas')
    conciliaciones_fallidas = models.IntegerField(default=0, verbose_name='Conciliaciones fallidas')
    conciliaciones_por_dia = models.IntegerField(default=0, verbose_name='Conciliaciones por día')
    promedio_conciliaciones_exitosas = models.FloatField(default=0.0, verbose_name='Promedio de conciliaciones exitosas')
    promedio_conciliaciones_fallidas = models.FloatField(default=0.0, verbose_name='Promedio de conciliaciones fallidas')
    audiencias_concluidas = models.IntegerField(default=0, verbose_name='Audiencias concluidas')
    audiencias_archivadas = models.IntegerField(default=0, verbose_name='Audiencias archivadas')
    audiencias_por_dia = models.IntegerField(default=0, verbose_name='Audiencias por día')
    promedio_audiencias_concluidas = models.FloatField(default=0.0, verbose_name='Promedio de audiencias concluidas')
    promedio_audiencias_archivadas = models.FloatField(default=0.0, verbose_name='Promedio de audiencias archivadas')
    tiempo_atencion_total = models.DurationField(default=timedelta(), verbose_name='Tiempo total de atención')
    turnos_en_proceso = models.BooleanField(default=False, verbose_name='Turno en proceso')
    fecha = models.DateField(auto_now_add=True, verbose_name='Fecha de estadística')

    def actualizar_promedios(self):
        total_turnos = self.turnos_atendidos + self.turnos_cancelados
        if total_turnos > 0:
            self.promedio_turnos_atendidos = (self.turnos_atendidos / total_turnos) * 100
            self.promedio_turnos_cancelados = (self.turnos_cancelados / total_turnos) * 100
        else:
            self.promedio_turnos_atendidos = 0
            self.promedio_turnos_cancelados = 0

        total_pagos = self.pagos_realizados + self.pagos_no_realizados
        if total_pagos > 0:
            self.promedio_pagos_realizados = (self.pagos_realizados / total_pagos) * 100
            self.promedio_pagos_no_realizados = (self.pagos_no_realizados / total_pagos) * 100
        else:
            self.promedio_pagos_realizados = 0
            self.promedio_pagos_no_realizados = 0

        total_solicitudes = self.solicitudes_confirmadas + self.solicitudes_no_confirmadas
        if total_solicitudes > 0:
            self.promedio_solicitudes_confirmadas = (self.solicitudes_confirmadas / total_solicitudes) * 100
            self.promedio_solicitudes_no_confirmadas = (self.solicitudes_no_confirmadas / total_solicitudes) * 100
        else:
            self.promedio_solicitudes_confirmadas = 0
            self.promedio_solicitudes_no_confirmadas = 0

        total_audiencias = self.audiencias_concluidas + self.audiencias_archivadas
        if total_audiencias > 0:
            self.promedio_audiencias_concluidas = (self.audiencias_concluidas / total_audiencias) * 100
            self.promedio_audiencias_archivadas = (self.audiencias_archivadas / total_audiencias) * 100
        else:
            self.promedio_audiencias_concluidas = 0
            self.promedio_audiencias_archivadas = 0

        self.save()
    
    def __str__(self):
        return f'Estadísticas de {self.user}'

@receiver(post_save, sender=User)
def create_user_estadisticas(sender, instance, created, **kwargs):
    if created:
        Estadisticas.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_estadisticas(sender, instance, **kwargs):
    instance.estadisticas.save()"""


#####################  EWH #######################################
class Solicitud(models.Model):
    folio_solicitud = models.CharField(max_length=100)
    id_ciudadano = models.IntegerField()
    asistencia = models.BooleanField(default=False, blank=True, null=True)
    registro = models.CharField(max_length=100,verbose_name='Número de Registro', null=True)

    def __str__(self):
        return f"Solicitud {self.folio_solicitud} ({self.id_ciudadano}) asistencia ({self.asistencia})"
    

class conciliadorbloquedo(models.Model):
    conciliador = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    bloqueo = models.BooleanField(null=True)