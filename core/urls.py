
from core import views
from .views import *
from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', RedirectView.as_view(url='inicio/')),
    path('admin/', admin.site.urls, name='admin'),
    path('admin/', admin.site.urls, name='admin'),
    path('inicio/', VistaInicio.as_view(), name = 'Inicio'),
    path('Registrar_con_IA/', recepcion_registro_ia.as_view(), name = 'Registrar con IA'),
    path('generar_token/', generar_token, name = 'generar_token'),
    path('Registrar_con_QR/', RegistroConQR.as_view(), name = 'Registrar con QR'),
    path('registrar_ciudadano_QR/', views.registrar_ciudadano_QR, name='registrar_ciudadano_QR'),
    path('registro/', views.registro, name = 'Registro'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('inicioAsesoria/', VistaInicioAsesoria.as_view(), name = 'Inicio Asesoria'),
    path('registroManual/', VistaRegistroManual.as_view(), name = 'Registro Manual'),
    #path('registroTestigo/', VistaRegistroTestigo.as_view(), name = 'Registro Testigo'),
    path('registro/ratificaciones/folio/', registroRatiEWH.as_view(), name = 'Registro Ratificaciones'),
    path('registro/ratificaciones/folio/insertar_ciudadanos/', insertar_ciudadanos, name='insertar_ciudadanos'),
    path('registro/ratificaciones/folio/buscar_folio_anio/', buscar_folio_anio, name='buscar_folio_anio'),
    path('registro/ratificaciones/folio/api', dataRati, name = 'Ratificacion con folio api'),
    path('registro/ratificaciones/folio/asistencia', update_attendance, name = 'Asistencia Ratificacion con folio'),
    path('registro/ratificaciones/folio/asistencia_testigos', update_attendance_testigos, name = 'Asistencia Ratificacion testigos con folio'),
    path('buscar_ciudadano_autocompletar/', views.buscar_ciudadano_autocompletar, name = 'buscar ciudadano autocompletar'),

    path('Mantenimiento/', views.VistaMantenimiento.as_view(), name='Vista Mantenimiento'),
    path('pruebaauthcitas/', views.consumoApi, name='pruebaauthcitas'),
    path('turneroPagos/', views.VistaTurneroPagos.as_view(), name ='Vista Turnero Pagos'),
    path('recepcion/', views.VistaRecepcion.as_view(), name='Recepcion'),
    path('buscar_datos_ciudadano/', views.buscar_datos_ciudadano, name='Buscar Datos Ciudadano'),

    path('administrador/', VistaAdministrador.as_view(), name = 'Administrador'),
    path('autorizacionPendiente/', VistaAutorizacionPendiente.as_view(), name = 'Autorizacion Pendiente'),

    # Vista de Comunicación
    path('comunicacion/',views.comunicacion, name="Comunicación"),

    #rutas de asesoria
    path('pantalla',views.asesorias_dashboard, name="asesorias_dashboard"),
    path('obtener_turnos/', views.obtener_turnos, name='obtener_turnos'),
    path('conteo_por_asesor/', views.conteo_por_asesor, name='Metricas Asesoria'),
    path('asesoria_metricas_dashboard/', views.asesoria_metricas_dashboard, name='Metricas dashboard'),
    path('asesorias/',views.asesorias_dashboard, name="asesorias_dashboard"),
    path('asesorias/asesor/',views.asesor, name="asesor"),
    path('asesorias/obtener_turnos/', views.obtener_turnos, name='obtener_turnos'),
    path('obtener_turnos/', views.obtener_turnos, name='obtener_turnos'),
    path('asesorias/asesor/llamar_turno/', views.llamar_turno, name='llamar_turno'),
    path('asesorias/asesor/cambiar_status/', views.cambiar_status, name='cambiar_status'),
    path('asesorias/cambiar_status_notificacion/', views.notificacion, name='cambiar_status_notificacion'),
    path('cambiar_status_notificacion/', views.notificacion, name='cambiar_status_notificacion'),
    path('asesorias/asesor/cambiar_status_notificacion/', views.notificacion, name='cambiar_status_notificacion'),
    path('asesorias/asesor/verTurnos/', views.notificacion, name='cambiar_status_notificacion'),
    path('asignarMesa', views.asignarMesa, name='AsignarMesa'),
    path('miMesa', views.miMesa, name='miMesa'),
    path('validar_turnos_abiertos', views.validar_turnos_abiertos, name='validar_turnos_abiertos'),
    path('iniciarAsesoria', views.iniciar_asesoria, name="iniciar_asesoria"),
    path('terminarAsesoria', views.terminar_asesoria, name="terminar_asesoria"),
    path('asesorias/asesor/cambiar_status_notificacion/', views.notificacion,name='cambiar_status_notificacion'),
    path('convertir-y-descargar-pdfs/', views.convertir_y_descargar_pdfs, name='convertir_y_descargar_pdfs'),
    path('fuentes_de_trabajo/', views.fuentes_de_trabajo, name="fuentes_de_trabajo"),
    path('agregar_fuentes_de_trabajo/', views.agregar_fuentes_de_trabajo, name="gregar_fuentes_de_trabajo"),
    path('pdf_local/', views.pdf_local, name="pdf_local"),
    path('ayuda_asesoria/', views.ayuda_auxiliares_asesoria, name="ayuda asesoria"),
    path('ver_solicitudes_asesor', views.ver_solicitud_ayuda, name='ver solicitudes asesor'),
    path('asesorias/auxiliares/', views.vista_auxiliares_asesoria, name='auxiliares asesoria'),
    path('asistir_asesor/', views.asistir_asesor, name='asistir asesor'),
    path('terminar_asistencia_asesor/', views.terminar_asistencia_asesor, name='termimar asistencia asesor'),

    path('validar_turnos_proceso/', views.validar_turnos_proceso, name='validar_turnos_proceso'),
    path('validar_audiencias_proceso/', views.validar_audiencias_proceso, name='validar_audiencias_proceso'),
    
    #rutas del chatbot 
    path('preRegistro', views.preRegistro, name='pre Registro'),
    path('chatQuery', views.chatQuery, name='chatQuery'),

    
    path('solicitud-genda-json/<int:id>/<int:formid>/', solicitudGenda, name='solicitud_genda_json'),

    # formulario ciudadano
    path('registroCiudadano/', registro_ciudadano, name='registro_ciudadano'),
    path('success/<int:pk>/', success, name='success'),
    path('buscar_ciudadano/', views.buscar_ciudadano, name='buscar_ciudadano'),
    path('registro_exitoso/', TemplateView.as_view(template_name="ciudadano/registro_exitoso.html"), name='registro_exitoso'),
    
    # path('leer_qr_camara_2/', leer_qr_camara_2, name='leer_qr_camara_2'),


    # definir solo vista
    # path('auto_turno_main/',TemplateView.as_view(template_name="turnos/registro_autoTurno.html")),
    path('auto_turno/', views.sacar_turno,name='auto_turno'),
    path('asignar_turno/',views.asignar_turno,name='asignar_turno'),
    path('asignar_turno_folio/',views.asignar_turno_folio,name='asignar_turno_folio'),
    path('actualizar_codigos_ciudadanos/',views.actualizar_codigos_ciudadanos,name='actualizar_codigos_ciudadanos'),
    path('verificar_estado_turno/', verificar_estado_turno, name='verificar_estado_turno'),
    path('registroareas/<str:area>/', OperacionAreaCreateView.as_view(), name='registro_area'),
    path('pagos/', views.VistaPagos.as_view(), name='pagos'),
    path('turnos/', views.VistaTurnosRecepcion, name='VistaTurnosRecepcion'),

    path('atender_pagos/', views.atender_pagos, name='atender_pagos'),
    path('cancelar_pago/', views.cancelar_pago, name='cancelar_pago'),
    path('citas_pagos/', views.citasPagos.as_view(), name='citas_pagos'),
    path('cancelarTurno/', views.cancelarTurno, name='cancelarTurno'),
    path('detalleTurno/', views.detalleTurno, name='detalleTurno'),

    path('pantallaTurno/', views.pantallaTurno, name='pantallaTurno'),
    path('cancelar_turno/<int:turno_id>/', views.cancelar_turno, name='cancelarTurno'),  

    #mesas
    path('mesas/', views.mesa_list, name='mesa_list'),
    path('mesas/<int:pk>/', views.mesa_detail, name='mesa_detail'),
    path('mesas/new/', views.mesa_create, name='mesa_create'),
    path('mesas/gi<int:pk>/edit/', views.mesa_update, name='mesa_update'),
    # path('mesas/<int:pk>/delete/', views.mesa_delete, name='mesa_delete'),  
    path('cancelar_turno/<int:turno_id>/', views.cancelar_turno, name='cancelarTurno'),   
    
    # conciliacion
    path('conciliacion/', TemplateView.as_view(template_name='conciliacion/index.html')),
    path('pantallaconciliacion/', TemplateView.as_view(template_name='conciliacion/pantalla.html')),
    path('conciliacion/auxiliares', TemplateView.as_view(template_name='conciliacion/auxiliar.html')),
    path('conciliacion/', views.salas_list, name = 'salas_list'),
    path('conciliador/', TemplateView.as_view(template_name ="conciliacion/conciliador.html")),
    path('edit_sala/', views.edit_sala, name='edit_sala'),
    path('delete_sala/<int:sala_id>/', views.delete_sala, name='delete_sala'),
    
    # path('salas/new/', views.sala_create, name='sala_create'),
    path('pantallaconciliacion/', TemplateView.as_view(template_name='conciliacion/pantalla.html')),


    # genera
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/seguridad/', views.perfil_seguridad, name='seguridad'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    path('consultar_estadisticas/', views.consultar_estadisticas, name='consultar_estadisticas'),
    path('face_recognition_test/', views.face_recognition_test, name='face_recognition_test'),

    #ratificacion
    path('ratificacion/auxiliares/', views.auxiliares_ratificacion, name='auxiliares_ratificacion'),
    path('ratificacion/metricas/', views.metricas_ratificacion, name='metricas_ratificacion'),
    path('cambiar_status_turno/', views.cambiar_status_turno, name='cambiar_status_turno'),
    path('ratificacion/pantalla/', views.pantalla_ratificaciones, name='pantalla_ratificacion'),
    path('asignar_conciliador/', views.asignar_conciliador, name='asignar_conciliador'),
    path('ratificacion/dashboard/', views.ratificacion_dashboard, name='ratificacion_dashboard'),
    path('conteo_por_conciliador/', views.conteo_por_conciliador, name='conteo_por_conciliador'),
    path('eliminar_ciudadano_ratis/<int:id>/', views.eliminar_ciudadano_ratis, name='eliminar_ciudadano_ratis'),
    path('remover_ciudadano_ratis/<int:id>/', views.remover_ciudadano_ratis, name='remover_ciudadano_ratis'),
    path('ratificacion_metricas_dashboard/', views.ratificacion_metricas_dashboard, name='Ratificacion Metricas dashboard'),
    path('actualizar_justificacion/', views.justificar_inactividad, name='justificar inactividad'),
    path('validar_si_justifico/', views.validar_si_justifico, name='validar si justifico'),
    path('conciliadores_disponibles/', views.administrar_conciliadores, name='conciliadores disponibles'),
    path('conciliadores_disponibles_notificacion/', views.conciliadores_disponibles_notificacion, name='conciliadores disponibles notificacion'),
    path('ver_quien_esta_disponible/', views.ver_quien_esta_disponible, name='ver quien esta disponible'),
    #path('ratificacion/conciliador/',views.conciliador, name="conciliador"),
    path('ratificacion/conciliador/',views.conciliador2, name="conciliador"),
    path('obtener_turnosRati/', views.obtener_turnosRati, name='obtener_turnosRati'),
    path('obtener_turnos_ratis/', views.obtener_turnos_ratificacion, name='obtener_turnosRati'),
    path('ratificacion/conciliador/obtener_turnosRati/', views.obtener_turnosRati, name='obtener_turnosRati'),
    path('obtener_turnosRati/', views.obtener_turnosRati, name='obtener_turnosRati'),
    path('ratificacion/conciliador/llamar_turno_ratis/', views.llamar_turno_rati, name='llamar_turnoRati'),
    path('ratificacion/conciliador/cambiar_status_rati/', views.cambiar_status, name='cambiar_statusRati'),
    path('cambiar_status_rati/', views.cambiar_status_turno, name='cambiar_status_rati'),
    path('asesorias/cambiar_status_notificacion/', views.notificacion, name='cambiar_status_notificacion'),
    path('ratificacion/conciliador/cambiar_status_notificacionRati/', views.notificacionRati, name='cambiar_status_notificacionRati'),
    path('ratificacion/conciliador/verTurnos/', views.notificacionRati, name='cambiar_status_notificacion'),
    path('cambiar_status_notificacion_rati/', views.notificacionRati, name='cambiar_status_notificacion'),
    path('asignarMesaRati/', views.asignarMesaRati, name='asignarMesaRati'),
    path('miMesaRati/', views.miMesaRati, name='miMesaRati'),
    path('validar_turnos_abiertos_rati/', views.validar_turnos_abiertosRati, name='validar_turnos_abiertosRati'),
    path('iniciar_ratificacion/', views.iniciar_conciliacion, name="iniciar_ratificacion"),
    path('terminar_ratificacion/', views.terminar_conciliacion, name="terminar_ratificacion"),
    path('ratificacion/conciliador/cambiar_status_notificacion_rati/', views.notificacionRati,name='cambiar_status_notificacion_rati'),
    path('actualizar_estado/', views.actualizar_estado, name='actualizar_estado'),
    path('iniciar_turno_automatico/', views.iniciar_turno_automatico, name='iniciar_turno_automatico'),
    path('turnos_auxiliares/', views.turnos_auxiliares, name='turnos_auxiliares'),
    path('mesa_de_ayuda/<int:pk>/', views.crear_mesa_ayuda, name='mesa ayuda'),
    path('validar_mesa_ayuda/', views.validar_mesa_ayuda, name='validar mesa ayuda'),
    path('bloquear_conciliador/', views.bloquear_conciliadores, name="bloquear conciliador"),

    
    
    # Generar turnos y añadir ciudadanos
    path('turnos_dia_actual/', views.turnos_dia_actual, name='turnos_dia_actual'),
    path('buscar_ciudadano_turno/', views.buscar_ciudadano_turno, name='buscar_ciudadano_turno'),
    path('agregar_ciudadano_turno/', agregar_ciudadano_turno, name='agregar_ciudadano_turno'),
    path('quitar_ciudadano_turno/', views.quitar_ciudadano_de_turno, name='quitar_ciudadano_turno'),
    path('registrar_adicional/', views.registrar_adicional, name='registrar_adicional'),
    path('cancelar_turno_recepcion/<int:turno_id>/', views.cancelar_turno_recepcion, name='cancelar_turno_recepcion'),


    

    path('upload/', upload_file, name='upload_file'),
    path('audiencias_auxiliares/',views.audiencias_auxiliares, name="audiencias_auxiliares"),
    path('llamar_audiencia/<int:audiencias_id>/', views.llamar_audiencia, name='llamar_audiencia'),
    path('asistencia/<int:pk>/', views.audiencia_asistencia, name='audiencia_asistencia'),
    path('celebrar/<int:pk>/', views.celebrar_audiencia_api, name='celebrar_audiencia'),
    path('obtener-notificaciones/', views.obtener_notificaciones, name='obtener_notificaciones'),
    path('notificacion_leida/<int:notificacion_id>/', views.notificacion_leida, name='notificacion_leida'),
    path('audiencia/editar/<int:pk>/', views.editar_audiencia_api, name='editar_audiencia'),
    path('asignar_auxiliar/<int:pk>/', views.asignar_auxiliar, name='asignar_auxiliar'),
    path('pantalla_audiencia/', views.pantalla_audiencia_api, name='pantalla_audiencia'),
    path('audiencias/ajax/', audiencias_ajax_view, name='audiencias_ajax'),
    path('audiencias/pendientes/ajax', audiencias_pendientes_ajax, name='audiencias_pendientes_ajax'),
    path('audiencia_mostrada/', audiencia_mostrada_ajax, name='audiencia_mostrada_ajax'),
    path('success_upload/', TemplateView.as_view(template_name='audiencia/success_upload.html'), name='success_upload'),
    path('audiencias/asignacion_salas/', views.asignacion_salas, name='asignacion_salas'),
    path('desocupar_sala/', views.desocupar_sala, name='desocupar_sala'),
    path('asignar_sala/', views.asignar_sala, name='asignar_sala'),

    # Endpoints Brigadistas
    path('conteo-ciudadanos/', ConteoCiudadanosPorDia.as_view(), name='conteo-ciudadanos'),

    #Envio encuestas
    path('encuestas_upload/', upload_and_send, name='upload-and-send'),

    #getaudiencias
    path('getaudiencias/', get_audiencias, name='getaudiencias'),
    path('audiencias_auxiliares_api/',views.audiencias_auxiliares_api, name="audiencias_auxiliares_api"),
    path('llamar_audiencia_api/<int:audiencias_id>/', views.llamar_audiencia_api, name='llamar_audiencia_api'),
    path('asistencia_api/<int:pk>/', views.audiencia_asistencia_api, name='audiencia_asistencia_api'),
    path('obtener-notificaciones-api/', views.obtener_notificaciones_api, name='obtener_notificaciones_api'),
    path('notificacion_leida_api/<int:notificacion_id>/', views.notificacion_leida_api, name='notificacion_leida_api'),
    path('celebrar_api/<int:pk>/', views.celebrar_audiencia_api, name='celebrar_audiencia_api'),
    path('asignar_auxiliar_api/<int:pk>/', views.asignar_auxiliar_api, name='asignar_auxiliar_api'),
    path('asistencia_auxiliares/<int:pk>/', views.asistencia_auxiliares, name='asistencia auxiliares'),
    path('ver_asistencias', views.ver_asistencias, name='ver asistencias'),
    path('asistir_conciliador/', views.asistir_conciliador, name='asistencia conciliador'),
    path('terminar_asistencia/', views.terminar_asistencia, name='terminar asistencia'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)