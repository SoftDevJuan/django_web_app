from django.contrib import admin
from . models import *
class CiudadanoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'sexo', 'correo', 'municipio', 'curp_rfc', 'tipo_persona', 'documento_1', 'documento_2','codigo_ciudadano', 'qr_code')
    search_fields = ('nombre', 'codigo_ciudadano', 'correo', 'tipo_persona')
    list_filter = ('nombre', 'sexo', 'correo', 'municipio',  'curp_rfc', 'tipo_persona', 'documento_1', 'documento_2','codigo_ciudadano', 'qr_code')
admin.site.register(ciudadanos ,CiudadanoAdmin)

class turnosAdmin(admin.ModelAdmin):
    list_display = ('area', 'turno', 'usuario','mesa', 'fecha', 'status','registro', 'codigo_ciudadano')
    #search_fields = ( 'area',)
    search_fields = ( 'turno','usuario')
    #search_fields = ( 'status',)
    list_filter = ('area', 'turno', 'mesa', 'fecha', 'status', 'usuario')
admin.site.register(turnos, turnosAdmin)

class areaAdmin(admin.ModelAdmin):
    list_display = ('area',)
    list_filter = ('area',)
admin.site.register(area, areaAdmin)

class mesaAdmin(admin.ModelAdmin):
    list_display = ('user', 'mesa')
    list_filter = ('user', 'mesa')
admin.site.register(mesa, mesaAdmin)


class asesoriaJuridicaAdmin(admin.ModelAdmin):
    list_display = ('user', 'mesa',  'cantidadPersonas', 'finalizacion', 'personasFinal', 'observaciones',  'turno_id', 'idCiudadano')
    list_filter = ('user', 'mesa',  'cantidadPersonas', 'finalizacion', 'personasFinal', 'observaciones',  'turno_id', 'idCiudadano')
admin.site.register(asesoriaJuridica, asesoriaJuridicaAdmin)

class pagosAdmin(admin.ModelAdmin):
    list_display = ('mesa', 'empleador', 'empleado', 'turno_id', 'idCiudadano')
    list_filter = ('mesa', 'empleador', 'empleado', 'turno_id', 'idCiudadano')
admin.site.register(pagos, pagosAdmin)

class conciliacionAdmin(admin.ModelAdmin):
    list_display = ('user', 'sala',  'expediente', 'cantidadPersonas', 'finalizacion', 'personasFinal', 'observaciones',  'turno_id', 'idCiudadano')
    list_filter = ('user', 'sala',  'expediente', 'cantidadPersonas', 'finalizacion', 'personasFinal', 'observaciones',  'turno_id', 'idCiudadano')
admin.site.register(conciliacion, conciliacionAdmin)

class procuraduriaAdmin(admin.ModelAdmin):
    list_display = ('user', 'mesa',  'cantidadPersonas', 'finalizacion', 'personasFinal', 'observaciones',  'turno_id', 'idCiudadano')
    list_filter = ('user', 'mesa',  'cantidadPersonas', 'finalizacion', 'personasFinal', 'observaciones',  'turno_id', 'idCiudadano')
admin.site.register(procuraduria, procuraduriaAdmin)

class ratificacionAdmin(admin.ModelAdmin):
    list_display = ('user', 'mesa',  'cantidadPersonas', 'finalizacion', 'personasFinal', 'observaciones',  'turno_id', 'idCiudadano')   
    list_filter = ('user', 'mesa',  'cantidadPersonas', 'finalizacion', 'personasFinal', 'observaciones',  'turno_id', 'idCiudadano')
admin.site.register(ratificacion, ratificacionAdmin)

class proveedorAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'trabajadorCCL', 'area', 'idCiudadano')
    list_filter = ('empresa', 'trabajadorCCL', 'area', 'idCiudadano')
admin.site.register(proveedor, proveedorAdmin)

class administrativoAdmin(admin.ModelAdmin):
    list_display = ('area', 'idCiudadano')
    list_filter = ('area', 'idCiudadano')
admin.site.register(administrativo, administrativoAdmin)

class asignacionAdmin(admin.ModelAdmin):
    list_display = ('encargado', 'area', 'status')
    list_filter = ('encargado', 'area', 'status')
admin.site.register(asignacion, asignacionAdmin)

class trabajadoraAdmin(admin.ModelAdmin):
    list_display = ('comprobantePago', 'conceptoPagar', 'folioSinacol', 'solicitudSinacol', 'idCiudadano')
    list_filter = ('comprobantePago', 'conceptoPagar', 'folioSinacol', 'solicitudSinacol', 'idCiudadano')
admin.site.register(trabajadora, trabajadoraAdmin)

class empleadoraFisicaAdmin(admin.ModelAdmin):
    list_display = ('constanciaSF', 'actaConstitutiva', 'actaRepresentacion', 'solicitudSinacol', 'idCiudadano')
    list_filter = ('constanciaSF', 'actaConstitutiva', 'actaRepresentacion', 'solicitudSinacol', 'idCiudadano')
admin.site.register(empleadoraFisica, empleadoraFisicaAdmin)

class empleadoraJuridicaAdmin(admin.ModelAdmin):
    list_display = ('constanciaSF', 'actaConstitutiva', 'actaRepresentacion', 'solicitudSinacol', 'idCiudadano')
    list_filter = ('constanciaSF', 'actaConstitutiva', 'actaRepresentacion', 'solicitudSinacol', 'idCiudadano')
admin.site.register(empleadoraJuridica, empleadoraJuridicaAdmin)

class recepcionAdmin(admin.ModelAdmin):
    list_display = ('cita', 'cantidadPersonas', 'area', 'idCiudadano', 'turno_id')
    list_filter = ('cita', 'cantidadPersonas', 'area', 'idCiudadano', 'turno_id')
admin.site.register(recepcion, recepcionAdmin)

class solicitudAdmin(admin.ModelAdmin):
    list_display = ('folio_solicitud', 'id_ciudadano', 'asistencia')
    list_filter = ('folio_solicitud', 'id_ciudadano', 'asistencia')
admin.site.register(Solicitud, solicitudAdmin)
class AudienciaAdmin(admin.ModelAdmin):
    list_display = ('expediente', 'fecha_audiencia', 'hora_audiencia', 'sala_audiencia', 'conciliador_audiencia', 'status_audiencia')
    list_filter = ('status_audiencia', 'fecha_audiencia', 'sala_audiencia')
    search_fields = ('expediente', 'conciliador_audiencia')

admin.site.register(Audiencia, AudienciaAdmin)

class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('audiencia', 'mensaje', 'creada_el', 'se_leyo')
    list_filter = ('creada_el', 'se_leyo')
    search_fields = ('audiencia', 'mensaje')
admin.site.register(Notificacion, NotificacionAdmin)

"""class EstadisticasAdmin(admin.ModelAdmin):
    list_display = ('user', 'turnos_atendidos', 'turnos_cancelados')
    list_filter = ('user', 'turnos_atendidos', 'turnos_cancelados')
admin.site.register(Estadisticas, EstadisticasAdmin)"""

#Admin de Audiencias y sus relacionados api
class SolicitanteAPIInline(admin.TabularInline):
    model = SolicitanteAPI
    fields = ['nombre']
    extra = 1

class CitadoAPIInline(admin.TabularInline):
    model = CitadoAPI
    fields = ['nombre']
    extra = 1

@admin.register(AudienciaAPI)
class AudienciaAPIAdmin(admin.ModelAdmin):
    list_display = ('expediente', 'fecha_audiencia', 'status_audiencia', 'conciliador_audiencia', 'get_solicitantes', 'get_citados')
    list_filter = ('status_audiencia', 'fecha_audiencia')
    search_fields = ('expediente', 'conciliador_audiencia')
    inlines = [SolicitanteAPIInline, CitadoAPIInline]

    def get_solicitantes(self, obj):
        return ", ".join([solicitante.nombre for solicitante in obj.solicitantes.all()])
    get_solicitantes.short_description = 'Solicitantes'

    def get_citados(self, obj):
        return ", ".join([citado.nombre for citado in obj.citados.all()])
    get_citados.short_description = 'Citados'

@admin.register(NotificacionAPI)
class NotificacionAPIAdmin(admin.ModelAdmin):
    list_display = ('audiencia', 'mensaje', 'creada_el', 'se_leyo')
    list_filter = ('se_leyo', 'creada_el')
    search_fields = ('audiencia__expediente', 'mensaje')
