import os
import io
import pdb
import cv2
import time
import re
import json
import base64
import random
import imutils
import secrets
import tempfile
import requests
import pendulum
import mimetypes
import pandas as pd
import threading
import subprocess
import numpy as np
import urllib.parse
from .forms import *
from . models import *
from PIL import Image
from io import BytesIO
from typing import Any
from django.utils.dateformat import format
import json 
from datetime import timedelta
from django.db.models import Prefetch
from datetime import datetime
from bs4 import BeautifulSoup
from django.views import View 
from django.db.models import Q
from django.db.models.functions import Concat
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from reportlab.pdfgen import canvas
from django.shortcuts import render
from django.contrib import messages
from asgiref.sync import async_to_sync
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.forms import formset_factory
from django.core.mail import EmailMessage
from django.views.generic import CreateView
from django.utils.safestring import mark_safe
from django.forms import modelformset_factory
from channels.layers import get_channel_layer
from django.views.generic import TemplateView
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import A4, letter
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.contrib.auth.models import Group, User
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.http import Http404, HttpResponseRedirect
from django.core.files.storage import default_storage
from django.views.decorators.http import require_POST
from django.http import StreamingHttpResponse, Http404
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count,F, Func, Value, CharField
from django.views.decorators.http import require_http_methods
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from urllib.parse import urlencode
import unicodedata
from accounts.models import Profile
from django.utils.safestring import mark_safe
from django.db.models import Case, When, Value, IntegerField
from django.db.models.functions import TruncDate
from datetime import timedelta, datetime, date
import pytz

# Importaciones para endpoint ConteoCiudadanosPorDia
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection
from django.db.models import Case, When, Value, IntegerField, Sum, Min
from calendar import monthrange
from django.db.models.functions import TruncDate
import holidays
from collections import defaultdict

class ConteoCiudadanosPorDia(APIView):
    def get(self, request, *args, **kwargs):
        # Obtener la fecha del encabezado de la solicitud
        fecha_especifica = request.headers.get('Fecha-Especifica')  # Por ejemplo: "2024-09-11"
        
        if not fecha_especifica:
            return Response({"error": "No se ha proporcionado una fecha en los headers."}, status=400)

        with connection.cursor() as cursor:
            # Primera consulta: Conteo por turno del día específico
            query_turno = """
            WITH conteo_por_dia AS (
                SELECT t.fecha::date AS dia, COUNT(c.registro) AS cantidad_ciudadanos
                FROM core_turnos t
                JOIN core_ciudadanos c ON t.registro = c.registro
                WHERE t.fecha::date = %s
                GROUP BY t.fecha::date
            )
            SELECT dia, cantidad_ciudadanos,
                (SELECT SUM(cantidad_ciudadanos) FROM conteo_por_dia) AS total_general
            FROM conteo_por_dia
            ORDER BY dia;
            """
            cursor.execute(query_turno, [fecha_especifica])
            rows_turno = cursor.fetchall()

            # Segunda consulta: Conteo por día con status 'FIN'
            query_fin = """
            WITH conteo_por_dia AS (
                SELECT t.fecha::date AS dia, COUNT(c.registro) AS cantidad_ciudadanos
                FROM core_turnos t
                JOIN core_ciudadanos c ON t.registro = c.registro
                WHERE t.status = 'FIN' AND t.fecha::date = %s
                GROUP BY t.fecha::date
            )
            SELECT dia, cantidad_ciudadanos,
                   (SELECT SUM(cantidad_ciudadanos) FROM conteo_por_dia) AS total_general
            FROM conteo_por_dia
            ORDER BY dia;
            """
            cursor.execute(query_fin, [fecha_especifica])
            rows_fin = cursor.fetchall()

            # Tercera consulta: Conteo por día con status 'CAN'
            query_can = """
            WITH conteo_por_dia AS (
                SELECT t.fecha::date AS dia, COUNT(c.registro) AS cantidad_ciudadanos
                FROM core_turnos t
                JOIN core_ciudadanos c ON t.registro = c.registro
                WHERE t.status = 'CAN' AND t.fecha::date = %s
                GROUP BY t.fecha::date
            )
            SELECT dia, cantidad_ciudadanos,
                   (SELECT SUM(cantidad_ciudadanos) FROM conteo_por_dia) AS total_general
            FROM conteo_por_dia
            ORDER BY dia;
            """
            cursor.execute(query_can, [fecha_especifica])
            rows_can = cursor.fetchall()

        # Función para sumar el segundo valor (cantidad_ciudadanos) en una lista de tuplas
        def sumar_cantidad(rows):
            return sum(row[1] for row in rows)  # row[1] es 'cantidad_ciudadanos'

        # Sumar los valores de cada conjunto de filas
        total_turnos = sumar_cantidad(rows_turno)
        total_fin = sumar_cantidad(rows_fin)
        total_can = sumar_cantidad(rows_can)

        # Calcular el valor de "Status PEN"
        total_pen = total_turnos - (total_fin + total_can)

        # Retornar los datos de las tres consultas y el valor calculado
        return Response({
            "Total Turnos": rows_turno,
            "Status FIN": rows_fin,
            "Status CAN": rows_can,
            "Status PEN": total_pen,
        })

@method_decorator(login_required, name='dispatch')
class VistaInicio(TemplateView):
    template_name = 'general/index.html'

        #return render(request, 'general/index.html', {'active_view': 'Inicio'})
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        nombreGrupo = None

        if usuario.is_authenticated:
            grupo = Group.objects.filter(user=usuario).first()

            if grupo:
                nombreGrupo = grupo.name
        context['usuario'] = usuario
        context['nombreGrupo'] = nombreGrupo
        context['active_view'] = 'Inicio'

        return context
    
class VistaInicioAsesoria(TemplateView):
    template_name = 'general1/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        nombreGrupo = None
        turnos_atendidos = 0

        if usuario.is_authenticated:
            grupo = Group.objects.filter(user=usuario).first()
            if grupo:
                nombreGrupo = grupo.name

            # Obtener estadísticas del usuario

            if estadisticas:
                turnos_atendidos = estadisticas.turnos_atendidos

        context['usuario'] = usuario
        context['nombreGrupo'] = nombreGrupo
        context['turnos_atendidos'] = turnos_atendidos

        return context  

def registro(request):
    if request.method == 'POST':
        form = formularioRegistro(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.correo = form.cleaned_data.get('correo')
            user.first_name = form.cleaned_data.get('nombre')
            user.last_name = form.cleaned_data.get('apellido')
            user.save()
            login(request, user)
            response = HttpResponseRedirect(reverse('Inicio'))
            return response
        else:
            response = render(request, 'registration/registro.html', {'form': form})
            return response
    else:
        form = formularioRegistro()
        response = render(request, 'registration/registro.html', {'form': form})
        return response

# Función para generar un número de 10 dígitos, ciudadanoID
def generate_10_digit_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(10)])


##################################### EHW  #########################################################
class registroRatiEWH(TemplateView):
    template_name = 'recepcion/solicitudRatis.html'

        #return render(request, 'general/index.html', {'active_view': 'Inicio'})
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        nombreGrupo = None
        form = turnoForm()

        if usuario.is_authenticated:
            grupo = Group.objects.filter(user=usuario).first()

            if grupo:
                nombreGrupo = grupo.name
        context['usuario'] = usuario
        context['nombreGrupo'] = nombreGrupo
        context['active_view'] = 'Registro Ratificaciones'
        context['form'] = form

        return context
    


urlin = 'https://sinacol.ccljalisco.gob.mx/login'
urlout = 'https://sinacol.ccljalisco.gob.mx/logout'
urlfolio = 'https://sinacol.ccljalisco.gob.mx/solicitudes/folio'

sessionSinacol = requests.Session()

def get_token_login():
    try:
        response = sessionSinacol.get(urlin)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        input_token = soup.find('input', {'name': '_token'})
        if input_token:
            return input_token['value']
        else:
            return None
    except requests.RequestException as e:
        print(f"Error al obtener el token de login: {e}")
        return None


def get_token_requests(token):
    data = {
        'email': "orientador.prueba@ccljalisco.gob.mx",
        'password': "Sinacol2022$",
        '_token': token
    }
    headers = {'Content-Type': 'application/json'}
    try:
        response = sessionSinacol.post(urlin, json=data, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        input_token = soup.find('input', {'name': '_token'})
        if input_token:
            return input_token['value']
        else:
            return None
    except requests.RequestException as e:
        print(f"Error al obtener el token de requests: {e}")
        return None
    

def primerPaso():
    token1 = get_token_login()
    if token1:
        token2 = get_token_requests(token1)
        if token2:
            return token2
        else:
            return JsonResponse({'error': 'No se pudo obtener el token de requests', 'token1': token1, 'token2': token2}, status=100)
    else:
        return JsonResponse({'error': 'No se pudo obtener el token de login'}, status=500)


def segundoPaso():
    try:
        response = sessionSinacol.get(urlout)
        response.raise_for_status()
        mensaje = "Se cerró conexión con exito"
        return mensaje
    except requests.RequestException as e:
        mensaje = f"Error al cerrar sesión"
        return mensaje
    
@csrf_exempt        
def dataRati(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        folio_solicitud = body.get('folio_solicitud')
        anio_solicitud = body.get('anio_solicitud')

        validate = "true"
        token = primerPaso()
        
        data = {
            'folio': folio_solicitud,
            'anio': anio_solicitud,
            'validate': validate,
            '_token': token
        }
        
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = sessionSinacol.post(urlfolio, json=data, headers=headers)
            response.raise_for_status()
            
            if response.ok: 
                response_data = response.json()
                segundoPaso()
                return JsonResponse({'Respuesta': response_data})
            else:
                return JsonResponse({'Error': 'No se obtuvieron datos de la consulta', 'status': response.status_code}, status=response.status_code)
        
        except requests.RequestException as e:
            mensaje = f"Error al procesar la solicitud: {e}"
            return JsonResponse({'error': mensaje}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405) 




def get_next_individual_registro():
        contador_registro = contadorRegistros.objects.first()
        if contador_registro is None:
            contador_registro = contadorRegistros.objects.create(contador=1)
            contador = 1
        else:
            contador = contador_registro.contador + 1
        timestamp = pendulum.now().format('YYYYMMDDHHmmssSSS')
        incrementar_contador_registro(1)
        return f"{contador}_{timestamp}"


@csrf_exempt
def insertar_ciudadanos(request):
    if request.method == 'POST':
        try:
            # Obtener datos JSON del cuerpo de la solicitud
            data = json.loads(request.body)
            if not isinstance(data.get('c'), dict):
                return JsonResponse({'mensaje': 'El parámetro "c" debe ser un objeto JSON'}, status=400)
            if not isinstance(data.get('s'), dict):
                return JsonResponse({'mensaje': 'El parámetro "s" debe ser un objeto JSON'}, status=400)
            citados = data.get('c', {})
            solicitantes = data.get('s', {})
            folio = data.get('f', '')

            registro_nuevo = get_next_individual_registro()
            if isinstance(citados, dict):
                for key in citados:
                    citado = citados.get(key)
                    if isinstance(citado, dict):
                        if citado.get('nombreCompleto'):
                            texto_nombre = citado.get('nombreCompleto')
                        else:
                            texto_nombre = "Fuente: " + citado.get('nombreComercial')
                        id_ciudadano = generate_10_digit_code()
                        ciudadano = ciudadanos.objects.create(
                            nombre= texto_nombre,
                            sexo='Masculino' if citado.get('sexo') == 1 else 'Femenino' if citado.get('sexo') == 2 else 'N/A',
                            municipio=citado.get('municipio'),
                            tipo_persona=citado.get('tipo_persona'),
                            codigo_ciudadano=id_ciudadano,
                            registro = registro_nuevo
                        )
                        # Crear registro en la tabla Solicitud
                        Solicitud.objects.create(
                            folio_solicitud=folio,
                            id_ciudadano=ciudadano.id,
                            registro=ciudadano.registro
                        )
                    else:
                        print(f"Error: El valor para la clave '{key}' no es un diccionario")
            else:
                print("Error: 'citados' no es un diccionario")
            


            for solicitante1 in solicitantes:
                solicitante = solicitantes[solicitante1]
                if solicitante.get('nombreCompleto'):
                    texto_nombre = solicitante.get('nombreCompleto')
                else:
                    texto_nombre = "Fuente: " + solicitante.get('nombreComercial')
                id_ciudadano = generate_10_digit_code()
                ciudadano = ciudadanos.objects.create(
                    nombre=texto_nombre,
                    sexo='Masculino' if solicitante.get('sexo') == 1 else 'Femenino' if solicitante.get('sexo') == 2 else 'N/A',
                    municipio=solicitante.get('municipio'),
                    tipo_persona=solicitante.get('tipo_persona'),
                    codigo_ciudadano=id_ciudadano,
                    registro = registro_nuevo
                )
                # Crear registro en la tabla Solicitud
                Solicitud.objects.create(
                    folio_solicitud=folio,
                    id_ciudadano=ciudadano.id,
                    registro=ciudadano.registro
                )
                
            return JsonResponse({'success': 'success1'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'mensaje': 'Error al decodificar JSON'}, status=400)
    else:
        return JsonResponse({'mensaje': 'Metodo no permitido'}, status=403)
    


@csrf_exempt
def registrar_adicional(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        sexo = request.POST.get('sexo')
        tipo_persona = request.POST.get('tipo_persona')
        municipio = request.POST.get('municipio')
        registro = request.POST.get('registro')
        folio = request.POST.get('folio')
        codigo = request.POST.get('codigo')

        if codigo:
            actualizar_ciudadano = ciudadanos.objects.get(codigo_ciudadano= codigo)
            actualizar_ciudadano.registro = registro
            actualizar_ciudadano.save()

            asistencia = Solicitud(
                folio_solicitud = folio,
                id_ciudadano = actualizar_ciudadano.id,
                asistencia = True,
                registro = registro
            )
            asistencia.save()

            return JsonResponse({
                'id': actualizar_ciudadano.id,
                'nombre': actualizar_ciudadano.nombre,
                'sexo': actualizar_ciudadano.sexo,
                'tipo_persona': actualizar_ciudadano.tipo_persona,
                'municipio': actualizar_ciudadano.municipio,
                'asistencia': asistencia.asistencia
            })
        else:

            if not nombre or not sexo or not tipo_persona or not municipio:
                return JsonResponse({'error': 'Todos los campos son obligatorios.'}, status=400)
            
            codigo_ciudadano = generate_10_digit_code()
            nuevo_ciudadano = ciudadanos(
                nombre=nombre,
                sexo=sexo,
                tipo_persona=tipo_persona,
                municipio=municipio,
                codigo_ciudadano = codigo_ciudadano,
                registro = registro
            )
            nuevo_ciudadano.save()

            folio_actualizado = Solicitud(folio_solicitud=folio, id_ciudadano=nuevo_ciudadano.id, registro=nuevo_ciudadano.registro)
            folio_actualizado.save()

            # Devolver la información del nuevo ciudadano como JSON
            return JsonResponse({
                'id': nuevo_ciudadano.id,
                'nombre': nuevo_ciudadano.nombre,
                'sexo': nuevo_ciudadano.sexo,
                'tipo_persona': nuevo_ciudadano.tipo_persona,
                'municipio': nuevo_ciudadano.municipio
            })

    return JsonResponse({'error': 'Método no permitido'}, status=405)



@csrf_exempt
@require_http_methods(["DELETE"])
def eliminar_ciudadano_ratis(request, id):
    try:
        folio = Solicitud.objects.filter(id_ciudadano=id)
        ciudadane = ciudadanos.objects.get(id=id)
        folio.delete()
        ciudadane.delete()
        return JsonResponse({'success': True, 'message': 'Ciudadano eliminado con éxito.'})
    except ciudadane.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Ciudadano no encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Error al eliminar ciudadano: ' + str(e)}, status=500)




@csrf_exempt
@require_http_methods(["PATCH"])
def remover_ciudadano_ratis(request, id):
    try:
        ciudadane = ciudadanos.objects.get(id=id)
        ciudadane.registro = None
        ciudadane.save()
        return JsonResponse({'success': True, 'message': 'Ciudadano eliminado con éxito.'})
    except ciudadane.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Ciudadano no encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Error al eliminar ciudadano: ' + str(e)}, status=500)

    


def buscar_folio_anio(request):
    folio = request.GET.get('folio_solicitud')
    anio = request.GET.get('anio_solicitud')
    
    if not folio or not anio:
        return JsonResponse({'success': True, 'message': 'Folio y año son requeridos.'})
    
    folio_anio = f"{folio}/{anio}"
    
    try:
        # Filtra las solicitudes por folio + año concatenados
        solicitudes = Solicitud.objects.filter(folio_solicitud=folio_anio)
        
        if not solicitudes.exists():
            return JsonResponse({'success': False, 'message': 'No se encontró la solicitud.'})

        # Recupera todos los ciudadanos relacionados a estas solicitudes usando el campo correcto
        ciudadanose = ciudadanos.objects.filter(id__in=solicitudes.values('id_ciudadano'))
        
        ciudadanos_data = []
        for ciudadano in ciudadanose:
            ciudadanos_data.append({
                'id': ciudadano.id,
                'nombre': ciudadano.nombre,
                'sexo': ciudadano.sexo,
                'municipio': ciudadano.municipio,
                'tipo_persona': ciudadano.tipo_persona,
                'registro' : ciudadano.registro
            })
        
        response_data = {
            'solicitudes': list(solicitudes.values()),
            'ciudadanos': ciudadanos_data
        }
        
        return JsonResponse({'success': True, 'data': response_data})
    except Exception as e:
        return JsonResponse({'success': True, 'message': str(e)})




@csrf_exempt
def update_attendance(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        front_image = data.get('frontImage')
        back_image = data.get('backImage')
        ciudadano_id = data.get('id')

        
        # Procesar imagen frontal
        front_image_data = front_image.split(',')[1]
        front_image_file = ContentFile(base64.b64decode(front_image_data), name=f'{ciudadano_id}_front.png')
        front_image_path = default_storage.save(f'identificacion/{front_image_file.name}', front_image_file)
        
        
        # Procesar imagen trasera
        back_image_data = back_image.split(',')[1]
        back_image_file = ContentFile(base64.b64decode(back_image_data), name=f'{ciudadano_id}_back.png')
        back_image_path = default_storage.save(f'identificacion/{back_image_file.name}', back_image_file)
        
        
        # Actualizar base de datos
        ciudadano = ciudadanos.objects.get(id=ciudadano_id)
        ciudadano.documento_1 = front_image_path
        ciudadano.documento_2 = back_image_path
        ciudadano.save()

        solicitud = Solicitud.objects.get(id_ciudadano=ciudadano_id)
        solicitud.asistencia = True
        solicitud.save()
        
        return JsonResponse({'success': True})


def update_attendance_testigos(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        front_image = data.get('frontImage1')
        back_image = data.get('backImage1')
        front_image = data.get('frontImage2')
        back_image = data.get('backImage2')
        ciudadano_id = data.get('id')

        
        # Procesar imagen frontal
        front_image_data1 = front_image.split(',')[1]
        front_image_file1 = ContentFile(base64.b64decode(front_image_data1), name=f'{ciudadano_id}_front.png')
        front_image_path1 = default_storage.save(f'testigos/{front_image_file1.name}', front_image_file1)
        
        
        # Procesar imagen trasera
        back_image_data1 = back_image.split(',')[1]
        back_image_file1 = ContentFile(base64.b64decode(back_image_data1), name=f'{ciudadano_id}_back.png')
        back_image_path1 = default_storage.save(f'testigos/{back_image_file1.name}', back_image_file1)

        # Procesar imagen frontal
        front_image_data2 = front_image.split(',')[1]
        front_image_file2 = ContentFile(base64.b64decode(front_image_data2), name=f'{ciudadano_id}_front.png')
        front_image_path2 = default_storage.save(f'testigos/{front_image_file2.name}', front_image_file2)
        
        
        # Procesar imagen trasera
        back_image_data2 = back_image.split(',')[1]
        back_image_file2 = ContentFile(base64.b64decode(back_image_data2), name=f'{ciudadano_id}_back.png')
        back_image_path2 = default_storage.save(f'testigos/{back_image_file2.name}', back_image_file2)
        
        
        
        # Actualizar base de datos
        ciudadano = ciudadanos.objects.get(id=ciudadano_id)
        codigo = ciudadano.codigo_ciudadano
        testigo = testigos(
            documento_3 = front_image_path1,
            documento_4 = back_image_path1,
            documento_5 = front_image_path2,
            documento_6 = back_image_path2,
            codigo_ciudadano = codigo
        )
        testigo.save()


        solicitud = Solicitud.objects.get(id_ciudadano=ciudadano_id)
        solicitud.asistencia = True
        solicitud.save()
        
        return JsonResponse({'success': True})



def buscar_ciudadano_autocompletar(request):
    query = request.GET.get('q', '').strip()
    resultados = ciudadanos.objects.filter(nombre__icontains=query)
    sugerencias = [{
        'nombre': c.nombre, 
        'sexo': c.sexo, 
        'tipo_persona': c.tipo_persona, 
        'municipio': c.municipio, 
        'codigo': c.codigo_ciudadano, 
        'ine': c.documento_1.url if c.documento_1 else ''} for c in resultados if 'Fuente:' not in c.nombre]
    return JsonResponse(sugerencias, safe=False)

#####################################  EHW  #######################################################################
    
    
class VistaRegistroManual(View):
    registros_multiples = False  # Rastrear múltiples formularios enviados simultáneamente

    def get(self, request):
        registro_activo = self.get_or_create_registro_activo(request)
        registro_actual = registro_activo.registro_actual
        ciudadanoFormSet = formset_factory(formularioRegistroManual)
        formset = ciudadanoFormSet()
        ciudadanos_con_registro_actual = ciudadanos.objects.filter(registro=registro_actual)

        return render(request, 'recepcion/registroManual/registroManual.html', {
            'formset': formset,
            'active': 'Registro Manual',
            'ciudadanos': ciudadanos_con_registro_actual,
            'registro': registro_actual
        })

    def post(self, request):
        if 'terminar_registro' in request.POST:
            return self.terminar_registro(request)
        else:
            return self.guardar_y_continuar(request)

    def guardar_y_continuar(self, request):
        registro_activo = self.get_or_create_registro_activo(request)
        registro_actual = registro_activo.registro_actual
        ciudadanoFormSet = formset_factory(formularioRegistroManual)
        formset = ciudadanoFormSet(request.POST, request.FILES)

        if formset.is_valid():
            for index, form in enumerate(formset):
                ciudadano = form.save(commit=False)
                ciudadano.codigo_ciudadano = generate_10_digit_code()
                ciudadano.registro = registro_actual
                ciudadano.save()
                self.handle_images(request.POST, ciudadano, index)

            ciudadanos_con_registro_actual = ciudadanos.objects.filter(registro=registro_actual)
            self.incrementar_contador_registro(1)
            formset = ciudadanoFormSet()

            return render(request, 'recepcion/registroManual/registroManual.html', {
                'formset': formset,
                'active': 'Registro Manual',
                'ciudadanos': ciudadanos_con_registro_actual,
                'registro': registro_actual
            })
        else:
            ciudadanos_con_registro_actual = ciudadanos.objects.filter(registro=registro_actual)

            return render(request, 'recepcion/registroManual/registroManual.html', {
                'formset': formset,
                'active': 'Registro Manual',
                'ciudadanos': ciudadanos_con_registro_actual,
                'registro': registro_actual
            })

    def get_or_create_registro_activo(self, request):
        registro_activo, created = RegistroActivo.objects.get_or_create(usuario=request.user)
        if created or not registro_activo.registro_actual:
            registro_activo.registro_actual = self.get_next_individual_registro()
            registro_activo.save()
        return registro_activo

    def terminar_registro(self, request):
    
        registro_activo = self.get_or_create_registro_activo(request)
        registro_actual = registro_activo.registro_actual
        nuevo_registro = self.get_next_individual_registro()
        registro_activo.registro_actual = nuevo_registro
        registro_activo.save()
        return HttpResponseRedirect(reverse('auto_turno') + f'?registro={registro_actual}')

    def get_next_individual_registro(self):
        contador_registro = contadorRegistros.objects.first()
        if contador_registro is None:
            contador_registro = contadorRegistros.objects.create(contador=1)
            contador = 1
        else:
            contador = contador_registro.contador + 1
        timestamp = pendulum.now().format('YYYYMMDDHHmmssSSS')
        incrementar_contador_registro(1)
        return f"{contador}_{timestamp}"

    def incrementar_contador_registro(self, num_personas):
        contador_registro = contadorRegistros.objects.first()
        if contador_registro is None:
            contador_registro = contadorRegistros.objects.create(contador=num_personas)
        else:
            contador_registro.contador += num_personas
        contador_registro.save()

    def handle_images(self, post_data, ciudadano, index):
        documento_fields = {
            'documento_1': f'documento_1_{index}',
            'documento_2': f'documento_2_{index}',
            'documento_3': f'documento_3_{index}',
            'documento_4': f'documento_4_{index}',
            'documento_5': f'documento_5_{index}',
            'documento_6': f'documento_6_{index}'
        }

        # Procesar documentos de ciudadanos
        for key, field in documento_fields.items():
            data_url = post_data.get(field)
            if data_url:
                try:
                    formato, imgstr = data_url.split(';base64,')
                    ext = formato.split('/')[-1]
                    data = ContentFile(base64.b64decode(imgstr), name=f'{ciudadano.id}_{key}.{ext}')
                    if key == 'documento_1':
                        ciudadano.documento_1.save(f'{ciudadano.id}_documento_1.{ext}', data, save=False)
                    elif key == 'documento_2':
                        ciudadano.documento_2.save(f'{ciudadano.id}_documento_2.{ext}', data, save=False)
                except (TypeError, ValueError, base64.binascii.Error) as e:
                    print(f"Error processing {key}: {e}")

        # Procesar documentos de testigos si están presentes en post_data
        curp_rfc_testigo_1 = post_data.get(f'curp_rfc_testigo_1_{index}')
        municipio_testigo_1 = post_data.get(f'municipio_testigo_1_{index}')
        curp_rfc_testigo_2 = post_data.get(f'curp_rfc_testigo_2_{index}')
        municipio_testigo_2 = post_data.get(f'municipio_testigo_2_{index}')

        if any([post_data.get(f'documento_3_{index}'), 
                post_data.get(f'documento_4_{index}'),
                post_data.get(f'documento_5_{index}'), 
                post_data.get(f'documento_6_{index}')]):

            testigo = testigos(
                registro=ciudadano.registro, 
                curp_rfc_ciudadano=ciudadano.curp_rfc, 
                codigo_ciudadano=ciudadano.codigo_ciudadano,
                curp_rfc_testigo_1=curp_rfc_testigo_1,
                municipio_testigo_1=municipio_testigo_1,
                curp_rfc_testigo_2=curp_rfc_testigo_2,
                municipio_testigo_2=municipio_testigo_2
            )

            for key in ['documento_3', 'documento_4', 'documento_5', 'documento_6']:
                field = f'{key}_{index}'
                data_url = post_data.get(field)
                if data_url:
                    try:
                        formato, imgstr = data_url.split(';base64,')
                        ext = formato.split('/')[-1]
                        data = ContentFile(base64.b64decode(imgstr), name=f'{ciudadano.id}_{key}.{ext}')
                        if key == 'documento_3':
                            testigo.documento_3.save(f'{ciudadano.id}_testigo_1_Frente.{ext}', data, save=False)
                        elif key == 'documento_4':
                            testigo.documento_4.save(f'{ciudadano.id}_testigo_1_Reverso.{ext}', data, save=False)
                        elif key == 'documento_5':
                            testigo.documento_5.save(f'{ciudadano.id}_testigo_2_Frente.{ext}', data, save=False)
                        elif key == 'documento_6':
                            testigo.documento_6.save(f'{ciudadano.id}_testigo_2_Reverso.{ext}', data, save=False)
                    except (TypeError, ValueError, base64.binascii.Error) as e:
                        print(f"Error processing {key}: {e}")

            testigo.save()

        ciudadano.save()

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)











def buscar_datos_ciudadano(request):
    query = request.GET.get('q')
    if query:
        resultados = ciudadanos.objects.filter(
            Q(nombre__icontains=query)
        )
    else:
        resultados = ciudadanos.objects.none()
    return render(request, 'recepcion/buscar_datos_ciudadano.html', {'resultados': resultados})

    
class recepcion_registro_ia(TemplateView):
    template_name = 'recepcion/Registrar_con_IA.html'

def generar_token(request):
    process = subprocess.Popen(['node', './static/idmision/index.js'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output, error = process.communicate()
    if process.returncode == 0:
        token_output = output.strip()
        token = token_output.split(':')[-1].strip()
    return JsonResponse({'token': token})

class VistaMantenimiento(TemplateView):
    template_name = 'general/vista_mantenimiento.html'

class RegistroConQR(TemplateView):
    template_name = 'recepcion/Registrar_con_QR.html'

class VistaAdministrador(TemplateView):
    template_name = 'administrador.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        nombreGrupo = None

        if usuario.is_authenticated:
            grupo = Group.objects.filter(user=usuario).first()

            if grupo:
                nombreGrupo = grupo.name
        context['usuario'] = usuario
        context['nombreGrupo'] = nombreGrupo

        return context   
    
@method_decorator(login_required, name='dispatch')
class VistaAutorizacionPendiente(TemplateView):
    template_name = 'areas/autorizacion_pendiente.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        nombreGrupo = None

        if usuario.is_authenticated:
            grupo = Group.objects.filter(user=usuario).first()

            if grupo:
                nombreGrupo = grupo.name
        context['usuario'] = usuario
        context['nombreGrupo'] = nombreGrupo

        return context
    
class VistaRecepcion(TemplateView):
    template_name = 'recepcion/recepcion.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_view'] = 'Recepcion'

        return context

class VistaTurneroPagos(TemplateView):
    template_name = 'turnero/pagos.html'

def consumoApi(request):
    data = request.GET.get('info')
    id = None
    formid = None
    if data is not None:
        formid,id = data.split(",")
    if id is None and formid is None:
        respuesta = 'Codigo qr no valido'
    else: 
        respuesta = solicitudGenda(id, formid)
    return respuesta

# Obtener Token      
def solicitarJWT():
    url = "https://citasccljalisco.gob.mx/index.php/wp-json/jwt-auth/v1/token"
    body = {
        "username": "turnero.ccl",
        "password": "tZ9X$DemVdOvpFmwl0x@f1*f"
    }
    response = requests.post(url, json=body)
    return response

# Jala los datos de wordpress
def solicitudGenda(id, formid):
    url_final = "https://citasccljalisco.gob.mx/api/consultarCita"
    response = solicitarJWT()

    if response.status_code == 200:
        data = response.json()
        token = data["token"]
        params = {
            "id": id,
            "formid": formid,
            "Authorization": token
        }
        response2 = requests.get(url_final, params=params)

        if response2.status_code == 200:
            response2 = response2.json()
            if formid == '10':
                respuesta = filtroAsesoriaJuridica(response2)
                #return JsonResponse({ 'Respuesta Servidor': response2[0]['posted_data'] })
            elif formid == '16':
                respuesta = filtroRatificaciones(response2)
            else:
                respuesta = {
                    'payload': 'El QR no corresponde a la sede AMG o no es valido'
                    }
            return JsonResponse({'resultadoAPI': respuesta }, status=200)
        else:
            return JsonResponse({'Error': 'error al consutar datos', 'formid': formid, 'id': id, 'token': token , 'status_code': response2.status_code, 'Respuesta Servidor': response2.json()}, status=response2.status_code)
    else:
        return JsonResponse({'error': 'Error en la solicitud', 'response': response.json() , 'status_code': response.status_code}, status=response.status_code)

def filtroAsesoriaJuridica(data):
    respuesta = {}
    data = data[0]
    data_separado = data['posted_data'] if data is not None else 'error'
    if data_separado == 'error':
        respuesta['Error'] = 'tipo de persona erroneo en la cita'
        return respuesta
    id = data['id']
    formid = data['formid']
    separado = data_separado.split('"')
    tipo_persona = separado[separado.index('fieldname41')+2]
    trabajador = {}
    documentacion = {}
    empleador = {}
    cita = {}
    asesoria = {}
    correo ={}

    if tipo_persona == 'Soy persona Trabajadora':
        trabajador['nombre'] = separado[separado.index('fieldname4')+2] if 'fieldname4' in separado else None
        trabajador['apellidopaterno'] = separado[separado.index('fieldname5')+2] if 'fieldname5' in separado else None
        trabajador['apellidomaterno'] = separado[separado.index('fieldname6')+2] if 'fieldname6' in separado else None
        trabajador['sexo'] = separado[separado.index('fieldname28')+2] if 'fieldname28' in separado else None
        trabajador['correo'] = separado[separado.index('fieldname112')+2] if 'fieldname112' in separado else None
        documentacion['trabajador_id'] = separado[separado.index('fieldname20_url')+2] if 'fieldname20' in separado else None
        cita['hora_cita'] = pendulum.from_format(separado[separado.index('app_starttime_1')+2].strip().rstrip('\\'), "hh:mm A").time() if 'app_starttime_1' in separado else None
        cita['dia_cita'] = pendulum.from_format(separado[separado.index('app_date_1')+2], "DD/MM/YYYY").date() if 'app_date_1' in separado else None
        cita['id_cita'] = id

    elif tipo_persona == 'Soy persona Física Empleadora':
        trabajador['nombre'] = separado[separado.index('fieldname130')+2] if 'fieldname130' in separado else None
        trabajador['apellidopaterno'] = separado[separado.index('fieldname131')+2] if 'fieldname131' in separado else None
        trabajador['apellidomaterno'] = separado[separado.index('fieldname132')+2] if 'fieldname132' in separado else None
        trabajador['sexo'] = separado[separado.index('fieldname150')+2] if 'fieldname150' in separado else None
        trabajador['correo'] = separado[separado.index('fieldname134')+2] if 'fieldname134' in separado else None
        documentacion['trabajador_id'] = separado[separado.index('fieldname133_url')+2] if 'fieldname133' in separado else None


        trabajador['nombre2'] = separado[separado.index('fieldname136')+2] if 'fieldname136' in separado else None
        trabajador['apellidopaterno2'] = separado[separado.index('fieldname137')+2] if 'fieldname137' in separado else None
        trabajador['apellidomaterno2'] = separado[separado.index('fieldname138')+2] if 'fieldname138' in separado else None
        trabajador['sexo2'] = separado[separado.index('fieldname151')+2] if 'fieldname151' in separado else None
        trabajador['correo2'] = separado[separado.index('fieldname140')+2] if 'fieldname140' in separado else None
        documentacion['trabajador2_id'] = separado[separado.index('fieldname139_url')+2] if 'fieldname139' in separado else None


        trabajador['nombre3'] = separado[separado.index('fieldname153')+2] if 'fieldname153' in separado else None
        trabajador['apellidopaterno3'] = separado[separado.index('fieldname154')+2] if 'fieldname154' in separado else None
        trabajador['apellidomaterno3'] = separado[separado.index('fieldname155')+2] if 'fieldname155' in separado else None
        trabajador['sexo3'] = separado[separado.index('fieldname156')+2] if 'fieldname156' in separado else None
        trabajador['correo3'] = separado[separado.index('fieldname158')+2] if 'fieldname158' in separado else None
        documentacion['trabajador3_id'] = separado[separado.index('fieldname157_url')+2] if 'fieldname157' in separado else None


        trabajador['nombre4'] = separado[separado.index('fieldname160')+2] if 'fieldname160' in separado else None
        trabajador['apellidopaterno4'] = separado[separado.index('fieldname161')+2] if 'fieldname161' in separado else None
        trabajador['apellidomaterno4'] = separado[separado.index('fieldname162')+2] if 'fieldname162' in separado else None
        trabajador['sexo4'] = separado[separado.index('fieldname163')+2] if 'fieldname163' in separado else None
        trabajador['correo4'] = separado[separado.index('fieldname165')+2] if 'fieldname165' in separado else None
        documentacion['trabajador4_id'] = separado[separado.index('fieldname164_url')+2] if 'fieldname164' in separado else None


        trabajador['nombre5'] = separado[separado.index('fieldname167')+2] if 'fieldname167' in separado else None
        trabajador['apellidopaterno5'] = separado[separado.index('fieldname168')+2] if 'fieldname168' in separado else None
        trabajador['apellidomaterno5'] = separado[separado.index('fieldname169')+2] if 'fieldname169' in separado else None
        trabajador['sexo5'] = separado[separado.index('fieldname170')+2] if 'fieldname170' in separado else None
        trabajador['correo5'] = separado[separado.index('fieldname172')+2] if 'fieldname172' in separado else None
        documentacion['trabajador5_id'] = separado[separado.index('fieldname171_url')+2] if 'fieldname171' in separado else None


        empleador['nombre'] = separado[separado.index('fieldname106')+2] if 'fieldname106' in separado else None
        empleador['apellidopaterno'] = separado[separado.index('fieldname107')+2] if 'fieldname107' in separado else None
        empleador['apellidomaterno'] = separado[separado.index('fieldname108')+2] if 'fieldname108' in separado else None
        empleador['sexo'] = separado[separado.index('fieldname109')+2] if 'fieldname109' in separado else None
        empleador['correo'] = separado[separado.index('fieldname128')+2] if 'fieldname128' in separado else None
        documentacion['empleador_id'] = separado[separado.index('fieldname111_url')+2] if 'fieldname111' in separado else None
        
        cita['hora_cita'] = pendulum.from_format(separado[separado.index('app_starttime_1')+2].strip().rstrip('\\'), "hh:mm A").time() if 'app_starttime_1' in separado else None
        cita['dia_cita'] = pendulum.from_format(separado[separado.index('app_date_1')+2], "DD/MM/YYYY").date() if 'app_date_1' in separado else None
        cita['id_cita'] = id


    elif tipo_persona == 'Persona Jurídica Empleadora':
        trabajador['nombre'] = separado[separado.index('fieldname69')+2] if 'fieldname69' in separado else None
        trabajador['apellidopaterno'] = separado[separado.index('fieldname70')+2] if 'fieldname70' in separado else None
        trabajador['apellidomaterno'] = separado[separado.index('fieldname71')+2] if 'fieldname71' in separado else None
        trabajador['sexo'] = separado[separado.index('fieldname145')+2] if 'fieldname145' in separado else None
        trabajador['correo'] = separado[separado.index('fieldname119')+2] if 'fieldname119' in separado else None
        documentacion['trabajador_id'] = separado[separado.index('fieldname123_url')+2] if 'fieldname123' in separado else None


        trabajador['nombre2'] = separado[separado.index('fieldname73')+2] if 'fieldname73' in separado else None
        trabajador['apellidopaterno2'] = separado[separado.index('fieldname74')+2] if 'fieldname74' in separado else None
        trabajador['apellidomaterno2'] = separado[separado.index('fieldname75')+2] if 'fieldname75' in separado else None
        trabajador['sexo2'] = separado[separado.index('fieldname146')+2] if 'fieldname146' in separado else None
        trabajador['correo2'] = separado[separado.index('fieldname118')+2] if 'fieldname118' in separado else None
        documentacion['trabajador2_id'] = separado[separado.index('fieldname124_url')+2] if 'fieldname124' in separado else None


        trabajador['nombre3'] = separado[separado.index('fieldname76')+2] if 'fieldname76' in separado else None
        trabajador['apellidopaterno3'] = separado[separado.index('fieldname77')+2] if 'fieldname77' in separado else None
        trabajador['apellidomaterno3'] = separado[separado.index('fieldname78')+2] if 'fieldname78' in separado else None
        trabajador['sexo3'] = separado[separado.index('fieldname147')+2] if 'fieldname147' in separado else None
        trabajador['correo3'] = separado[separado.index('fieldname120')+2] if 'fieldname120' in separado else None
        documentacion['trabajador3_id'] = separado[separado.index('fieldname125_url')+2] if 'fieldname125' in separado else None


        trabajador['nombre4'] = separado[separado.index('fieldname80')+2] if 'fieldname80' in separado else None
        trabajador['apellidopaterno4'] = separado[separado.index('fieldname81')+2] if 'fieldname81' in separado else None
        trabajador['apellidomaterno4'] = separado[separado.index('fieldname82')+2] if 'fieldname82' in separado else None
        trabajador['sexo4'] = separado[separado.index('fieldname148')+2] if 'fieldname148' in separado else None
        trabajador['correo4'] = separado[separado.index('fieldname121')+2] if 'fieldname121' in separado else None
        documentacion['trabajador4_id'] = separado[separado.index('fieldname126_url')+2] if 'fieldname126' in separado else None


        trabajador['nombre5'] = separado[separado.index('fieldname85')+2] if 'fieldname85' in separado else None
        trabajador['apellidopaterno5'] = separado[separado.index('fieldname86')+2] if 'fieldname86' in separado else None
        trabajador['apellidomaterno5'] = separado[separado.index('fieldname87')+2] if 'fieldname87' in separado else None
        trabajador['sexo5'] = separado[separado.index('fieldname149')+2] if 'fieldname149' in separado else None
        trabajador['correo5'] = separado[separado.index('fieldname122')+2] if 'fieldname122' in separado else None
        documentacion['trabajador5_id'] = separado[separado.index('fieldname127_url')+2] if 'fieldname127' in separado else None


        empleador['nombre'] = separado[separado.index('fieldname62')+2] if 'fieldname62' in separado else None
        empleador['apellidopaterno'] = separado[separado.index('fieldname63')+2] if 'fieldname63' in separado else None
        empleador['apellidomaterno'] = separado[separado.index('fieldname59')+2] if 'fieldname59' in separado else None
        empleador['sexo'] = separado[separado.index('fieldname64')+2] if 'fieldname64' in separado else None
        empleador['correo'] = separado[separado.index('fieldname117')+2] if 'fieldname117' in separado else None
        documentacion['empleador_id'] = separado[separado.index('fieldname66_url')+2] if 'fieldname66' in separado else None

        cita['hora_cita'] = pendulum.from_format(separado[separado.index('app_starttime_1')+2].strip().rstrip('\\'), "hh:mm A").time() if 'app_starttime_1' in separado else None
        cita['dia_cita'] = pendulum.from_format(separado[separado.index('app_date_1')+2], "DD/MM/YYYY").date() if 'app_date_1' in separado else None
        cita['id_cita'] = id
        cita['formid'] = formid
    else:
        trabajador = None
        empleador = None
        documentacion = None
        cita['Error'] == "tipo de persona erroneo en la cita"

    asesoria['trabajador'] = trabajador
    asesoria['empleador'] = empleador
    asesoria['documentacion'] = documentacion
    asesoria['cita'] = cita
    asesoria['correo'] = correo
    return asesoria



def get_next_registro():
    contador_registro, created = contadorRegistros.objects.get_or_create(id=1, defaults={'contador': 1})
    registro = contador_registro.contador
    return registro

def incrementar_contador_registro(num_incrementos):
    contador_registro, created = contadorRegistros.objects.get_or_create(id=1, defaults={'contador': 1})
    contador_registro.contador += num_incrementos
    contador_registro.save()

@csrf_protect
def registrar_ciudadano_QR(request):
    if request.method == 'POST':
        def get_post_data(field_name):
            return request.POST.getlist(field_name)[0] if request.POST.getlist(field_name) else ''

        def contar_campos_con_info(*campos):
            return sum(1 for campo in campos if campo.strip() != '')

        # Obtener datos del empleador
        nombre_empleador = get_post_data('nombre_empleador')
        sexo_empleador = get_post_data('sexo_empleador')
        correo_empleador = get_post_data('correo_empleador')
        curp_rfc_empleador = get_post_data('curp_rfc_empleador')
        municipio_empleador = get_post_data('municipio_empleador')
        tipo_persona_empleador = get_post_data('tipo_persona_empleador')
        documento_empleador_id = get_post_data('documento_empleador_id')
        documento_empleador_actac = get_post_data('documento_empleador_actac')
        documento_empleador_actar = get_post_data('documento_empleador_actar')
        documento_empleador_csf = get_post_data('documento_empleador_csf')

        # Obtener datos del trabajador
        nombre_trabajador = get_post_data('nombre_trabajador')
        sexo_trabajador = get_post_data('sexo_trabajador')
        correo_trabajador = get_post_data('correo_trabajador')
        curp_rfc_trabajador = get_post_data('curp_rfc_trabajador')
        municipio_trabajador = get_post_data('municipio_trabajador')
        tipo_persona_trabajador = get_post_data('tipo_persona_trabajador')
        documento_trabajador_id = get_post_data('documento_trabajador_id')
        documento_trabajador_curp = get_post_data('documento_trabajador_curp')
        documento_trabajador_comprobante = get_post_data('documento_trabajador_comprobante')
        

        # Obtener el siguiente número de registro
        siguiente_registro = get_next_registro()

        # Contar campos con información
        campos_empleador = [nombre_empleador, sexo_empleador, correo_empleador, curp_rfc_empleador, municipio_empleador, tipo_persona_empleador]
        campos_trabajador = [nombre_trabajador, sexo_trabajador, correo_trabajador, curp_rfc_trabajador, municipio_trabajador, tipo_persona_trabajador]

        campos_empleador_count = contar_campos_con_info(*campos_empleador)
        campos_trabajador_count = contar_campos_con_info(*campos_trabajador)

        # Crear y guardar documentos
        documentos_to_save = []
        if campos_empleador_count > 3:
            documentos_empleador = Documentos(
                empleador_id=documento_empleador_id,
                empleador_actac=documento_empleador_actac,
                empleador_actar=documento_empleador_actar,
                empleador_csf=documento_empleador_csf,
            )
            documentos_empleador.save()
            documentos_to_save.append(documentos_empleador)

        if campos_trabajador_count > 3:
            documentos_trabajador = Documentos(
                trabajador_id=documento_trabajador_id,
                trabajador_curp=documento_trabajador_curp,
                trabajador_comprobante=documento_trabajador_comprobante,
            )
            documentos_trabajador.save()
            documentos_to_save.append(documentos_trabajador)

        # Crear lista de objetos para guardar
        ciudadanos_to_save = []

        # Si el empleador tiene más de 3 campos con información, guardar su información
        if campos_empleador_count > 3:
            ciudadanos_to_save.append(ciudadanos(
                nombre=nombre_empleador,
                sexo=sexo_empleador,
                correo=correo_empleador,
                curp_rfc=curp_rfc_empleador,
                municipio=municipio_empleador,
                tipo_persona=tipo_persona_empleador,
                registro=siguiente_registro,
                codigo_ciudadano=generate_10_digit_code()
            ))

        # Si el trabajador tiene más de 3 campos con información, guardar su información
        if campos_trabajador_count > 3:
            ciudadanos_to_save.append(ciudadanos(
                nombre=nombre_trabajador,
                sexo=sexo_trabajador,
                correo=correo_trabajador,
                curp_rfc=curp_rfc_trabajador,
                municipio=municipio_trabajador,
                tipo_persona=tipo_persona_trabajador,
                registro=siguiente_registro,
                codigo_ciudadano=generate_10_digit_code()
            ))

        # Guardar los datos en el modelo Ciudadanos
        try:
            if ciudadanos_to_save:
                for ciudadano in ciudadanos_to_save:
                    ciudadano.save()

                # Incrementar el contador
                incrementar_contador_registro(1)

                return HttpResponseRedirect(reverse('auto_turno') + f'?registro={siguiente_registro}')
            else:
                # Si no hay datos válidos para guardar
                return render(request, 'recepcion/Registrar_con_QR.html', {'mensaje': 'No hay suficiente información para registrar'})

        except IntegrityError as e:
            print(f'Error al registrar: {e}')
            return render(request, 'recepcion/Registrar_con_QR.html', {'mensaje': 'Error al registrar'})

    return JsonResponse({'success': False})







def filtroRatificaciones(data):
    respuesta = {}
    data = data[0]
    data_separado = data['posted_data'] if data is not None else 'error'
    if data_separado == 'error':
        respuesta['Error'] = 'tipo de persona erroneo en la cita'
        return respuesta
    data_separado = data['posted_data']
    id = data['id']
    formid = data['formid']
    separado = data_separado.split('"')
    tipo_persona = separado[separado.index('fieldname3')+2]
    trabajador = {}
    empleador = {}
    documentacion = {}
    cita = {}
    rati = {}

    if tipo_persona == 'Ratificación con convenio (Persona Física Empleadora)':
        trabajador['nombre'] = separado[separado.index('fieldname8')+2] if 'fieldname8' in separado else None
        trabajador['apellidopaterno'] = separado[separado.index('fieldname9')+2] if 'fieldname9' in separado else None
        trabajador['apellidomaterno'] = separado[separado.index('fieldname10')+2] if 'fieldname10' in separado else None
        trabajador['sexo'] = separado[separado.index('fieldname13')+2] if 'fieldname13' in separado else None
        documentacion['trabajador_id'] = separado[separado.index('fieldname12_url')+2] if 'fieldname12'in separado else None
        cita['hora_cita'] = pendulum.from_format(separado[separado.index('app_starttime_1')+2].strip().rstrip('\\'), "HH:mm").time() if 'app_starttime_1' in separado else None
        cita['dia_cita'] = pendulum.from_format(separado[separado.index('app_date_1')+2], "MM/DD/YYYY").date() if 'app_date_1' in separado else None
        cita['id_cita'] = id
        empleador['nombre'] = separado[separado.index('fieldname25')+2] if 'fieldname25' in separado else None
        empleador['apellidopaterno'] = separado[separado.index('fieldname26')+2] if 'fieldname26' in separado else None
        empleador['apellidomaterno'] = separado[separado.index('fieldname27')+2] if 'fieldname27' in separado else None
        empleador['sexo'] = separado[separado.index('fieldname107')+2] if 'fieldname107' in separado else None
        documentacion['empleador_id'] = separado[separado.index('fieldname31_url')+2] if 'fieldname31' in separado else None
    elif tipo_persona == 'Ratificación con convenio (Persona Jurídica Empleadora)':
        trabajador['nombre'] = separado[separado.index('fieldname70')+2] if 'fieldname70' in separado else None
        trabajador['apellidopaterno'] = separado[separado.index('fieldname71')+2] if 'fieldname71' in separado else None
        trabajador['apellidomaterno'] = separado[separado.index('fieldname72')+2] if 'fieldname72' in separado else None
        trabajador['sexo'] = separado[separado.index('fieldname102')+2] if 'fieldname102' in separado else None
        documentacion['trabajador_id'] = separado[separado.index('fieldname73_url')+2] if 'fieldname73'in separado else None
        trabajador['nombre2'] = separado[separado.index('fieldname76')+2] if 'fieldname76' in separado else None
        trabajador['apellidopaterno2'] = separado[separado.index('fieldname77')+2] if 'fieldname77' in separado else None
        trabajador['apellidomaterno2'] = separado[separado.index('fieldname78')+2] if 'fieldname78' in separado else None
        trabajador['sexo2'] = separado[separado.index('fieldname103')+2] if 'fieldname103' in separado else None
        documentacion['trabajador2_id'] = separado[separado.index('fieldname79_url')+2] if 'fieldname79'in separado else None
        trabajador['nombre3'] = separado[separado.index('fieldname82')+2] if 'fieldname82' in separado else None
        trabajador['apellidopaterno3'] = separado[separado.index('fieldname83')+2] if 'fieldname83' in separado else None
        trabajador['apellidomaterno3'] = separado[separado.index('fieldname84')+2] if 'fieldname84' in separado else None
        trabajador['sexo3'] = separado[separado.index('fieldname104')+2] if 'fieldname104' in separado else None
        documentacion['trabajador3_id'] = separado[separado.index('fieldname85_url')+2] if 'fieldname85'in separado else None
        trabajador['nombre4'] = separado[separado.index('fieldname88')+2] if 'fieldname88' in separado else None
        trabajador['apellidopaterno4'] = separado[separado.index('fieldname89')+2] if 'fieldname89' in separado else None
        trabajador['apellidomaterno4'] = separado[separado.index('fieldname90')+2] if 'fieldname90' in separado else None
        trabajador['sexo4'] = separado[separado.index('fieldname105')+2] if 'fieldname105' in separado else None
        documentacion['trabajador4_id'] = separado[separado.index('fieldname91_url')+2] if 'fieldname91'in separado else None
        trabajador['nombre5'] = separado[separado.index('fieldname94')+2] if 'fieldname94' in separado else None
        trabajador['apellidopaterno5'] = separado[separado.index('fieldname95')+2] if 'fieldname95' in separado else None
        trabajador['apellidomaterno5'] = separado[separado.index('fieldname96')+2] if 'fieldname96' in separado else None
        trabajador['sexo5'] = separado[separado.index('fieldname106')+2] if 'fieldname106' in separado else None
        documentacion['trabajador5_id'] = separado[separado.index('fieldname97_url')+2] if 'fieldname97'in separado else None
        empleador['nombre'] = separado[separado.index('fieldname62')+2] if 'fieldname62' in separado else None
        empleador['apellidopaterno'] = separado[separado.index('fieldname63')+2] if 'fieldname63' in separado else None
        empleador['apellidomaterno'] = separado[separado.index('fieldname64')+2] if 'fieldname64' in separado else None
        empleador['sexo'] = separado[separado.index('fieldname65')+2] if 'fieldname65' in separado else None
        documentacion['empleador_id'] = separado[separado.index('fieldname67_url')+2] if 'fieldname67'in separado else None
        documentacion['empleador_csf'] = separado[separado.index('fieldname48_url')+2] if 'fieldname48'in separado else None
        documentacion['empleador_actac'] = separado[separado.index('fieldname49_url')+2] if 'fieldname49'in separado else None
        documentacion['empleador_actar'] = separado[separado.index('fieldname50_url')+2] if 'fieldname50'in separado else None
        cita['hora_cita'] = pendulum.from_format(separado[separado.index('app_starttime_1')+2], "HH:mm").time() if 'app_starttime_1' in separado else None
        cita['dia_cita'] = pendulum.from_format(separado[separado.index('app_date_1')+2], "MM/DD/YYYY").date() if 'app_date_1' in separado else None
        cita['id_cita'] = id
        cita['formid'] = formid
    else:
        trabajador = None
        empleador = None
        documentacion = None
        cita['Error'] == "tipo de persona erroneo en la cita"

    rati['trabajador'] = trabajador
    rati['empleador'] = empleador
    rati['documentacion'] = documentacion
    rati['cita'] = cita
    return rati


########################################################  funciones para el turnero de asesorias y pantalla asesor  ###############################################################################################


#renderiza el template de dasboard / pantalla de turnos
def asesorias_dashboard(request):
    try:
        turno = turnos.objects.filter(Q(status = "PEN") | Q(status = "PRO"),Q(area=3)).values('id','turno','status' 'mesa')
        if not turno:
            return render(request, 'asesorias/dashboard.html', {})
        else: 
            return render(request, 'asesorias/dashboard.html', {'turnos': turno})
    except turnos.DoesNotExist:  
        return render(request, 'asesorias/dashboard.html', {})
    except Exception as e:
        return render(request, 'asesorias/dashboard.html', {'error': str(e)})   
    

# renderiza el template de asesor
@login_required
def asesor(request):
    numeros_mesa = range(1, 21)
    username = request.user.username
    return render(request, 'asesorias/asesor.html',  {'numeros_mesa': numeros_mesa, 'username' : username})



#funcion para obtener los turnos unicamente del area de asesoria o area 3
def obtener_turnos(request):
    turno = turnos.objects.filter(Q(status = "PEN") | Q(status = "NOT") | Q(status = "PRO"), Q(area=3),).values('id', 'turno', 'status', 'notificacion','mesa')
    turno_list = list(turno)
    return JsonResponse(turno_list, safe=False) 


#websocket
def actualizar_turnos():
    channel_layer = get_channel_layer()
    turnos = obtener_turnos()  
    async_to_sync(channel_layer.group_send)(
        "turnos",
        {
            "type": "send_turnos",
            "turnos": turnos,
        },
    )


#funcion que muestra la cantidad de turnos pendientes al asesor
def verTurnos(request):
    turno = turnos.objects.filter(status = "PEN",area=3).values('id')
    turnos_list = list(turno)
    return JsonResponse(turnos_list, safe=False)


# funcion para llamar un turno que esta pendiente
def llamar_turno(request):
    mesa_activa = request.GET.get('mesa')

    if mesa_activa == 'Sin Mesa':
        return JsonResponse({'error': 'No puedes llamar turnos sin mesa.'}, status=404)

    turno_activo = turnos.objects.filter(Q(status='PRO') | Q(status='NOT'), Q(area=3), mesa=mesa_activa).first()

    if turno_activo and turno_activo.registro:
        ciudadanos_asociados = ciudadanos.objects.filter(registro=turno_activo.registro).select_related()
        datos_ciudadanos = []

    
        if ciudadanos_asociados.exists():
            for ciudadano in ciudadanos_asociados:
                if 'Fuente:' not in ciudadano.nombre:
                    solicitud = Solicitud.objects.filter(id_ciudadano = ciudadano.id, registro = turno_activo.registro).last()
                    if solicitud is None:
                        asistencia = True
                    else:
                        asistencia = solicitud.asistencia
                    if asistencia:
                        testigos_list = testigos.objects.filter(codigo_ciudadano=ciudadano.codigo_ciudadano)

                        # Inicializa los documentos como None
                        documento_3 = None
                        documento_4 = None
                        documento_5 = None
                        documento_6 = None

                        # Si hay testigos, intenta asignar los documentos
                        for testigo in testigos_list:
                            if testigo.documento_3:
                                documento_3 = testigo.documento_3.url
                            if testigo.documento_4:
                                documento_4 = testigo.documento_4.url
                            if testigo.documento_5:
                                documento_5 = testigo.documento_5.url
                            if testigo.documento_6:
                                documento_6 = testigo.documento_6.url

                        datos_ciudadanos.append({
                            'id_ciudadano': ciudadano.id,
                            'nombre': ciudadano.nombre,
                            'asistencia' : asistencia,
                            'documento_1': ciudadano.documento_1.url if ciudadano.documento_1 else None,
                            'documento_2': ciudadano.documento_2.url if ciudadano.documento_2 else None,
                            'documento_3': documento_3,
                            'documento_4': documento_4,
                            'documento_5': documento_5,
                            'documento_6': documento_6,
                        })
        else:
            turno_activo.status = 'CAN'
            turno.activo.save()  
            return JsonResponse({'error': f'se te asigno el turno {turno_activo.turno} pero este fue cancelado por recepcion, llama un turno nuevo.'}, status=404)

        turno_data = {
            'hora_inicio': turno_activo.hora_notificacion,
            'turno' : turno_activo,
            'id': turno_activo.id,
            'turno': turno_activo.turno,
            'status': turno_activo.status,
            'registro': turno_activo.registro,
            'area': turno_activo.area,
            'datosCiudadanos': datos_ciudadanos
        }

        return JsonResponse(turno_data)
    else:
        turno = turnos.objects.filter(Q(status='PEN', preferente=True, area=3)).order_by('id').first()
        if not turno:
            turno = turnos.objects.filter(Q(status='PEN', preferente=False, area=3)).order_by('id').first()

        if turno and turno.registro:
            ciudadanos_asociados = ciudadanos.objects.filter(registro=turno.registro)
            datos_ciudadanos = []

            if ciudadanos_asociados.exists():
                for ciudadano in ciudadanos_asociados:
                    if 'Fuente:' not in ciudadano.nombre:
                        
                        solicitud = Solicitud.objects.filter(id_ciudadano = ciudadano.id, registro= turno.registro).last()
                        
                        if solicitud is None:
                            asistencia = True
                        else:
                            
                            asistencia = solicitud.asistencia
                        if asistencia:
                            testigos_list = testigos.objects.filter(registro=ciudadano.registro)

                            documento_3 = None
                            documento_4 = None
                            documento_5 = None
                            documento_6 = None

                            for testigo in testigos_list:
                                if testigo.documento_3:
                                    documento_3 = testigo.documento_3.url
                                if testigo.documento_4:
                                    documento_4 = testigo.documento_4.url
                                if testigo.documento_5:
                                    documento_5 = testigo.documento_5.url
                                if testigo.documento_6:
                                    documento_6 = testigo.documento_6.url

                            datos_ciudadanos.append({
                                'id_ciudadano': ciudadano.id,
                                'nombre': ciudadano.nombre,
                                'asistencia' : asistencia,
                                'documento_1': ciudadano.documento_1.url if ciudadano.documento_1 else None,
                                'documento_2': ciudadano.documento_2.url if ciudadano.documento_2 else None,
                                'documento_3': documento_3,
                                'documento_4': documento_4,
                                'documento_5': documento_5,
                                'documento_6': documento_6,
                            })
            else:
                
                turno.status = 'CAN'
                turno.save()
                return JsonResponse({'error': f'se te asigno el turno {turno.turno} pero este fue cancelado por recepcion, llama un turno nuevo.'}, status=404)
                

            turno_data = {
                'hora_inicio' : turno.hora_notificacion,
                'id': turno.id,
                'area': turno.area if turno.area else None,
                'turno': turno.turno,
                'status': turno.status,
                'registro': turno.registro,
                'datosCiudadanos': datos_ciudadanos
            }
        
            return JsonResponse(turno_data)
        else:
            return JsonResponse({'error': 'No se encontraron turnos'}, status=404)

        


@csrf_exempt
def validar_turnos_abiertos(request):
    mesa_activa = request.GET.get('mesa')
    turno_activo = turnos.objects.filter(status='PRO', mesa=mesa_activa, area=3).first()
    if turno_activo:
        ciudadanos_en_turno = ciudadanos.objects.filter(registro=turno_activo.registro)
        nombres_ciudadanos = [ciudadano.nombre for ciudadano in ciudadanos_en_turno]
        turno_data = {
            'hora_inicio': turno_activo.hora_inicio_turno,
            'id': turno_activo.id,
            'turno': turno_activo.turno,
            'status': turno_activo.status,
            'nombreCiudadano': nombres_ciudadanos  
        }
        return JsonResponse(turno_data)
    else:
        return JsonResponse({'turno': 'none'})
    


@csrf_exempt
def asistir_conciliador(request):
    if request.method == 'POST':
        try:
            user = request.POST.get('user_id')
            audiencia = request.POST.get('audiencia')
            print("usuario : ", user)
            print("audiencia : ", audiencia)
            if user:
                usuario = User.objects.get(id=user)
                audiencia_asistida = AudienciaAPI.objects.get(expediente = audiencia)
                audiencia_asistida.auxiliar = usuario.get_full_name()
                audiencia_asistida.atendiendo = True
                audiencia_asistida.save()
                messages.success(request,"asistencia actualizada")
                return HttpResponseRedirect(reverse('audiencias_auxiliares_api'))
            else:
                messages.success(request,"no se proporciono un usuario")
                return HttpResponseRedirect(reverse('audiencias_auxiliares_api'))
        except User.DoesNotExist:
            messages.success(request,"no existe el usuario") 
            return HttpResponseRedirect(reverse('audiencias_auxiliares_api')) 
        except AudienciaAPI.DoesNotExist:
            messages.success(request,"la audiencia no existe") 
            return HttpResponseRedirect(reverse('audiencias_auxiliares_api'))  
        
        
@csrf_exempt
def terminar_asistencia(request):
    if request.method == 'POST':
        try:
            user = request.POST.get('user_id')
            audiencia = request.POST.get('audiencia')
            if user:
                usuario = User.objects.get(id=user)
                audiencia_asistida = AudienciaAPI.objects.get(expediente = audiencia)
                audiencia_asistida.auxiliar = usuario.get_full_name()
                audiencia_asistida.atendiendo = False
                audiencia_asistida.asistencia = False
                audiencia_asistida.save()
                messages.success(request,"asistencia concluida")
                return HttpResponseRedirect(reverse('audiencias_auxiliares_api'))
            else:
                messages.error(request,"No se proporciono usuario")
                return HttpResponseRedirect(reverse('audiencias_auxiliares_api'))
        except User.DoesNotExist:
            messages.error(request,"No existe el usuario")
            return HttpResponseRedirect(reverse('audiencias_auxiliares_api'))  
        except AudienciaAPI.DoesNotExist:
            messages.error(request,"No existe la audiencia")
            return HttpResponseRedirect(reverse('audiencias_auxiliares_api')) 
    else:
        messages.error(request,"Bad request")
        return HttpResponseRedirect(reverse('audiencias_auxiliares_api'))



@csrf_exempt
def asistir_asesor(request):
    if request.method == 'POST':
        try:
            user = request.POST.get('user_id')
            mesa_name = request.POST.get('mesa')
            
            if user and mesa_name:
                usuario = User.objects.get(id=user)
                mesa_id = mesa.objects.get(mesa=mesa_name)
                mesa_asistida = AyudaAsesor.objects.get(mesa = mesa_id)
                mesa_asistida.auxiliar = usuario.get_full_name()
                mesa_asistida.atendiendo = True
                mesa_asistida.save()
                messages.success(request,"asistencia actualizada")
                return HttpResponseRedirect(reverse('auxiliares asesoria'))
            else:
                messages.success(request,"no se proporciono un usuario")
                return HttpResponseRedirect(reverse('auxiliares asesoria'))
        except User.DoesNotExist:
            messages.success(request,"no existe el usuario") 
            return HttpResponseRedirect(reverse('auxiliares asesoria')) 
        except AudienciaAPI.DoesNotExist:
            messages.success(request,"la audiencia no existe") 
            return HttpResponseRedirect(reverse('auxiliares asesoria'))  
        
        
@csrf_exempt
def terminar_asistencia_asesor(request):
    if request.method == 'POST':
        try:
            user = request.POST.get('user_id')
            mesa_name = request.POST.get('mesa')
            if user and mesa_name:
                usuario = User.objects.get(id=user)
                mesa_id = mesa.objects.get(mesa=mesa_name)
                audiencia_asistida = AyudaAsesor.objects.get(mesa = mesa_id)
                audiencia_asistida.auxiliar = usuario.get_full_name()
                audiencia_asistida.atendiendo = False
                audiencia_asistida.activo = False
                audiencia_asistida.save()
                messages.success(request,"asistencia concluida")
                return HttpResponseRedirect(reverse('auxiliares asesoria'))
            else:
                messages.error(request,f"No se proporciono usuario: {user} o mesa: {mesa_name}")
                return HttpResponseRedirect(reverse('auxiliares asesoria'))
        except User.DoesNotExist:
            messages.error(request,"No existe el usuario")
            return HttpResponseRedirect(reverse('auxiliares asesoria'))  
        except AudienciaAPI.DoesNotExist:
            messages.error(request,"No existe la audiencia")
            return HttpResponseRedirect(reverse('auxiliares asesoria')) 
    else:
        messages.error(request,"Bad request")
        return HttpResponseRedirect(reverse('auxiliares asesoria'))


@csrf_exempt
def ayuda_auxiliares_asesoria(request):
    if request.method == 'POST':
        try:
            asesor = request.POST.get('asesor')
            mensaje = request.POST.get('mensaje')

            if asesor and mensaje:
                es_user = User.objects.get(id=asesor)
                es_mesa = mesa.objects.get(user=es_user)
                fecha = pendulum.now().date()
                hora = pendulum.now().time()
                if es_user and es_mesa:
                    ayuda_asesor, creado = AyudaAsesor.objects.update_or_create(
                        asesor=es_user,
                        defaults={
                            'mensaje': mensaje,
                            'mesa': es_mesa,
                            'atendiendo': False,
                            'activo': True,
                            'fecha' : fecha,
                            'hora': hora
                        }
                    )
                else:
                    messages.error(request, 'No fue posible pedir ayuda.')
            else:
                messages.error(request, 'Faltan datos requeridos para la solicitud.')
            
            return HttpResponseRedirect(reverse('asesor'))

        except Exception as e:
            messages.error(request, f'Error al procesar la solicitud: {str(e)}')
            return HttpResponseRedirect(reverse('asesor'))
    else:
        messages.error(request, "Método no permitido")
        return HttpResponseRedirect(reverse('asesor'))
    

def ver_solicitud_ayuda(request):
    asesor = request.GET.get('user_id')
    usuario = None
    if asesor and asesor != 'None':
        print("entra a buscar el user")
        try:
            usuario = User.objects.get(id=asesor)
        except User.DoesNotExist:
            return JsonResponse({"message": "El usuario no existe."})
    try:
        if usuario:
            solicitudes = AyudaAsesor.objects.filter(activo=True, asesor=usuario)
        else:
            solicitudes = AyudaAsesor.objects.filter(activo=True)

        if solicitudes.exists():
            lista = []
            for solicitud in solicitudes:
                mesa_name = solicitud.mesa.mesa
                nombre = solicitud.asesor.get_full_name()
                        
                lista.append({
                    'id': solicitud.id,  
                    'mensaje': solicitud.mensaje,  
                    'mesa': mesa_name, 
                    'atendiendo': solicitud.atendiendo,
                    'activo': solicitud.activo,
                    'nombre': nombre,
                    'auxiliar': solicitud.auxiliar,
                    'fecha': solicitud.fecha,
                    'hora': solicitud.hora
                })
            return JsonResponse(lista, safe=False)
        else:
            return JsonResponse({"message": "No hay solicitudes."})
    except Exception as e:
        return JsonResponse({"message": "Error al obtener las audiencias", "error": str(e)})


def vista_auxiliares_asesoria(request):
    try:
        solicitudes_ayuda = AyudaAsesor.objects.filter(activo=True).select_related('asesor', 'mesa').all()
        lista = []
        contador_proceso = 0
        contador_pendientes = 0

        for solicitud in solicitudes_ayuda:
            if solicitud.activo and solicitud.atendiendo:
                contador_proceso += 1
            elif solicitud.activo and not solicitud.atendiendo:
                contador_pendientes +=1

            mesa_asesor = solicitud.mesa.mesa  
            nombre_asesor = solicitud.asesor.get_full_name()

            solicitud_dict = {
                'id' : solicitud.id,
                'mesa': mesa_asesor,
                'nombre': nombre_asesor,
                'mensaje': solicitud.mensaje,
                'activo' : solicitud.activo,
                'atendiendo': solicitud.atendiendo,
                'auxiliar' : solicitud.auxiliar,
                'hora' : solicitud.hora,
                'fecha' : solicitud.fecha
            }
            lista.append(solicitud_dict)
        print(contador_pendientes)
        print(contador_proceso)
        return render(request, 'asesorias/auxiliares.html', {'solicitudes': lista, 'pendientes':contador_pendientes, 'proceso': contador_proceso})
    except AyudaAsesor.DoesNotExist:
        return render(request, 'asesorias/auxiliares.html')
    


@csrf_exempt
def asistencia_auxiliares(request, pk):
    if request.method == 'POST':
        try:
            conciliador = request.POST.get('conciliador')
            mensaje = request.POST.get('mensaje')
            audiencia = request.POST.get('audiencia_id')

            print("La audiencia:", audiencia)

            if conciliador and mensaje and audiencia:
                es_user = User.objects.filter(id=conciliador).first()
                if es_user:
                    actualizar_audiencia = AudienciaAPI.objects.get(id=audiencia)
                    if actualizar_audiencia:
                        print("La audiencia que se encontró:", actualizar_audiencia)
                        actualizar_audiencia.mensaje = mensaje
                        actualizar_audiencia.asistencia = True
                        actualizar_audiencia.save()
                        messages.success(request, 'Ayuda requerida exitosamente.')
                    else:
                        messages.error(request, 'No se encontró la audiencia especificada.')
                else:
                    messages.error(request, 'No fue posible pedir ayuda.')
            else:
                messages.error(request, 'Faltan datos requeridos para la solicitud.')
            return HttpResponseRedirect(reverse('celebrar_audiencia', args=[pk]))
        except Exception as e:
            messages.error(request, f'Error al procesar la solicitud: {str(e)}')
            return HttpResponseRedirect(reverse('celebrar_audiencia', args=[pk]))
    else:
        messages.error(request, "Método no permitido")
        return HttpResponseRedirect(reverse('celebrar_audiencia', args=[pk]))



    

def ver_asistencias(request):
    try:
        audiencias_para_asistir = AudienciaAPI.objects.filter(asistencia=True).values()
        lista_audiencias = list(audiencias_para_asistir) 
        return JsonResponse({"audiencias": lista_audiencias}, safe=False)
    except Exception as e:
        return JsonResponse({"message": "Error al obtener las audiencias", "error": str(e)})




@csrf_exempt
def crear_mesa_ayuda(request, pk):
    print("Inicia a trabajar la vista de mesa de ayuda")
    if request.method == 'POST':
        try:
            expediente = request.POST.get("expediente")
            audiencia = request.POST.get("audiencia")
            solicitud = request.POST.get("solicitud")
            peticion = request.POST.get("peticion")
            mensaje = request.POST.get("mensaje")
            conciliador = request.POST.get("user_id")
            solicitantes = request.POST.get("nombres_solicitantes")
            citados = request.POST.get("nombres_citados")

            print("Entramos a la creación de la mesa de ayuda")

            if expediente and audiencia and solicitud and peticion and conciliador:
                ahora = pendulum.now()
                usuario = User.objects.get(id=conciliador)
                print("Están todos los parámetros completos")
                
                # Crear la entrada en la base de datos
                nueva_mesa = mesadeayuda(
                    expediente=expediente,
                    audiencia=audiencia,
                    solicitud=solicitud,
                    peticion=peticion,
                    mensaje=mensaje,
                    fecha=ahora,
                    status='PEN',
                    user=usuario
                )
                nueva_mesa.save()

                print("Comienza a enviar la solicitud a la API")
                
                # Cuerpo del request para la API
                body = {
                    "expediente": expediente,
                    "audiencia": audiencia,
                    "solicitud": solicitud,
                    "peticion": peticion,
                    "mensaje": mensaje,
                    "conciliador": conciliador,
                    "nombres_solicitantes": solicitantes,
                    "nombres_citados": citados,
                    "subject": f"SINACOL, solicitud de {usuario.get_full_name()}, ticket numero: {nueva_mesa.id} "
                }

                # URL de la API externa
                url = 'https://citas.ccljalisco.gob.mx/api/mesaAyuda'

                # Enviar la solicitud POST a la API
                response = requests.post(url, json=body, verify=False)

                # Manejo de respuesta de la API
                if response.status_code == 200:
                    print("Solicitud enviada correctamente a la API")
                    messages.success(request, 'Mesa de ayuda creada y solicitud enviada exitosamente.')
                else:
                    print(f"Error en la petición a la API: {response.text}")
                    messages.error(request, f'Error al enviar la solicitud a la API: {response.text}')

                return HttpResponseRedirect(reverse('celebrar_audiencia', args=[pk]))

            else:
                messages.error(request, 'Faltan datos requeridos para crear la mesa de ayuda.')
                return HttpResponseRedirect(reverse('celebrar_audiencia', args=[pk]))
        except Exception as e:
            messages.error(request, f'Error al crear la mesa de ayuda: {str(e)}')
            return HttpResponseRedirect(reverse('celebrar_audiencia', args=[pk]))
    else:
        messages.error(request, 'Método no permitido.')
        return HttpResponseRedirect(reverse('celebrar_audiencia', args=[pk]))


            
def validar_mesa_ayuda(request):
    usuario = request.GET.get('user_id')
    usuario_validado = User.objects.get(id=usuario)

    print(usuario_validado)

    if usuario_validado:
        mesa_ayuda = mesadeayuda.objects.filter(user = usuario_validado)
        tickets_activos = []

        for mesa in mesa_ayuda:
            if mesa.status == 'PEN':
                tickets_activos.append(mesa.expediente)

        return JsonResponse({'mesas' : tickets_activos}) 
    else:
        return JsonResponse({"message" : "el usuario no existe"})




def validar_turnos_proceso(request):
    usuario = request.GET.get('user')
    turnos_del_usuario = turnos.objects.filter(status='PRO', usuario=usuario, area=1)
    
    if turnos_del_usuario.exists():
        turnos_activos = []
        ahora = pendulum.now()

        for turno in turnos_del_usuario:
            diferencia_minutos = int((ahora - turno.hora_notificacion).total_seconds() / 60)
            
            turnos_activos.append({
                'turno': turno.turno,

                'status': turno.status,
                'diferencia_minutos': diferencia_minutos
            })
        return JsonResponse(turnos_activos, safe=False)
    else:
        return JsonResponse([], safe=False)
    



def conciliadores_disponibles_notificacion(request):
    usuario = request.GET.get('user')
    if usuario:
        try:
            es_coordinador = User.objects.get(id=usuario)
            
            if es_coordinador.groups.filter(id=15).exists():
                conciliadores = User.objects.filter(groups = 5)
                contador = 0
                for conciliador in conciliadores:
                    tiene_turno = turnos.objects.filter(usuario=conciliador, status='PRO')
                    if not tiene_turno:
                        contador += 1
                turnos_pendientes = turnos.objects.filter(area = 1, status = 'PEN').count()
                return JsonResponse({"conciliadores": contador, "turnos" : turnos_pendientes})
            else:
                return JsonResponse({})
        except User.DoesNotExist:
            JsonResponse({"error" : "el usuario no existe"})
    else:
        return JsonResponse({"error" : "no es usuario"})        



def validar_audiencias_proceso(request): 
    usuario = request.GET.get('user')
    
    try: 
        es_conciliador = User.objects.filter(id=usuario, groups__id=5).exists()
        conciliador = User.objects.get(id=usuario)
        if es_conciliador:
            print("el conciliador: ",es_conciliador, conciliador)
            turnos_del_usuario = turnos.objects.filter(status='PRO', usuario=conciliador, area=1).first()
            
            if turnos_del_usuario:
                print("el conciliador tiene turnos")
                return JsonResponse({"message": "si audiencia"})
            else:
                ahora = pendulum.now()  
                fecha_actual = ahora.to_date_string()  
                hora_inicio = ahora.start_of('hour')  
                hora_fin = hora_inicio.add(hours=1)

                audiencia = Audiencia.objects.filter(
                    user=usuario,
                    fecha_audiencia=fecha_actual,
                    hora_audiencia__gte=hora_inicio.time(),
                    hora_audiencia__lt=hora_fin.time()
                ).first()
                #si hay audiencia
                if audiencia:
                    print("el conciliador tiene audienciasa")
                    #si ya esta concluida
                    if audiencia.hora_fin_audiencia:
                        print("la de esta hora ya termino")
                        #si termino media hora antes y aun quedan 20 minutos
                        if audiencia.status_audiencia=='Concluida' and audiencia.hora_fin_audiencia <= hora_fin.subtract(minutes=25) and ahora <= hora_fin.subtract(minutes=20):
                            print("y tiene tiempo para una rati")
                            return JsonResponse({"message": "si notificar", "audiencia_id": audiencia.id})
                        else:
                            return JsonResponse({})
                    #si no es asi entonces, ver si esta iniciada
                    elif audiencia.hora_inicio_audiencia or audiencia.status_audiencia == 'En audiencia':
                        print("tiene audiencia en proceso")
                        return JsonResponse({})
                    else:
                        hora_audiencia_datetime = pendulum.datetime(
                                    ahora.year, ahora.month, ahora.day,
                                    audiencia.hora_audiencia.hour, audiencia.hora_audiencia.minute, tz=ahora.tz
                                )

                        minutos_transcurridos = int((ahora - hora_audiencia_datetime).total_seconds() / 60)
                        print("tiene audiencia sin empezar")

                        if minutos_transcurridos >= 7 and audiencia.status_audiencia=='Pendiente':
                            print("ya pasaron 7 minutos") 
                            if ahora < hora_fin.subtract(minutes=20):
                                print("y es menor a 40")       
                                return JsonResponse({"message": "si notificar", "audiencia_id": audiencia.id})
                            else:
                                return JsonResponse({})
                        else:
                            print("no cumple ninguna y no esta en el rango de 7 a 40 minutos")
                            return JsonResponse({})
                else:            
                    print("retorna el general")   
                    return JsonResponse({"message": "si notificar"})    
        else:
            return JsonResponse({"message": "Usuario no es conciliador"})
    
    except User.DoesNotExist:
        return JsonResponse({"message": "Usuario no existe"})



@csrf_exempt
def justificar_inactividad(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        audiencia = data.get('audiencia')
        user = data.get('user')
        mensaje = data.get('mensaje')
        print(audiencia)

        if user and mensaje and audiencia:
            if audiencia == "none":
                print("none en la audiencia")
                audiencia = None
            ahora = pendulum.now()
            try:
                audiencia_actual = Audiencia.objects.get(id=audiencia)
                if audiencia_actual:
                    audiencia = audiencia_actual
            except Audiencia.DoesNotExist:
                audiencia = None
            conciliador = User.objects.get(id=user)
            if conciliador:
                user = conciliador
            justificacion = justificaciones(audiencia= audiencia, user=user, mensaje=mensaje, fecha=ahora)
            justificacion.save()
            return JsonResponse({"message": "justificacion guardada"})
        else:
            return JsonResponse({"error" : "faltan datos"})
    else:
        return JsonResponse({"error": "metodo no permitido"})
        

        

def validar_si_justifico(request):
    user_id = request.GET.get('user')
    audiencia_id = request.GET.get('audiencia')
    ahora = pendulum.now()
    hora_inicio = ahora.start_of('hour')
    hora_fin = hora_inicio.add(hours=1)
    print (hora_inicio, " y ", hora_fin)
    if user_id and audiencia_id:
        try:
            conciliador = User.objects.get(id=user_id, groups__id=5)
            print(conciliador)
            audiencia = Audiencia.objects.get(id=audiencia_id)
            try:
                motivo = justificaciones.objects.get(audiencia=audiencia, user=conciliador)
                respuesta = f"El conciliador {conciliador.get_full_name()} está inactivo en el turnero, motivo: {motivo.mensaje}"
                return JsonResponse({"message": respuesta})
            except justificaciones.DoesNotExist:
                return JsonResponse({"respuesta": "No ha justificado"})
        
        except (User.DoesNotExist, Audiencia.DoesNotExist):
            return JsonResponse({"error": "Conciliador o audiencia no encontrados"})
    elif user_id:
        try:
            conciliador = User.objects.get(id=user_id, groups__id=5)
            try:
                motivo = justificaciones.objects.get(user=conciliador, fecha__gte=hora_inicio, fecha__lt=hora_fin)
                respuesta = f"El conciliador {conciliador.get_full_name()} está inactivo en el turnero, motivo: {motivo.mensaje}"
                return JsonResponse({"message": respuesta})
            except justificaciones.DoesNotExist:
                return JsonResponse({"respuesta": "No ha justificado"})
        
        except (User.DoesNotExist, Audiencia.DoesNotExist):
            return JsonResponse({"error": "Conciliador o audiencia no encontrados"})

    else:
        return JsonResponse({"error": "Faltan datos"})





# funcion para cambiar el status de un turno
@csrf_exempt
@require_http_methods(["PATCH"])
def cambiar_status(request):
    if request.method == 'PATCH':
        data = json.loads(request.body)
        turnoactual = data.get('turno_id')
        registro = data.get('registro')
        nuevo_status = data.get('nuevoStatus')
        nueva_mesa = data.get('mesa')
        user_nuevo = data.get('user')
        notificacion_nueva = data.get('notificacion')
        
        if turnoactual and nuevo_status and nueva_mesa:
            try:
                cambio_status = turnos.objects.get(id=turnoactual)
                if cambio_status:
                    cambio_status.status = nuevo_status
                    cambio_status.mesa = nueva_mesa
                    user_instance = User.objects.get(id=user_nuevo)
                    if user_instance:
                        
                        cambio_status.usuario = user_instance
                    
                    
                    if nuevo_status == 'NOT':
                        cambio_status.hora_notificacion = timezone.now()
                        if notificacion_nueva:
                            cambio_status.notificacion = notificacion_nueva
                    elif nuevo_status == 'PRO':
                        cambio_status.hora_inicio_turno = timezone.now()
                    elif nuevo_status == 'FIN' or nuevo_status == 'CAN':
                        cambio_status.hora_fin_turno = timezone.now()
                    cambio_status.save()    
                    return JsonResponse({'message': 'Turno Actualizado Correctamente'})
                else:
                    return JsonResponse({'error': 'Registro no encontrado'}, status=404)
            except Exception as e:
                return JsonResponse({'error': f'Error al cambiar el status py: {e}', 'status': nuevo_status}, status=500)
        elif turnoactual and registro and nuevo_status:
            try:
                cambio_status = turnos.objects.filter(turno=turnoactual, registro=registro).first()
                if cambio_status:
                    cambio_status.status = nuevo_status
                    user_instance = User.objects.get(id=user_nuevo)
                    if user_instance:
                        cambio_status.usuario = user_instance
                    cambio_status.save()
                    return JsonResponse({'message': 'Turno Actualizado Correctamente'})
                else:
                    return JsonResponse({'error': 'Registro no encontrado'}, status=404)
            except Exception as e:
                return JsonResponse({'error': f'Error al cambiar el status py: {e}', 'status': nuevo_status}, status=500)
        else:
            return JsonResponse({'error': 'Faltan Datos'}, status=400)
    else:
        return JsonResponse({'error': 'Request no permitido'}, status=405)
    

#funcion para notificar el llamado de un turno
@csrf_exempt
@require_http_methods(["PATCH"])
def notificacionRati(request):
    try:
        data = json.loads(request.body)
        estado_notificacion = data.get('notificacion')
        turno_notificado = data.get('turno_id')

        if estado_notificacion is not None and turno_notificado:
            cambiar_notificacion = turnos.objects.filter(id=turno_notificado).update(notificacion=estado_notificacion, hora_notificacion=pendulum.now())
            if cambiar_notificacion:
                return JsonResponse({'message': 'Estado de notificación actualizado correctamente'}, status=200)
            else:
                return JsonResponse({'error': 'No se encontró el turno especificado'}, status=404)
        else:
            return JsonResponse({'error': 'Faltan datos en la solicitud'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Error al parsear JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

#funcion para mostrarle la mesa actual al asesor
def miMesa(request):
    try:
        usuarioreq = request.GET.get('usuario')
        usuario = get_object_or_404(User,username=usuarioreq)
        mesas = mesa.objects.filter(user=usuario).first()
        if mesas:
            numero_mesa = mesas.mesa
            id_mesa = mesas.id
            return JsonResponse({'numero_mesa': numero_mesa, 'id_mesa': id_mesa})
        else:
            return JsonResponse({'numero_mesa': 'Sin Mesa'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

# funcion para asignar mesa al asesor
@require_http_methods(["PATCH"])
@csrf_exempt
def asignarMesa(request):
    try:
        data = json.loads(request.body)
        asesor = data.get('asesor')
        mesanueva = data.get('mesa')
        if asesor is None:
            return JsonResponse({'error': 'El campo "asesor" es requerido'}, status=400)
        user = User.objects.get(username=asesor)
        user_id = user.id
        if mesanueva == 0 or mesanueva == "0":
            
            mesa_actual_usuario = mesa.objects.filter(user=user_id, area=3).first()
            if mesa_actual_usuario:
                mesa_actual_usuario.user = None
                mesa_actual_usuario.save()
                return JsonResponse({'success': True,'message': 'Mesa liberada correctamente'}, status=200)
            else:
                return JsonResponse({'error': 'El usuario no tiene asignada ninguna mesa'}, status=400)
        else:
            mesa_obj_nueva = mesa.objects.get(mesa=mesanueva, area=3)
            if mesa_obj_nueva.user_id and mesa_obj_nueva.user_id != user_id:
                usuario_ocupante = User.objects.get(id=mesa_obj_nueva.user_id)
                return JsonResponse({'error': f'La mesa ya está ocupada por el usuario: {usuario_ocupante.username}. Intenta otra o pide que la desocupen en el sistema.'}, status=400)
            mesa_actual_usuario = mesa.objects.filter(user=user_id, area=3).first()
            if mesa_actual_usuario:
                
                mesa_actual_usuario.user = None
                mesa_actual_usuario.save()
            asignacion = mesa.objects.filter(mesa=mesanueva, area= 3).update(user=user_id)
            return JsonResponse({'success': True,'message': 'Mesa asignada con éxito', 'user_id': user_id})
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado: ' + asesor}, status=404)
    except mesa.DoesNotExist:
        return JsonResponse({'error': 'Mesa no encontrada, pide que la agreguen en sistema'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)








#funcion para iniciar la asesoria
@csrf_exempt
def iniciar_asesoria(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=200)

        

        user_asesor = data.get('asesor_id')
        mesa_id = data.get('mesa')
        turno_id = data.get('turno')
        area_id = data.get('area')
        total_personas = data.get('cantidad_personas')
        registro = data.get('registro')


        if not all([user_asesor, mesa_id, turno_id, area_id, total_personas, registro]):
            return JsonResponse({'error': 'Faltan datos por capturar'}, status=400)

        try:
            user_instance = User.objects.get(id=user_asesor)
            mesa_instance = mesa.objects.get(id=mesa_id)
            turno_instance = turnos.objects.get(id=turno_id)
            ciudadanos_instances = ciudadanos.objects.filter(registro=registro)

            if not ciudadanos_instances.exists():
                return JsonResponse({'error': 'Ciudadano no encontrado'}, status=404)

        except User.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404) 
        except mesa.DoesNotExist:
            return JsonResponse({'error': 'Mesa no encontrada'}, status=404)
        except turnos.DoesNotExist:
            return JsonResponse({'error': 'Turno no encontrado'}, status=404)

        try:
            with transaction.atomic():
                for ciudadano_instance in ciudadanos_instances:
                    asesoria_obj, created = asesoriaJuridica.objects.update_or_create(
                        user=user_instance,
                        mesa=mesa_instance,
                        turno_id=turno_instance,
                        area_id=area_id,
                        registro=registro,
                        defaults={
                            'cantidadPersonas': total_personas,
                            'hora_entrada': pendulum.now()
                        }
                    )
                    if created:
                        response_data = {
                            'mensaje': 'Asesoría Iniciada'
                        }
                    else:
                        response_data = {
                            'mensaje': 'La asesoría se ha actualizado para este usuario.'
                        }
                return JsonResponse(response_data, status=201 if created else 200)

        except IntegrityError as e:
            return JsonResponse({'error': 'Error al iniciar la asesoría: ' + str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)



@csrf_exempt
def terminar_asesoria(request):
    if request.method == 'PATCH':
        try:
            data = json.loads(request.body)
            general_data = data.get('general', {})
            detalles_data = data.get('detalles', [])

            observaciones_text = general_data.get('observaciones')
            razon_social = general_data.get('razonSocial')
            turno_id = general_data.get('turno_id')
            registro_ciudadano = general_data.get('registro')
            folio = general_data.get('folio')

            if not observaciones_text or not razon_social or not turno_id or not registro_ciudadano:
                return JsonResponse({'error': 'Datos incompletos en general'}, status=400)

            try:
                turno_instance = turnos.objects.get(id=turno_id)
            except turnos.DoesNotExist:
                return JsonResponse({'error': 'Turno no encontrado'}, status=404)

            try:
                asesoria_obj = asesoriaJuridica.objects.filter(registro=registro_ciudadano).last()
            except asesoriaJuridica.DoesNotExist:
                return JsonResponse({'error': 'Registro de asesoría no encontrado'}, status=404)

            # Contar casos exitosos
            exitos_count = sum(1 for detalle_item in detalles_data if detalle_item.get('exito') == 'si')

            # Actualizar personasFinal en asesoriaJuridica
            asesoria_obj.folio_sinacol = folio
            asesoria_obj.observaciones = observaciones_text
            asesoria_obj.hora_salida = pendulum.now()
            asesoria_obj.empresa = razon_social
            asesoria_obj.turno_id = turno_instance
            asesoria_obj.personasFinal = exitos_count  # Actualizar personasFinal con el conteo
            asesoria_obj.save()

            for detalle_item in detalles_data:
                exito = detalle_item.get('exito')
                ciudadano_id = detalle_item.get('id_ciudadano')

                if not exito or not ciudadano_id:
                    return JsonResponse({'error': 'Datos incompletos en detalles'}, status=400)

                try:
                    ciudadano_instance = ciudadanos.objects.get(id=ciudadano_id)
                except ciudadanos.DoesNotExist:
                    return JsonResponse({'error': 'Ciudadano no encontrado'}, status=404)

                conclusion_obj, created = conclusion.objects.update_or_create(
                    id_ciudadano=ciudadano_instance,
                    id_asesoria=asesoria_obj,
                    defaults={'conclusion_exitosa': str(exito)}  # Convertir exito a string si no lo es
                )

            response_data = {'mensaje': 'Asesoría concluida correctamente. '}
            return JsonResponse(response_data, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


#metodo de prueba para el chatbot
def chatQuery(request):
    if (request.method == 'GET'):
        try:
            data = list(ciudadanos.objects.order_by('id')[:1].values())
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error' : str(e)}, status=500)


@csrf_exempt
def preRegistro(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            nombre = data.get('nombre')
            sexo = data.get('sexo')
            correo = data.get('correo')
            municipio = data.get('municipio')
            curp_rfc = data.get('curp_rfc')
            tipo_persona = data.get('tipo_persona')
            identificacionFrente = data.get('identificacionFrente')
            identificacionReverso = data.get('identificacionReverso')

            if all([nombre, sexo, correo, municipio, curp_rfc, tipo_persona]):
                codigo_ciudadano = generate_10_digit_code()
                ciudadano_obj = ciudadanos(
                    nombre=nombre,
                    sexo=sexo,
                    correo=correo,
                    municipio=municipio,
                    curp_rfc=curp_rfc,
                    tipo_persona=tipo_persona,
                    documento_1=identificacionFrente,
                    documento_2=identificacionReverso,
                    codigo_ciudadano=codigo_ciudadano
                )
                ciudadano_obj.save()

                # Genera el código QR
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(codigo_ciudadano)
                qr.make(fit=True)

                # Crea una imagen en memoria
                img = qr.make_image(fill='black', back_color='white')
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                # Retorna la imagen como respuesta
                response = HttpResponse(img_bytes, content_type='image/png')
                response['Content-Disposition'] = f'attachment; filename="qr_{codigo_ciudadano}.png"'
                return response
            
            else:
                return JsonResponse({'error': 'Todos los campos requeridos deben estar llenos'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)




@csrf_exempt
def convertir_y_descargar_pdfs(request):
    if request.method == 'POST':
        urls = request.POST.getlist('urls[]')
        nombre_para_archivo = request.POST.get('nombre')
        

        if not urls:
            return JsonResponse({'error': 'No se proporcionaron URLs.'}, status=400)

        try:
            pdf_combined = combinar_imagenes_a_pdf(urls)
            response = HttpResponse(pdf_combined, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{nombre_para_archivo}.pdf"'
            return response
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido.'}, status=405)



def combinar_imagenes_a_pdf(urls):
    
    output_pdf = io.BytesIO()
    c = canvas.Canvas(output_pdf, pagesize=A4)
    
    width, height = A4

    for url in urls:
        response = requests.get(url)
        image = Image.open(io.BytesIO(response.content))

        if image:
            image_width, image_height = image.size

        aspect = image_height / float(image_width)
        new_width = width
        new_height = width * aspect

        if new_height > height:
            
            new_height = height
            new_width = height / aspect

        x_offset = (width - new_width) / 2  
        y_offset = (height - new_height) / 2  

        # Guardar la imagen en un archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_image_file:
            image.save(temp_image_file, format='PNG')
            temp_image_path = temp_image_file.name

        c.drawImage(temp_image_path, x_offset, y_offset, new_width, new_height)
        c.showPage()

    c.save()
    output_pdf.seek(0)

    return output_pdf



#funcion para obtener las fuentes de trabajo en la base de datos local y o insertar una nueva
def fuentes_de_trabajo(request):
    if request.method == 'GET':
        fuentes = fuentesdetrabajo.objects.all().values('id','razon_social')
    return JsonResponse(list(fuentes), safe=False)

@csrf_exempt
def agregar_fuentes_de_trabajo(request):
    data = json.loads(request.body)
    razon = data.get('razon_social')
    
    

    if fuentesdetrabajo.objects.filter(razon_social=razon).exists():
        return JsonResponse({'message': 'La razón social ya existe'}, status=201)
    
    nueva_fuente = fuentesdetrabajo.objects.create(
        razon_social=razon
    )
    return JsonResponse({'message': 'Fuente de trabajo agregada exitosamente', 'id': nueva_fuente.id}, status=201)



def pdf_local(request):
    if request.method == 'GET':
        # Obtener los nombres de las imágenes desde los parámetros de consulta
        img1 = request.GET.get('img1')
        img2 = request.GET.get('img2')
        nombre_ciudadano = request.GET.get('nombre')

        if not img1 or not img2 or not nombre_ciudadano:
            return JsonResponse({"error": "Faltan parámetros en la solicitud."}, status=400)

        # Definir las carpetas de imágenes
        media_root = settings.MEDIA_ROOT
        identificacion_folder = os.path.join(media_root, 'identificacion')
        testigos_folder = os.path.join(media_root, 'testigos')

        def get_image_path(image_name):
            path = os.path.join(identificacion_folder, image_name)
            if os.path.exists(path):
                return path
            path = os.path.join(testigos_folder, image_name)
            return path if os.path.exists(path) else None

        # Obtener las rutas completas de las imágenes
        image_path_front = get_image_path(img1)
        image_path_back = get_image_path(img2)

        if not image_path_front or not image_path_back:
            error_message = {
                "error": "Una o ambas imágenes no se encontraron.",
                "image_path_front": image_path_front,
                "image_path_back": image_path_back
            }
            return JsonResponse(error_message, status=404)

        # Crear un buffer en memoria para el PDF
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        def add_image_to_pdf(image_path):
            with Image.open(image_path) as img:
                img_width, img_height = img.size
                scale = min(width / img_width, height / img_height)
                new_width = img_width * scale
                new_height = img_height * scale
                x = (width - new_width) / 2
                y = (height - new_height) / 2
                c.drawImage(image_path, x, y, new_width, new_height)

        add_image_to_pdf(image_path_front)
        c.showPage()
        add_image_to_pdf(image_path_back)
        c.showPage()
        c.save()
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{nombre_ciudadano}.pdf"'

        return response

    return HttpResponse("Método no permitido.", status=405)


#############################################################  aqui concluyen las funciones de asesoria. Juan Carlos.  #################################################################################################


# Función para generar un número de 10 dígitos
def generate_10_digit_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(10)])

# Vista registro de ciudadano
def registro_ciudadano(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        sexo = request.POST.get('sexo')
        correo = request.POST.get('correo')
        cita = request.POST.get('cita')
        municipio = request.POST.get('municipio')
        curp_rfc = request.POST.get('curp_rfc')
        tipo_persona = request.POST.get('tipo_persona')
        documento_1 = request.FILES.get('documento_1')
        documento_2 = request.FILES.get('documento_2')

        codigo_ciudadano = generate_10_digit_code()

        ciudadano = ciudadanos(
            nombre=nombre,
            sexo=sexo,
            correo=correo,
            cita=cita,
            municipio=municipio,
            curp_rfc=curp_rfc,
            tipo_persona=tipo_persona,
            documento_1=documento_1,
            documento_2=documento_2,
            codigo_ciudadano=codigo_ciudadano  # Generación de un número único y aleatorio de 10 dígitos
        )
        
        ciudadano.save()

        # Renderizar el mensaje HTML usando la plantilla
        """#message_html = render_to_string('ciudadano/email_template.html', {
            'nombre': nombre,
            'sexo': sexo,
            'correo': correo,
            'cita': cita,
            'municipio': municipio,
            'curp_rfc': curp_rfc,
            'tipo_persona': tipo_persona,
            'codigo_ciudadano': codigo_ciudadano
        })

        # Envío del correo electrónico con los archivos adjuntos
        email = EmailMessage(
            subject='Registro de ciudadano exitoso',
            body=message_html,
            from_email='cclcitas@mail.com',
            to=[correo],
        )
        email.content_subtype = 'html'  # Define que el contenido es HTML

        if identificacionFrente:
            email.attach(identificacionFrente.name, identificacionFrente.read(), identificacionFrente.content_type)

        if identificacionReverso:
            email.attach(identificacionReverso.name, identificacionReverso.read(), identificacionReverso.content_type)

        email.send()"""

        return render(request,'ciudadano/registro_exitoso.html', {'ciudadano': ciudadano})  # Usa HttpResponseRedirect para redirigir

    return render(request, 'ciudadano/registro_ciudadano.html')

def success(request, pk):
    ciudadano = ciudadano.objects.get(pk=pk)
    return render(request, 'ciudadano/ciudadanoSuccess.html', {'ciudadano': ciudadano})

def buscar_ciudadano(request):
    codigo_ciudadano = request.GET.get('codigo_ciudadano')
    registro = request.GET.get('registro')
    ciudadanos_encontrados = []

    if codigo_ciudadano or registro:
        try:
            # buscar por código ciudadano
            if codigo_ciudadano:
                ciudadanos_encontrados = ciudadanos.objects.filter(codigo_ciudadano=codigo_ciudadano)

            # buscar por registro
            if registro:
                ciudadanos_encontrados = ciudadanos.objects.filter(registro=registro)
            
            if ciudadanos_encontrados:
                return render(request, 'ciudadano/ciudadanoDetalle.html', {'ciudadanos': ciudadanos_encontrados})
            else:
                return render(request, 'ciudadano/ciudadanoDetalle.html', {'ciudadanos': None, 'error': "No se encontró un ciudadano con ese código o registro."})
        except Exception as e:
            return render(request, 'ciudadano/ciudadanoDetalle.html', {'ciudadanos': None, 'error': "Ocurrió un error al buscar el ciudadano."})
    else:
        return render(request, 'ciudadano/ciudadanoDetalle.html', {'ciudadanos': None, 'error': "Debe proporcionar un código de ciudadano o un número de registro."})
    
def sacar_turno(request):
    codigo_ciudadano = request.GET.get('codigo_ciudadano')
    registro = request.GET.get('registro')
    ciudadanos_encontrados = []

    if codigo_ciudadano or registro:
        try:
            if codigo_ciudadano:
                ciudadanos_encontrados = ciudadanos.objects.filter(codigo_ciudadano=codigo_ciudadano)
            elif registro:
                
                ciudadanos_encontrados = ciudadanos.objects.filter(registro=registro)

            if ciudadanos_encontrados.exists():
                registro_encontrado = ciudadanos_encontrados[0].registro
                testigos_encontrados = testigos.objects.filter(registro=registro_encontrado)
                form = turnoForm()
                return render(request, 'turnos/registro_autoTurno.html', {'ciudadanos': ciudadanos_encontrados, 'testigos': testigos_encontrados, 'form': form, 'active_view': 'auto_turno/'})
            else:
                return render(request, 'turnos/registro_autoTurno.html', {'ciudadanos': None, 'error': "No se encontró un ciudadano con ese código o registro.", 'active_view': 'auto_turno/'})
        
        except Exception as e:
            return render(request, 'turnos/registro_autoTurno.html', {'ciudadanos': None, 'error': f"Error inesperado: {str(e)}", 'active_view': 'auto_turno/'})
    
    else:
        return render(request, 'turnos/registro_autoTurno.html', {'ciudadanos': None, 'error': "Debe proporcionar un código de ciudadano o un número de registro.", 'active_view': 'auto_turno/'})

def numeroTurno(prefijo):
    hoy = timezone.now().date()
    with transaction.atomic():
        # Obtiene o crea el contador para el prefijo
        counter, created = contadorTurnos.objects.get_or_create(prefijo=prefijo)

        # Si la fecha del contador es diferente a la de hoy, reinicia el contador
        if counter.fecha != hoy:
            counter.numero = 0
            counter.fecha = hoy
            counter.save()

        # Incrementa el número de turno
        counter.numero += 1
        counter.save()

        # Devuelve el número de turno formateado
        return f"{prefijo}{str(counter.numero).zfill(3)}"





def asignar_turno(request):
    if request.method == 'POST':
        area = request.POST.get('area')
        codigo_ciudadano = request.POST.get('codigo_ciudadano')
        registro = request.POST.get('registro')
        prefijo_seleccionado = request.POST.get('prefijo')  # Capturar el prefijo seleccionado

        area_turnos = {
            1: {'prefijo': 'CN', 'opciones': {'1': 'CR', '2': 'RPR', '3': 'CN'}},  # Ratificacion
            3: {'prefijo': 'AJ', 'opciones': {'1': 'CF', '2': 'CC', '3': 'PR', '4': 'AJ'}},  # Asesoría jurídica
        }

        try:
            if area.isdigit():
                area = int(area)
            else:
                raise ValueError("Área no válida")
            
            prefijo = area_turnos[area]['prefijo']
            preferente = False

            if area == 3:  # Asesoría Jurídica
                prefijo = prefijo_seleccionado  # Usar el prefijo seleccionado
                if prefijo in ['PR']:
                    preferente = True  # Establecer preferente en True si el prefijo es CF o CC
            elif area == 1:  # Asesoría Jurídica
                prefijo = prefijo_seleccionado  # Usar el prefijo seleccionado
                if prefijo in ['CR', 'RPR']:
                    preferente = True  # Establecer preferente en True si el prefijo es CF, CC, o PR

            turnos_asignados = []

            if codigo_ciudadano:
                # Búsqueda por código de ciudadano para un turno individual
                ciudadano = ciudadanos.objects.get(codigo_ciudadano=codigo_ciudadano)
                # Incrementar el número de registro por el siguiente consecutivo en el modelo de turnos
                ultimo_turno = turnos.objects.filter(codigo_ciudadano=codigo_ciudadano).order_by('registro').first()
                nuevo_registro = (ultimo_turno.registro + 1) if ultimo_turno else 1

                turno = turnos(
                    turno=numeroTurno(prefijo),
                    area=area,
                    registro=nuevo_registro,
                    codigo_ciudadano=codigo_ciudadano,
                    status='PEN',  # Estado por defecto
                    preferente=preferente  # Establecer el campo preferente
                )
                turno.save()
                turnos_asignados.append({
                    'turno': turno,
                    'ciudadanos': [ciudadano]
                })
            elif registro:
                # Búsqueda por número de registro para un turno grupal
                ciudadanos_mismo_registro = ciudadanos.objects.filter(registro=registro)

                if not ciudadanos_mismo_registro.exists():
                    raise Http404("No se encontraron ciudadanos con el número de registro proporcionado")

                turno = turnos(
                    turno=numeroTurno(prefijo),
                    area=area,
                    registro=registro,
                    status='PEN',  # Estado por defecto
                    preferente=preferente  # Establecer el campo preferente
                )
                turno.save()

                # Asociar todos los códigos de ciudadanos a este turno
                ciudadanos_list = []
                for ciudadano in ciudadanos_mismo_registro:
                    ciudadanos_list.append(ciudadano)
                    turno.codigo_ciudadano += f"{ciudadano.codigo_ciudadano} "  # Concatenar los códigos de ciudadanos

                turno.codigo_ciudadano = turno.codigo_ciudadano.strip()  # Eliminar espacios extra
                turno.save()

                turnos_asignados.append({
                    'turno': turno,
                    'ciudadanos': ciudadanos_list
                })

            # Redireccionar o renderizar la página de entrega de turnos
            return render(request, 'turnos/turno_entrega.html', {'turnos_asignados': turnos_asignados, 'active_view': 'asignar_turno/'})

        except Http404 as e:
            return JsonResponse({'error': str(e)}, status=403)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f"Error inesperado: {str(e)}"}, status=500)

    return render(request, 'turnos/turno_entrega.html')






def numeroTurnoFolio(prefijo):
    hoy = timezone.now().date()
    with transaction.atomic():
        # Obtiene o crea el contador global
        counter, created = contadorTurnos.objects.get_or_create(prefijo="global")
        

        # Si la fecha del contador es diferente a la de hoy, reinicia el contador
        if counter.fecha != hoy:
            counter.numero = 0
            counter.fecha = hoy
            counter.save()
            

        # Incrementa el número de turno
        counter.numero += 1
        counter.save()


        # Devuelve el número de turno formateado con el prefijo
        return f"{counter.numero}-{prefijo}"





@csrf_exempt
def asignar_turno_folio(request):
    if request.method == 'POST':
        folio_solicitud = request.POST.get('folio')
        registro = request.POST.get('registro')
        area = request.POST.get('area')  # Obtener el área seleccionada


        try:
            # Validar que los campos requeridos estén presentes
            if not folio_solicitud or not registro or not area:
                raise ValueError("Folio, registro o área no proporcionado")

            # Definir área y turno generado
            if area == 'ratificacion':
                prefijo = folio_solicitud  
                area_id = 1  # ID de ratificación
                turno_generado = numeroTurnoFolio(prefijo)
                preferencia = False
            elif area == 'ratificacion con cita':
                prefijo = 'CR'  
                area_id = 1
                preferencia = True  
                turno_generado = numeroTurno(prefijo)
            elif area == 'ratificacion preferente':
                prefijo = 'RPR'  
                area_id = 1
                preferencia = True  
                turno_generado = numeroTurno(prefijo)
            elif area == 'asesoria':
                prefijo = 'CF'  
                area_id = 3
                preferencia = False
                turno_generado = numeroTurno(prefijo)
            elif area == 'asesoria con cita':
                prefijo = 'CC'
                area_id = 3
                preferencia = True
                turno_generado = numeroTurno(prefijo)
            elif area == 'asesoria preferente':
                prefijo = 'PR'
                area_id = 3
                preferencia = True
                turno_generado = numeroTurno(prefijo)
            else:
                raise ValueError("Área no válida")

        
            turnos_existentes = turnos.objects.filter(
                area=area_id,
                registro=registro,
                status__in=['PEN', 'NOT', 'PRO']
            )

            
            if turnos_existentes.exists():
                ultimo_turno = turnos_existentes.last() 

                if ultimo_turno.status == 'PEN':
                    return JsonResponse({'message': 'El turno ya está creado y está pendiente.'}, status=200)
                elif ultimo_turno.status in ['NOT', 'PRO']:
                    return JsonResponse({'error': 'El turno ya está siendo atendido.'}, status=403)
                
            nuevo_turno = turnos(
                area=area_id,
                registro=registro,
                turno=turno_generado,
                status='PEN',
                preferente=preferencia,
                codigo_ciudadano=''
            )
            nuevo_turno.save()
            solicitudes_asistencia = Solicitud.objects.filter(folio_solicitud=folio_solicitud, registro=registro, asistencia=True)

            if not solicitudes_asistencia.exists():
                raise Http404("Debes marcar la asistencia en los ciudadanos, tomar las fotos de la identificación y hacer clic en Actualizar.")

            for solicitud in solicitudes_asistencia:
                ciudadano = ciudadanos.objects.get(id=solicitud.id_ciudadano)
                if f"{ciudadano.codigo_ciudadano}" not in nuevo_turno.codigo_ciudadano:
                    nuevo_turno.codigo_ciudadano += f"{ciudadano.codigo_ciudadano} "

            nuevo_turno.codigo_ciudadano = nuevo_turno.codigo_ciudadano.strip()  # Eliminar espacios extra
            nuevo_turno.save()
            return JsonResponse({'message': f"Turno asignado correctamente {nuevo_turno.turno}", 'turno': nuevo_turno.turno, 'id' : nuevo_turno.id}, status=200)

        except Http404 as e:
            return JsonResponse({'error': str(e)}, status=403)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f"Error inesperado: {str(e)}"}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)




@csrf_exempt
def actualizar_codigos_ciudadanos(request):
    if request.method == 'POST':
        registro = request.POST.get('registro')
        solicitudes_con_asistencia = Solicitud.objects.filter(asistencia=True, registro=registro)
        
        try:
            turno = get_object_or_404(turnos, registro=registro)
            codigos_actuales = turno.codigo_ciudadano.split()
            
            for solicitud in solicitudes_con_asistencia:
                ciudadano = get_object_or_404(ciudadanos, id=solicitud.id_ciudadano)
                if ciudadano.codigo_ciudadano not in codigos_actuales:
                    codigos_actuales.append(ciudadano.codigo_ciudadano)

            turno.codigo_ciudadano = ' '.join(codigos_actuales)
            turno.save()

            return JsonResponse({'status': 'success'}, status=200)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def verificar_estado_turno(request):
    if request.method == 'POST':
        registro = json.loads(request.body).get('registro')
        turno = turnos.objects.filter(registro=registro).last()
        
        if turno:
            return JsonResponse({'existe': True, 'estado': turno.status, 'turno': turno.turno, 'id': turno.id})
        else:
            return JsonResponse({'existe': False, 'estado': 'NO_FOUND'})


# prueba vistas areas
class OperacionAreaCreateView(CreateView):
    template_name = 'areas/vista_areas.html'
    
    def get_form_class(self):
        if self.kwargs['area'] == 'asesoria_juridica':
            return asesoriaJuridicaForm
        elif self.kwargs['area'] == 'pagos':
            return pagosForm
        elif self.kwargs['area'] == 'conciliacion':
            return conciliacionForm
        elif self.kwargs['area'] == 'ratificacion':
            return ratificacionForm
        elif self.kwargs['area'] == 'procuraduria':
            return procuraduriaForm
        else:
            raise ValueError('Área no reconocida')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        area = self.kwargs['area']
        if area == 'asesoria_juridica':
            context['titulo'] = 'Asesoría Jurídica'
        elif area == 'pagos':
            context['titulo'] = 'Pagos'
        elif area == 'conciliacion':
            context['titulo'] = 'Conciliación'
        elif area == 'ratificacion':
            context['titulo'] = 'Ratificación'
        elif area == 'procuraduria':
            context['titulo'] = 'Procuraduría'
        else:
            context['titulo'] = 'Registro Ciudadano'
        return context
    
class VistaPagos(TemplateView):
    template_name = 'pagos/index.html'

def atender_pagos(request):
    if request.method == 'POST':
        turno = request.POST.get('turno')
        expediente = request.POST.get('expediente')
        estadistica = True

        if estadistica:
            messages.warning(request, "Ya tienes un turno en progreso.")
        else:
            estadistica.inicio_turno_actual = timezone.now()
            estadistica.fin_turno_actual = None
            estadistica.save()
            messages.success(request, "Turno iniciado correctamente.")
        
        return render(request, 'pagos/atender_pagos.html', {'turno': turno, 'expediente': expediente})
    
    elif request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Esta parte maneja la solicitud AJAX para obtener el tiempo transcurrido
        

        if estadistica:
            tiempo_transcurrido = timezone.now() - estadistica.inicio_turno_actual
            segundos = int(tiempo_transcurrido.total_seconds())
            return JsonResponse({'tiempo': segundos})
        else:
            return JsonResponse({'tiempo': 0})
    
    return HttpResponseRedirect('/turnos/')

def cancelar_pago(request):
    if request.method == 'POST':
        estadistica = True
        if estadistica:
            estadistica.fin_turno_actual = timezone.now()
            duracion_turno = estadistica.fin_turno_actual - estadistica.inicio_turno_actual
            
            # Verificar si la duración es razonable (por ejemplo, menos de 4 horas)
            if duracion_turno > timezone.timedelta(hours=4):
                messages.warning(request, "La duración del turno parece inusualmente larga. Se ha ajustado a 4 horas.")
                duracion_turno = timezone.timedelta(hours=4)
            
            estadistica.tiempo_total += duracion_turno
            # estadistica.turnos_atendidos += 1
            estadistica.inicio_turno_actual = None
            estadistica.fin_turno_actual = None
            estadistica.save()
            messages.success(request, "Turno cancelado correctamente.")
        else:
            messages.warning(request, "No hay un turno activo para finalizar.")
        
        return HttpResponseRedirect('/turnos/')
    return HttpResponseRedirect('/turnos/')

def VistaTurnosRecepcion(request):
    turno = turnos.objects.filter(status='PEN')
    turnosCan = len(turnos.objects.filter(status='CAN'))
    turnosFin = len(turnos.objects.filter(status='FIN'))
    turnosPen = len(turno)
    
    # turnos = turnos.select_related('ciudadanoId').all()
    return render(request,'recepcion/index.html',{'turnos': turno,'turnosPen': turnosPen,'turnosCan': turnosCan,'turnosFin': turnosFin})

def cancelarTurno (request):
    id = request.GET.get('codigo_ciudadano')
    if request.method == 'PUT':
        turno = turnos.objects.get(pk = id)
        turno.status = 'CAN'
        turno.save()
        return render(request,'recepcion/index.html')
    
def detalleTurno (request):
    if request.method == 'POST':
        id = request.POST.get('id')
        turno = get_object_or_404(turnos, pk=id)
        return render(request, 'recepcion/base.html', {'turno': turno})
    else:
        # Manejo del caso GET si es necesario
        return render(request, 'recepcion/base.html')
    
def pantallaTurno (request):
    turno = turnos.objects.all()
    return render(request, 'recepcion/pantalla_1.html', {'turnos': turno})

def cancelar_turno(request, turno_id):
    if request.method == "POST":
        turno = get_object_or_404(turnos, id=turno_id)
        turno.status = 'CAN'
        turno.save()
    return HttpResponseRedirect('/turnos')  

class citasPagos(TemplateView):
    template_name = 'pagos/citas_pagos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        turnos_data = self.get_turnos_data()
        context['turnos'] = json.dumps(turnos_data, cls=DjangoJSONEncoder)
        return context

    def get_turnos_data(self):
        Turno = turnos.objects.filter(status='PEN')

        area_colors = {
            turnos.RATIFICACION: {'bg': '#e0f7f3', 'text': '#00a783', 'border': '#00a783'},
            turnos.CONCILIACION: {'bg': '#e0ebfd', 'text': '#3366cc', 'border': '#3366cc'},
            turnos.ASESORIA_JURIDICA: {'bg': '#fff0e0', 'text': '#ff9900', 'border': '#ff9900'},
            turnos.PROCURADURIA: {'bg': '#ffe0e0', 'text': '#cc3366', 'border': '#cc3366'},
            turnos.PAGOS: {'bg': '#e0ffe0', 'text': '#33cc66', 'border': '#33cc66'},
        }

        turnos_data = []
        for turno in Turno:
            colors = area_colors.get(turno.area, {'bg': '#e0e0e0', 'text': '#333333', 'border': '#333333'})
            turnos_data.append({
                'title': f"{turno.get_area_display()} - Mesa: {turno.mesa}" if turno.mesa else turno.get_area_display(),
                'start': turno.fecha.isoformat(),
                'backgroundColor': colors['bg'],
                'textColor': colors['text'],
                'borderColor': colors['border'],
                'turnoId': turno.id,
                'area': turno.get_area_display(),
                'mesa': turno.mesa,
                'sala': turno.sala,
                #'ciudadanoNombre': turno.ciudadanoId.nombre,
                'registro': turno.registro,
                #'cant_personas': turno.ciudadanoId.cant_personas,
                'fecha': turno.fecha.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return turnos_data



def comunicacion(request):
    video_url = settings.STATIC_URL + 'videos/cclvideo.mp4'
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.cleaned_data['video']
            video_path = os.path.join(settings.BASE_DIR, 'static', 'videos', 'cclvideo.mp4')
            with open(video_path, 'wb+') as destination:
                for chunk in video.chunks():
                    destination.write(chunk)
            try:
                return HttpResponseRedirect(reverse('comunicacion'))
            except Exception as e:
                print("An exception occurred:", e)
    else:
        form = VideoUploadForm()
    
    return render(request, 'comunicacion/index.html', {'video_url': video_url, 'form': form})

#salas
def salas_list(request):
    salas = sala.objects.all()
    users = User.objects.all()

    if request.method == 'POST':
        form = SalaForm(request.POST, request.FILES)
        if form.is_valid(): 
            sala_name = form.cleaned_data['sala']  
        
            if sala.objects.filter(sala=sala_name).exists():  
                messages.error(request, 'La sala ya existe')
                return HttpResponseRedirect('/conciliacion/')  
            else:
                form.save()
                return HttpResponseRedirect('/conciliacion/')  
        else:
            messages.error(request, 'Error en el formulario')
    else:
        form = SalaForm()

    context = {
        'salas': salas,
        'form': form,
        'users': users
    }
    return render(request, 'conciliacion/index.html', context)

def edit_sala(request):
    if request.method == 'POST':
        sala_id = request.POST.get('sala_id')
        sala = sala.objects.get(pk=sala_id)  # Asegúrate de manejar el caso donde no se encuentra
        form = SalaForm(request.POST, request.FILES, instance=sala)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Sala actualizada correctamente'}, status=200)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        return redirect('nombre_de_tu_lista_de_salas')

@require_POST
def delete_sala(request):
    sala_id = request.POST.get('sala_id')
    try:
        sala = sala.objects.get(pk=sala_id)
        sala.delete()
        return JsonResponse({'message': 'Sala eliminada correctamente'}, status=200)
    except sala.DoesNotExist:
        return JsonResponse({'error': 'Sala no encontrada'}, status=404)
#mesas

def mesa_list(request):
    mesas = mesa.objects.all()
    return render(request, 'mesas/mesa_list.html', {'mesas': mesas})

def mesa_detail(request, pk):
    mesa = get_object_or_404(mesa, pk=pk)
    return render(request, 'mesas/mesa_detail.html', {'mesa': mesa})


def mesa_create(request):
    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            mesa_name = form.cleaned_data['mesa']
            area = form.cleaned_data['area']
            if mesa.objects.filter(mesa=mesa_name, area=area).exists():
                form.add_error('mesa', 'La mesa ya existe en esta área.')
                return render(request, 'mesas/mesa_form.html', {'form': form})
            else:
                form.save()
                return render('mesa_list')
        else:
            return render(request, 'mesas/mesa_form.html', {'form': form})
    else:
        form = MesaForm()
    return render(request, 'mesas/mesa_form.html', {'form': form})



def mesa_update(request, pk):
    # Cambié la variable 'mesa' a 'mesa_instance' para evitar posibles conflictos
    mesa_instance = get_object_or_404(mesa, pk=pk)
    
    if request.method == 'POST':
        form = MesaForm(request.POST, instance=mesa_instance)
        if form.is_valid():
            form.save()
            return redirect('mesas/mesa_list')
    else:
        form = MesaForm(instance=mesa_instance)
    
    return render(request, 'mesas/mesa_form.html', {'form': form})



def mesa_delete(request, pk):
    mesa = get_object_or_404(mesa, pk=pk)
    if request.method == 'POST':
        mesa.delete()
        return redirect('mesa_list')
    return render(request, 'mesas/mesa_confirm_delete.html', {'mesa': mesa})




@login_required
def perfil(request):
    user = request.user
    profile = user.profile
    is_admin = user.groups.filter(name='Administrador').exists()
    
    if request.method == 'POST':
        form = UserPerfilForm(request.POST, request.FILES, instance=user, user=user)
        if form.is_valid():
            user = form.save()

            if 'image' in request.FILES:
                profile.image = request.FILES['image']
                profile.save()
            
            if is_admin:
                group = form.cleaned_data.get('groups')
                if group:
                    user.groups.clear()
                    user.groups.add(group)
            
            return HttpResponseRedirect(reverse('perfil'))
    else:
        form = UserPerfilForm(instance=user, user=user)
    
    return render(request, 'general/perfil/perfil.html', {
        'form': form,
        'profile': profile,
        'nombreGrupo': user.groups.first().name if user.groups.exists() else 'No tiene rol',
        'is_admin': is_admin,
    })

@login_required
def perfil_seguridad(request):
    try:
        cara_codificada = CodificaciónCaraDeUsuario.objects.get(user=request.user)
        reconocimiento_activado = True
    except CodificaciónCaraDeUsuario.DoesNotExist:
        reconocimiento_activado = False

    if request.method == 'POST':
        face_image_data = request.POST.get('faceImage')

        if face_image_data:
            try:
                # Decodificar la imagen base64
                image_data = base64.b64decode(face_image_data.split(',')[1])
                image = Image.open(BytesIO(image_data))
                frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                # Identificar el rostro en la imagen
                face_encodings = face_recognition.face_encodings(frame)
                if face_encodings:
                    user = request.user
                    face_encoding, created = CodificaciónCaraDeUsuario.objects.get_or_create(user=user)
                    face_encoding.encoding = np.array(face_encodings[0]).tobytes()
                    face_encoding.save()
                    message = mark_safe('El reconocimiento facial se activó correctamente, puede verificar si se le reconoce correctamente probandolo dando<a href="{0}"> click aquí.</a>'.format(reverse('face_recognition_test')))
                    messages.success(request, message)
                    return HttpResponseRedirect(reverse('seguridad'))
                else:
                    messages.error(request, 'No se detectó ningún rostro en la imagen. Por favor, intente de nuevo.')
            except Exception as e:
                messages.error(request, f'Error procesando la imagen: {str(e)}')
        else:
            messages.error(request, 'No se recibió ninguna imagen. Por favor, intente de nuevo.')

    return render(request, 'general/perfil/seguridad.html', {
        'reconocimiento_activado': reconocimiento_activado
    })

def estadisticas(request):
    return render(request, 'general/estadisticas.html')

@login_required
def face_recognition_test(request):
    context = {
        'recognized': False,
        'message': 'No se ha realizado ningún escaneo.',
        'details': ''
    }

    if request.method == 'POST':
        face_image_data = request.POST.get('faceImage')

        # Decodificar la imagen base64
        image_data = base64.b64decode(face_image_data.split(',')[1])
        image = Image.open(BytesIO(image_data))
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Identificar el rostro en la imagen
        face_encodings = face_recognition.face_encodings(frame)
        if face_encodings:
            input_encoding = face_encodings[0]

            try:
                # Obtener la codificación facial almacenada para el usuario
                user_face_encoding = CodificaciónCaraDeUsuario.objects.get(user=request.user).encoding
                stored_encoding = np.frombuffer(user_face_encoding, dtype=np.float64)

                # Comparar las codificaciones faciales
                match = face_recognition.compare_faces([stored_encoding], input_encoding)[0]
                if match:
                    context['recognized'] = True
                    context['message'] = 'Usuario reconocido exitosamente.'
                    context['details'] = 'La codificación facial coincide con la almacenada en la base de datos.'
                else:
                    context['message'] = 'El rostro no coincide con el usuario registrado.'
                    context['details'] = 'La codificación facial no coincide con la almacenada en la base de datos.'

            except CodificaciónCaraDeUsuario.DoesNotExist:
                context['message'] = 'No se encontró una codificación facial registrada para el usuario.'
                context['details'] = 'Asegúrate de registrar tu codificación facial primero.'

        else:
            context['message'] = 'No se pudo identificar ningún rostro en la imagen.'
            context['details'] = 'Asegúrate de que tu rostro esté claramente visible en la cámara.'

    return render(request, 'face_recognition_test.html', context)



#################################################################### metodos de auxiliar de ratificacion ############################################################################################

def auxiliares_ratificacion(request):
    hoy = pendulum.today()
    inicio_dia = hoy.start_of('day')
    fin_dia = hoy.end_of('day')

    # Contar los turnos según su estado
    turnosCan = turnos.objects.filter(status='CAN', area='1', fecha__gte=inicio_dia, hora_fin_turno__lte=fin_dia).count()
    turnosFin = turnos.objects.filter(status='FIN', area='1', fecha__gte=inicio_dia, hora_fin_turno__lte=fin_dia).count()
    turnosPen = turnos.objects.filter(status='PEN', area='1', fecha__gte=inicio_dia, hora_fin_turno__lte=fin_dia).count()
    print("procesa el conteo de turnos en auxiliares ratis")

    return render(request, 'ratificacion/auxiliar.html', {
        'turnosPen': turnosPen,
        'turnosCan': turnosCan,
        'turnosFin': turnosFin,
    }) 



def administrar_conciliadores(request):
    hoy = pendulum.today()
    inicio_dia = hoy.start_of('day')
    fin_dia = hoy.end_of('day')
    conciliadores = User.objects.filter(groups__id=5)
    turnos_pendientes = turnos.objects.filter(area=1, status='PEN').count()
    print(turnos_pendientes)
    lista=[]
    for conciliador in conciliadores:
        lista.append(conciliador)
    return render(request, 'ratificacion/administrar_conciliadores.html', {
        'conciliadores': lista,
        'turnos_pendientes': turnos_pendientes,
        
    }) 

@csrf_exempt
def bloquear_conciliadores(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')
        bloqueo = data.get('bloqueo')

        if user_id:
            conciliador = User.objects.get(id=user_id)
            print("blqueo: ", bloqueo)

            bloquear, created = conciliadorbloquedo.objects.update_or_create(conciliador = conciliador, defaults={'conciliador' : conciliador, 'bloqueo' : bloqueo})
            JsonResponse({"message":"Se bloqueo Conciliador con exito"})
        else:
            return JsonResponse({"error" : "faltan datos"})
    else:
        return JsonResponse({"error" : "metodo no permitido"})
    return JsonResponse({"message" : "correcto"})







def ver_quien_esta_disponible(request):
    if request.method == 'GET':
        turnos_pendientes = turnos.objects.filter(area=1, status='PEN').count()
        conciliadores = User.objects.filter(groups__id=5)
        lista_conciliadores = []
        ahora = pendulum.now()
        hoy = pendulum.now().date()
        hora_inicio = ahora.start_of('hour')
        hora_fin = hora_inicio.add(hours=1)
        for conciliador in conciliadores:
            try:
                esta_bloqueado = conciliadorbloquedo.objects.get(conciliador=conciliador)
                if esta_bloqueado:
                    bloqueo = esta_bloqueado.bloqueo
                else:
                    bloqueo = False;
            except conciliadorbloquedo.DoesNotExist:
                bloqueo = False
            turno = turnos.objects.filter(usuario = conciliador, status='PRO').first()
            sala_audiencia = AudienciaAPI.objects.filter(user = conciliador, fecha_audiencia=hoy).first()
            observacion = justificaciones.objects.filter(user=conciliador, fecha__lt= hora_fin, fecha__gte=hora_inicio).first()
            if sala_audiencia:
                sala_del_conciliador = sala_audiencia.sala_audiencia
            else:
                try:
                    mesa_conciliador =  mesa.objects.get(user = conciliador)
                    if mesa_conciliador:
                        sala_del_conciliador = mesa_conciliador.mesa
                    else:
                        sala_del_conciliador = "No Asignada"
                except mesa.DoesNotExist:
                    sala_del_conciliador = "No Asignada"
                except conciliadorbloquedo.DoesNotExist:
                    bloqueo = False
            if observacion:
                justificacion_conciliador = observacion.mensaje
            else:
                justificacion_conciliador = "Ninguna"
            if not turno:
                audiencias = AudienciaAPI.objects.filter(user = conciliador, status_audiencia='En audiencia', fecha_audiencia=hoy).first()
                if not audiencias:
                    lista_conciliadores.append({'id': conciliador.id, "nombre" : conciliador.get_full_name(), "sala": sala_del_conciliador, "proceso" : "No Tiene", "observaciones" : justificacion_conciliador, 'bloqueo' : bloqueo,'pendientes':turnos_pendientes})
                else:
                    lista_conciliadores.append({'id': conciliador.id, "nombre" :conciliador.get_full_name(), "sala": sala_del_conciliador,"proceso": audiencias.expediente,  "observaciones" : justificacion_conciliador, 'bloqueo' : bloqueo,'pendientes':turnos_pendientes})
            else:
                lista_conciliadores.append({'id': conciliador.id, "nombre" :conciliador.get_full_name(), "sala": sala_del_conciliador, "proceso": turno.turno,  "observaciones" : justificacion_conciliador, 'bloqueo' : bloqueo, 'pendientes':turnos_pendientes})
        return JsonResponse({"conciliadores": lista_conciliadores})
    else:
        return JsonResponse({"error" : "metodo no permitido"})
        



def turnos_auxiliares(request):
    turnosn = turnos.objects.filter( Q(status = 'PRO') | Q(status = 'PEN') | Q(status='NOT'), area='1').annotate(
        status_order=Case(
            When(status='NOT', then=Value(1)),
            When(status='PRO', then=Value(3)),
            default=Value(2),
            output_field=IntegerField(),
        )
    ).order_by('-id').select_related('usuario')

    turnos_data = []

    for turno in turnosn:
        ciudadanos_ids = ciudadanos.objects.filter(
        registro=turno.registro,
        tipo_persona="Soy Persona Trabajadora"
        ).values_list('id', flat=True)

        # Contando las solicitudes que tengan un ciudadano_id en los IDs obtenidos
        personas_count = Solicitud.objects.filter(
            Q(id_ciudadano__in=ciudadanos_ids),
            asistencia=True  # Aquí puedes especificar el valor del campo asistencia que deseas filtrar
        ).count()

        if personas_count == 0:
            personas_count = ciudadanos.objects.filter(
                registro=turno.registro,
                tipo_persona="Soy Persona Trabajadora",
            ).count()

        usuario_first_name = turno.usuario.first_name + " " + turno.usuario.last_name if turno.usuario else turno.usuario
        
        turno_info = {
            'id': turno.id,
            'turno': turno.turno,
            'status': turno.status,
            'estado_revisado': turno.estado_revisado,
            'hora_notificacion': turno.hora_notificacion,
            'personas_count': personas_count,
            'usuario': usuario_first_name,
        }
        turnos_data.append(turno_info)

    return JsonResponse({'turnos': turnos_data})





def pantalla_ratificaciones(request):
    hoy = pendulum.today()
    inicio_dia = hoy.start_of('day')
    fin_dia = hoy.end_of('day')
    mesas = mesa.objects.filter(area='1').select_related('user')
    turnosn = turnos.objects.filter(area='1', fecha__gte=inicio_dia, hora_fin_turno__lte=fin_dia).annotate(
        status_order=Case(
        When(status='NOT', then=Value(1)),
        When(status='PRO', then=Value(2)),
        default=Value(3),
        output_field=IntegerField(),
        )
    ).order_by('-hora_notificacion','status_order')

    for turno in turnosn:
        if "-" in turno.turno:
            turno.turno = turno.turno.split("-", 1)[-1]


    mesas_dict = {m.mesa: m for m in mesas}
    
    for turno in turnosn:
        personas_count = ciudadanos.objects.filter(registro=turno.registro, tipo_persona="Soy Persona Trabajadora").count()
        turno.personas_count = personas_count 
        if turno.mesa in mesas_dict:
            turno.mesa_obj = mesas_dict[turno.mesa]
        else:
            turno.mesa_obj = None

    turnosCan = turnosn.filter(status='CAN').count()
    turnosFin = turnosn.filter(status='FIN').count()
    turnosPen = turnosn.filter(status='PEN').count()
    
    contexto = {
        'turnos': turnosn,
        'turnosPen': turnosPen,
        'turnosCan': turnosCan,
        'turnosFin': turnosFin,
        'mesas': mesas,
    }
    
    return render(request, 'ratificacion/dashboard.html', contexto)




def conteo_por_asesor(request):
    hoy = pendulum.today()
    inicio_dia = hoy.start_of('day')
    fin_dia = hoy.end_of('day')

    asesorias = asesoriaJuridica.objects.filter(
        turno_id__fecha__gte=inicio_dia, 
        turno_id__hora_fin_turno__lte=fin_dia
    ).values('user__username', 'user__first_name', 'user__last_name').annotate(
        total_folio=Count(
            Case(
                # Cambiar conclusion__conclusion a conclusion__conclusion_exitosa
                When(conclusion__conclusion_exitosa__in=['si'], then=1),
                output_field=IntegerField(),
            )  
        ),
        total_sin_folio=Count(
            Case(
                # Cambiar conclusion__conclusion a conclusion__conclusion_exitosa
                When(conclusion__conclusion_exitosa__in=['no', 'Otra Area'], then=1),
                output_field=IntegerField(),
            )
        )
    )

    turnos_contados = asesoriaJuridica.objects.filter(
        turno_id__fecha__gte=inicio_dia, 
        turno_id__hora_fin_turno__lte=fin_dia
    ).values('user__username').annotate(
        total_turnos=Count('operacion_id')
    )

    turnos_dict = {item['user__username']: item['total_turnos'] for item in turnos_contados}

    asesoria_data = []
    for data in asesorias:
        username = data['user__username']
        fullname = f"{data['user__first_name']} {data['user__last_name']}"
        asesoria_data.append({
            'user__username': fullname,
            'total_folio': data['total_folio'],
            'total_sin_folio': data['total_sin_folio'],
            'total_turnos': turnos_dict.get(username, 0),
            
        })


    return JsonResponse(asesoria_data, safe=False)



######################################################################################################
def asesoria_metricas_dashboard(request):
    hoy = pendulum.today()
    inicio_dia = hoy.start_of('day')
    fin_dia = hoy.end_of('day')
    ahora = pendulum.now()  # Obtener el tiempo actual

    convenios = conclusion.objects.filter(
        conclusion_exitosa='si',
        id_asesoria__turno_id__fecha__gte=inicio_dia,
        id_asesoria__turno_id__hora_fin_turno__lte=fin_dia
    ).count()

    turnosFin = asesoriaJuridica.objects.filter(
        turno_id__fecha__gte=inicio_dia,
        turno_id__hora_fin_turno__lte=fin_dia
    ).count()

    turnosCan = turnos.objects.filter(
        fecha__gte=inicio_dia,
        status='CAN',
        area=3
    ).count()

    noconvenios = conclusion.objects.filter(
        conclusion_exitosa__in=['no', 'Otra Area'],
        id_asesoria__turno_id__fecha__gte=inicio_dia,
        id_asesoria__turno_id__hora_fin_turno__lte=fin_dia
    ).count()

    total_turnos_dia = turnos.objects.filter(
        fecha__gte=inicio_dia,
        area=3
    ).count()

    turnos_del_dia = turnos.objects.filter(
        Q(status='FIN') | Q(status='PRO'),
        fecha__gte=inicio_dia,
        fecha__lte=fin_dia,
        area=3
    ).select_related('usuario').order_by('mesa', 'hora_notificacion')

    # Agrupar turnos por usuario
    usuarios_turnos = {}
    for turno in turnos_del_dia:
        if turno.usuario:
            if turno.usuario not in usuarios_turnos:
                usuarios_turnos[turno.usuario] = []
            usuarios_turnos[turno.usuario].append(turno)

    # Calcular tiempos de atención, sin atención, suma total y promedio por usuario
    resultado_usuarios = {}
    for usuario, turnos_usuario in usuarios_turnos.items():
        tiempos_atencion = []
        tiempos_sin_atencion = []
        tiempos_atencion_actual = []
        suma_atencion = 0  # Suma total del tiempo de atención
        suma_sin_atencion = 0  # Suma total del tiempo sin atención
        inicio_jornada = inicio_dia.replace(hour=8, minute=0)
        fin_jornada = inicio_dia.replace(hour=16, minute=0)

        fin_ultimo_turno = inicio_jornada
        fin_ultimo_turno_pro = None

        for turno in turnos_usuario:
            if turno.status == 'FIN':
                if turno.hora_notificacion:
                    tiempo_sin_atencion = turno.hora_notificacion - fin_ultimo_turno
                    if tiempo_sin_atencion.total_seconds() > 0:
                        suma_sin_atencion += tiempo_sin_atencion.total_seconds()
                        tiempos_sin_atencion.append({
                            'inicio': fin_ultimo_turno.isoformat(),
                            'fin': turno.hora_notificacion.isoformat(),
                            'duracion': tiempo_sin_atencion.total_seconds()
                        })

                    if turno.hora_fin_turno:
                        tiempo_atencion = turno.hora_fin_turno - turno.hora_notificacion
                        suma_atencion += tiempo_atencion.total_seconds()
                        tiempos_atencion.append({
                            'inicio': turno.hora_notificacion.isoformat(),
                            'fin': turno.hora_fin_turno.isoformat(),
                            'duracion': tiempo_atencion.total_seconds()
                        })
                        fin_ultimo_turno = turno.hora_fin_turno

            elif turno.status == 'PRO':
                if turno.hora_notificacion:
                    tiempo_sin_atencion = turno.hora_notificacion - fin_ultimo_turno
                    if tiempo_sin_atencion.total_seconds() > 0:
                        suma_sin_atencion += tiempo_sin_atencion.total_seconds()
                        tiempos_sin_atencion.append({
                            'inicio': fin_ultimo_turno.isoformat(),
                            'fin': turno.hora_notificacion.isoformat(),
                            'duracion': tiempo_sin_atencion.total_seconds()
                        })
                        fin_ultimo_turno_pro = turno.hora_notificacion

        if fin_ultimo_turno_pro and fin_ultimo_turno_pro < ahora:
            tiempo_actual = ahora - fin_ultimo_turno_pro
            tiempos_atencion_actual.append({
                'inicio': fin_ultimo_turno_pro.isoformat(),  
                'fin': ahora.isoformat(),
                'duracion': tiempo_actual.total_seconds()
            })
            suma_atencion += tiempo_actual.total_seconds()

        else:
            if fin_ultimo_turno < ahora:
                tiempo_sin_atencion = ahora - fin_ultimo_turno
                suma_sin_atencion += tiempo_sin_atencion.total_seconds()
                tiempos_sin_atencion.append({
                    'inicio': fin_ultimo_turno.isoformat(),
                    'fin': ahora.isoformat(),
                    'duracion': tiempo_sin_atencion.total_seconds()
                })

        # Calcular promedios
        total_turnos = len(turnos_usuario)
        promedio_atencion = suma_atencion / total_turnos if total_turnos > 0 else 0
        promedio_sin_atencion = suma_sin_atencion / total_turnos if total_turnos > 0 else 0

        # Asignar el resultado al usuario
        resultado_usuarios[usuario.username] = {
            'tiempos_atencion': tiempos_atencion,
            'tiempos_sin_atencion': tiempos_sin_atencion,
            'tiempos_atencion_actual': tiempos_atencion_actual,
            'suma_atencion': suma_atencion,
            'suma_sin_atencion': suma_sin_atencion,
            'promedio_atencion': promedio_atencion,
            'promedio_sin_atencion': promedio_sin_atencion
        }

    # Convertir el diccionario a JSON
    resultado_usuarios_json = json.dumps(resultado_usuarios)

    contexto = {
        'convenio': convenios,
        'noconvenio': noconvenios,
        'turnosFin': turnosFin,
        'turnosCan': turnosCan,
        'turnosTotal': total_turnos_dia,
        'resultado_usuarios_json': resultado_usuarios_json
    }

    return render(request, 'asesorias/asesoria_metricas.html', contexto)


##############################################################################################################

def ratificacion_metricas_dashboard(request):
    hoy = pendulum.today()
    inicio_dia = hoy.start_of('day')
    fin_dia = hoy.end_of('day')
    ahora = pendulum.now()  # Obtener el tiempo actual

    turnosFin = ratificacion.objects.filter(
        turno_id__fecha__gte=inicio_dia,
        turno_id__hora_fin_turno__lte=fin_dia
    ).count()

    turnosCan = turnos.objects.filter(
        fecha__gte=inicio_dia,
        status='CAN',
        area=1
    ).count()

    total_turnos_dia = turnos.objects.filter(
        fecha__gte=inicio_dia,
        area=1
    ).count()

    turnos_del_dia = turnos.objects.filter(
        Q(status='FIN') | Q(status='PRO'),
        fecha__gte=inicio_dia,
        fecha__lte=fin_dia,
        area=1
    ).select_related('usuario').order_by('mesa', 'hora_notificacion')

    # Agrupar turnos por usuario
    usuarios_turnos = {}
    for turno in turnos_del_dia:
        if turno.usuario:
            if turno.usuario not in usuarios_turnos:
                usuarios_turnos[turno.usuario] = []
            usuarios_turnos[turno.usuario].append(turno)

    # Calcular tiempos de atención, sin atención, suma total y promedio por usuario
    resultado_usuarios = {}
    for usuario, turnos_usuario in usuarios_turnos.items():
        tiempos_atencion = []
        tiempos_sin_atencion = []
        tiempos_atencion_actual = []
        suma_atencion = 0  # Suma total del tiempo de atención
        suma_sin_atencion = 0  # Suma total del tiempo sin atención
        inicio_jornada = inicio_dia.replace(hour=8, minute=0)
        fin_jornada = inicio_dia.replace(hour=16, minute=0)

        fin_ultimo_turno = inicio_jornada
        fin_ultimo_turno_pro = None

        for turno in turnos_usuario:
            if turno.status == 'FIN':
                if turno.hora_notificacion:
                    tiempo_sin_atencion = turno.hora_notificacion - fin_ultimo_turno
                    if tiempo_sin_atencion.total_seconds() > 0:
                        suma_sin_atencion += tiempo_sin_atencion.total_seconds()
                        tiempos_sin_atencion.append({
                            'inicio': fin_ultimo_turno.isoformat(),
                            'fin': turno.hora_notificacion.isoformat(),
                            'duracion': tiempo_sin_atencion.total_seconds()
                        })

                    if turno.hora_fin_turno:
                        tiempo_atencion = turno.hora_fin_turno - turno.hora_notificacion
                        suma_atencion += tiempo_atencion.total_seconds()
                        tiempos_atencion.append({
                            'inicio': turno.hora_notificacion.isoformat(),
                            'fin': turno.hora_fin_turno.isoformat(),
                            'duracion': tiempo_atencion.total_seconds()
                        })
                        fin_ultimo_turno = turno.hora_fin_turno

            elif turno.status == 'PRO':
                if turno.hora_notificacion:
                    tiempo_sin_atencion = turno.hora_notificacion - fin_ultimo_turno
                    if tiempo_sin_atencion.total_seconds() > 0:
                        suma_sin_atencion += tiempo_sin_atencion.total_seconds()
                        tiempos_sin_atencion.append({
                            'inicio': fin_ultimo_turno.isoformat(),
                            'fin': turno.hora_notificacion.isoformat(),
                            'duracion': tiempo_sin_atencion.total_seconds()
                        })
                        fin_ultimo_turno_pro = turno.hora_notificacion

        if fin_ultimo_turno_pro and fin_ultimo_turno_pro < ahora:
            tiempo_actual = ahora - fin_ultimo_turno_pro
            tiempos_atencion_actual.append({
                'inicio': fin_ultimo_turno_pro.isoformat(),  
                'fin': ahora.isoformat(),
                'duracion': tiempo_actual.total_seconds()
            })
            suma_atencion += tiempo_actual.total_seconds()

        else:
            if fin_ultimo_turno < ahora:
                tiempo_sin_atencion = ahora - fin_ultimo_turno
                suma_sin_atencion += tiempo_sin_atencion.total_seconds()
                tiempos_sin_atencion.append({
                    'inicio': fin_ultimo_turno.isoformat(),
                    'fin': ahora.isoformat(),
                    'duracion': tiempo_sin_atencion.total_seconds()
                })

        # Calcular promedios
        total_turnos = len(turnos_usuario)
        promedio_atencion = suma_atencion / total_turnos if total_turnos > 0 else 0
        promedio_sin_atencion = suma_sin_atencion / total_turnos if total_turnos > 0 else 0

        # Asignar el resultado al usuario
        resultado_usuarios[usuario.username] = {
            'tiempos_atencion': tiempos_atencion,
            'tiempos_sin_atencion': tiempos_sin_atencion,
            'tiempos_atencion_actual': tiempos_atencion_actual,
            'suma_atencion': suma_atencion,
            'suma_sin_atencion': suma_sin_atencion,
            'promedio_atencion': promedio_atencion,
            'promedio_sin_atencion': promedio_sin_atencion
        }

    # Convertir el diccionario a JSON
    resultado_usuarios_json = json.dumps(resultado_usuarios)

    contexto = {
        'turnosFin': turnosFin,
        'turnosCan': turnosCan,
        'turnosTotal': total_turnos_dia,
        'resultado_usuarios_json': resultado_usuarios_json
    }

    return render(request, 'ratificacion/conciliador/ratificaciones_metricas.html', contexto)

################################################################################################################





def conteo_por_conciliador(request):
    hoy = pendulum.today()
    inicio_dia = hoy.start_of('day')
    fin_dia = hoy.end_of('day')


    turnos_contados = ratificacion.objects.filter(
        turno_id__fecha__gte=inicio_dia, 
        turno_id__hora_fin_turno__lte=fin_dia
    ).values('user__username').annotate(
        total_turnos=Count('operacion_id')
    )

    turnos_contados_list = list(turnos_contados)
    return JsonResponse(turnos_contados_list, safe=False)



def ratificacion_dashboard(request):
    hoy = pendulum.today()
    inicio_dia = hoy.start_of('day')
    fin_dia = hoy.end_of('day')
    noconvenios = conclusionratificaciones.objects.filter(
        conclusion='No Concluido',
        id_ratificacion__turno_id__fecha__gte=inicio_dia,
        id_ratificacion__turno_id__hora_fin_turno__lte=fin_dia
    ).count()

    turnosFin = ratificacion.objects.filter(
        turno_id__fecha__gte=inicio_dia,
        turno_id__hora_fin_turno__lte=fin_dia
    ).count()

    convenios = conclusionratificaciones.objects.filter(
        conclusion__in=['Convenio Pago', 'Convenio Diferido'],
        id_ratificacion__turno_id__fecha__gte=inicio_dia,
        id_ratificacion__turno_id__hora_fin_turno__lte=fin_dia
    ).count()

    contexto = {
        'convenio': convenios,
        'noconvenio': noconvenios,
        'turnosFin': turnosFin
    }

    return render(request, 'ratificacion/ratis_dashboard.html', contexto)




@csrf_protect
def asignar_conciliador(request):
    if request.method == 'POST':
        turno_id = request.POST.get('turno_id')
        user_id = request.POST.get('user_id')
    
        
        try:
            turno = turnos.objects.get(id=turno_id)
            usuario = User.objects.get(id=user_id)
            mesan = mesa.objects.filter(user=usuario).first()
            if mesan:
                turno.mesa = mesan.mesa
            else:
                turno.mesa = None 
            turno.usuario = usuario
            turno.save()
            
            messages.success(request, 'El turno ha sido asignado correctamente.')
        except turnos.DoesNotExist:
            messages.error(request, 'El turno no fue encontrado.')
        except User.DoesNotExist:
            messages.error(request, 'El usuario no fue encontrado.')
        
        return HttpResponseRedirect(reverse('auxiliares_ratificacion'))
    else:
        messages.error(request, 'Método no permitido.')
        return HttpResponseRedirect(reverse('auxiliares_ratificacion'))
    

    

@csrf_exempt
def cambiar_status_turno(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        turno_id = data.get('turno_id')
        nuevo_status = data.get('nuevo_status')
        
        try:
            turno = turnos.objects.get(id=turno_id)
            if turno.status == nuevo_status:
                turno.notificacion = False
                turno.save()
            else:
                turno.status = nuevo_status
                if turno.status == 'NOT':
                    turno.hora_notificacion = timezone.now()
                elif turno.status == 'PRO' and not turno.hora_inicio_turno:
                    turno.hora_inicio_turno = timezone.now()
                elif turno.status in ['FIN', 'CAN']:
                    turno.hora_fin_turno = timezone.now()
                turno.save()
        except turnos.DoesNotExist:
            return JsonResponse({ 'message' : "no existe el turno" })
        return JsonResponse({'success' : "status cambiado correctamente"})
    return JsonResponse({'error':'Método no permitido.'})
    



@csrf_protect
def iniciar_turno_automatico(request):
    try:
        turnos_asignados = turnos.objects.filter(Q(status='NOT') | Q(status='PEN'), area=1,)
        ahora = pendulum.now()
        turnos_actualizados = 0
        for turno in turnos_asignados:
            if turno.usuario is None:
                continue
            else:
                if turno.fecha < ahora.subtract(minutes=15):
                    if not turno.hora_notificacion:
                        turno.hora_notificacion = ahora
                    turno.hora_inicio_turno = ahora
                    turno.status = 'PRO'
                    turno.save()
                    turnos_actualizados += 1
        if turnos_actualizados > 0:
            return JsonResponse({'message': f'Se actualizaron {turnos_actualizados} turnos.'}, status=200)
        else:
            return JsonResponse({'message': 'No hay turnos para actualizar.'}, status=200)
    except Exception as e:
        return JsonResponse({'error': f'Ocurrió un error: {str(e)}'}, status=500)



def metricas_ratificacion(request):
    
    users = User.objects.all()
    mesas = mesa.objects.filter(area='1')
    turno = turnos.objects.filter(status='PEN',area='1')
    turnosCan = len(turnos.objects.filter(status='CAN',area='1'))
    turnosFin = len(turnos.objects.filter(status='FIN',area='1'))
    turnosPen = len(turnos.objects.filter(status='PEN',area='1'))
    
    # turnos = turnos.select_related('ciudadanoId').all()
    return render(request,'ratificacion/metricas.html',{'users' : users,'turnos': turno,'turnosPen': turnosPen,'turnosCan': turnosCan,'turnosFin': turnosFin,'mesas':mesas})





#################################################################### metodos de conciliador de ratificacion ############################################################################################


# Vistas para el conciliador area Ratificacion
# renderiza el template de conciliador
@login_required
def conciliador2(request):
    numeros_mesa = mesa.objects.filter(area=1)
    username = request.user.username
    return render(request, 'ratificacion/conciliador/ratificador.html',  {'numeros_mesa': numeros_mesa, 'username' : username})

@login_required
def conciliador(request):
    numeros_mesa = mesa.objects.filter(area=1)
    username = request.user.username
    return render(request, 'ratificacion/conciliador/conciliador.html',  {'numeros_mesa': numeros_mesa, 'username' : username})

#funcion para obtener los turnos unicamente del area de ratificacion o area 1
def obtener_turnosRati(request):
    turno = turnos.objects.filter(Q(status="PEN") | Q(status="NOT") | Q(status="PRO"), Q(area=1)).select_related('usuario')
    turno_list = turno.values(
        *[f.name for f in turnos._meta.fields],
        'usuario__id', 
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name'
    )
    return JsonResponse(list(turno_list), safe=False)


#funcion para obtener los turnos unicamente del area de asesoria o area 3
def obtener_turnos_ratificacion(request):
    turno = turnos.objects.filter(Q(status = "PEN") | Q(status = "NOT") | Q(status = "PRO"), Q(area=1),).values('id', 'turno', 'status', 'notificacion','mesa','estado_revisado', 'usuario')
    turno_list = list(turno)
    return JsonResponse(turno_list, safe=False) 



@csrf_exempt
def cancelar_turno_recepcion(request, turno_id):
    if request.method == 'POST':
        
        turno = get_object_or_404(turnos, id=turno_id)
        try:
            turno.status = 'CAN'
            turno.save()
            return JsonResponse({'message': 'Turno Cancelado con Exito'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Metodo no Permitido'}, status=405)



#websocket
def actualizar_turnosRati():
    channel_layer = get_channel_layer()
    turnos = obtener_turnos_rati()  
    async_to_sync(channel_layer.group_send)(
        "turnos",
        {
            "type": "send_turnos",
            "turnos": turnos,
        },
    )


def obtener_datos_ciudadano(ciudadano, asistencia):
    testigos_list = testigos.objects.filter(codigo_ciudadano=ciudadano.codigo_ciudadano)
    documentos = {
        'documento_3': None,
        'documento_4': None,
        'documento_5': None,
        'documento_6': None,
    }
    
    for testigo in testigos_list:
        documentos['documento_3'] = testigo.documento_3.url if testigo.documento_3 else documentos['documento_3']
        documentos['documento_4'] = testigo.documento_4.url if testigo.documento_4 else documentos['documento_4']
        documentos['documento_5'] = testigo.documento_5.url if testigo.documento_5 else documentos['documento_5']
        documentos['documento_6'] = testigo.documento_6.url if testigo.documento_6 else documentos['documento_6']

    return {
        'id_ciudadano': ciudadano.id,
        'nombre': ciudadano.nombre,
        'asistencia': asistencia,
        'documento_1': ciudadano.documento_1.url if ciudadano.documento_1 else None,
        'documento_2': ciudadano.documento_2.url if ciudadano.documento_2 else None,
        **documentos,
    }

def verificar_bloqueo_usuario(id_user):
    try:
        esta_bloqueado = conciliadorbloquedo.objects.get(conciliador=id_user.id)
        return esta_bloqueado.bloqueo
    except conciliadorbloquedo.DoesNotExist:
        return False

def obtener_turnos_rati():
    turno_preferente = turnos.objects.filter(
        Q(status='PEN', area=1, estado_revisado=True, preferente=True)
    ).order_by('id').first()

    if turno_preferente:
        return turno_preferente

    return turnos.objects.filter(
        Q(status='PEN', area=1, estado_revisado=True)
    ).order_by('id').first()

def buscar_turno_valido():
    for turno in obtener_turnos_rati():
        ciudadanos_asociados = ciudadanos.objects.filter(registro=turno.registro)
        contador = sum(1 for c in ciudadanos_asociados if c.tipo_persona == 'Soy Persona Trabajadora')
        if contador == 1:
            return turno  
    return None  



def llamar_turno_rati(request):
    mesa_activa = request.GET.get('mesa')
    user_id = request.GET.get('user')
    if mesa_activa == 'Sin Mesa':
        return JsonResponse({'error': 'No puedes llamar turnos sin mesa.'}, status=404)
    existe_usuario = User.objects.get(id=user_id)
    if existe_usuario:
        turno_activo = turnos.objects.filter(Q(status='PRO') | Q(status='NOT'), Q(area=1), usuario=existe_usuario).first()
    else:
        return JsonResponse({'error': 'No existe el usuario.'}, status=404)
    if turno_activo and turno_activo.registro:
        ciudadanos_asociados = ciudadanos.objects.filter(registro=turno_activo.registro)
        datos_ciudadanos = []

        for ciudadano in ciudadanos_asociados:
            if 'Fuente:' not in ciudadano.nombre:
                solicitud = Solicitud.objects.filter(id_ciudadano=ciudadano.id, registro=turno_activo.registro).last()
                asistencia = solicitud.asistencia if solicitud else True
                if asistencia:
                    datos_ciudadanos.append(obtener_datos_ciudadano(ciudadano, asistencia))
        if not datos_ciudadanos:
            turno_activo.status = 'CAN'
            turno_activo.save()
            return JsonResponse({
                'error': f'Se te asignó el turno {turno_activo.turno}, pero fue cancelado por recepción. Llama un turno nuevo.'
            }, status=404)
        
        turno_data = {
            'hora_inicio': turno_activo.hora_notificacion,
            'id': turno_activo.id,
            'turno': turno_activo.turno,
            'status': turno_activo.status,
            'registro': turno_activo.registro,
            'area': turno_activo.area,
            'datosCiudadanos': datos_ciudadanos
        }
        return JsonResponse(turno_data)

    id_user = User.objects.get(id=user_id)
    if id_user:
        esta_bloqueado = verificar_bloqueo_usuario(id_user)
        
        if esta_bloqueado:
            turno = obtener_turnos_rati()  
            if turno and turno.registro:
                ciudadanos_asociados = ciudadanos.objects.filter(registro=turno.registro)
                contador = sum(1 for c in ciudadanos_asociados if c.tipo_persona == 'Soy Persona Trabajadora')

                if contador > 1:
                    turno = buscar_turno_valido() 
                    if not turno:
                        return JsonResponse({"error": "No hay turnos por el momento, tu perfil esta bloqueado para solo atender turnos de 1 trabajador"}, status=404)

                datos_ciudadanos = [
                    obtener_datos_ciudadano(ciudadano, solicitud.asistencia if (solicitud := Solicitud.objects.filter(id_ciudadano=ciudadano.id, registro=turno.registro).last()) else True)
                    for ciudadano in ciudadanos_asociados if 'Fuente:' not in ciudadano.nombre
                ]

                turno_data = {
                    'hora_inicio': turno.hora_notificacion,
                    'id': turno.id,
                    'turno': turno.turno,
                    'status': turno.status,
                    'registro': turno.registro,
                    'area': turno.area,
                    'datosCiudadanos': datos_ciudadanos
                }
                return JsonResponse(turno_data)
            else:
                return JsonResponse({'error': 'Aún no hay turnos disponibles'}, status=404)

        turno = obtener_turnos_rati()
        if turno and turno.registro:
            ciudadanos_asociados = ciudadanos.objects.filter(registro=turno.registro)
            datos_ciudadanos = [
                obtener_datos_ciudadano(ciudadano, solicitud.asistencia if (solicitud := Solicitud.objects.filter(id_ciudadano=ciudadano.id, registro=turno.registro).last()) else True)
                for ciudadano in ciudadanos_asociados if 'Fuente:' not in ciudadano.nombre
            ]

            turno_data = {
                'hora_inicio': turno.hora_notificacion,
                'id': turno.id,
                'turno': turno.turno,
                'status': turno.status,
                'registro': turno.registro,
                'area': turno.area,
                'datosCiudadanos': datos_ciudadanos
            }
            return JsonResponse(turno_data)
    return JsonResponse({"error": "No se pudo asignar un turno"}, status=404)



####################################################### funcion para llamar un turno que esta pendiente en ratificaciones ###########################################################################################################
def llamar_turno_ratis(request):
    mesa_activa = request.GET.get('mesa')
    if mesa_activa == 'Sin Mesa':
        return JsonResponse({'error': 'No puedes llamar turnos sin mesa.'}, status=404)
    turno_activo = turnos.objects.filter(Q(status='PRO') | Q(status='NOT'), Q(area=1), mesa=mesa_activa).first()
    if turno_activo and turno_activo.registro:
        ciudadanos_asociados = ciudadanos.objects.filter(registro=turno_activo.registro).select_related()
        datos_ciudadanos = []
        if ciudadanos_asociados.exists():
            for ciudadano in ciudadanos_asociados:
                if 'Fuente:' not in ciudadano.nombre:
                    solicitud = Solicitud.objects.filter(id_ciudadano = ciudadano.id, registro = turno_activo.registro).last()
                    if solicitud is None:
                        asistencia = True
                    else:
                        asistencia = solicitud.asistencia
                    if asistencia:
                        testigos_list = testigos.objects.filter(codigo_ciudadano=ciudadano.codigo_ciudadano)

                        # Inicializa los documentos como None
                        documento_3 = None
                        documento_4 = None
                        documento_5 = None
                        documento_6 = None

                        # Si hay testigos, intenta asignar los documentos
                        for testigo in testigos_list:
                            if testigo.documento_3:
                                documento_3 = testigo.documento_3.url
                            if testigo.documento_4:
                                documento_4 = testigo.documento_4.url
                            if testigo.documento_5:
                                documento_5 = testigo.documento_5.url
                            if testigo.documento_6:
                                documento_6 = testigo.documento_6.url

                        datos_ciudadanos.append({
                            'id_ciudadano': ciudadano.id,
                            'nombre': ciudadano.nombre,
                            'asistencia' : asistencia,
                            'documento_1': ciudadano.documento_1.url if ciudadano.documento_1 else None,
                            'documento_2': ciudadano.documento_2.url if ciudadano.documento_2 else None,
                            'documento_3': documento_3,
                            'documento_4': documento_4,
                            'documento_5': documento_5,
                            'documento_6': documento_6,
                        })
        else:
            turno_activo.status = 'CAN'
            turno.activo.save()  
            return JsonResponse({'error': f'se te asigno el turno {turno_activo.turno} pero este fue cancelado por recepcion, llama un turno nuevo.'}, status=404)

        turno_data = {
            'hora_inicio': turno_activo.hora_notificacion,
            'turno' : turno_activo,
            'id': turno_activo.id,
            'turno': turno_activo.turno,
            'status': turno_activo.status,
            'registro': turno_activo.registro,
            'area': turno_activo.area,
            'datosCiudadanos': datos_ciudadanos
        }
        return JsonResponse(turno_data)
    
############################################## else de la misma funcion #######################################################################################################
    else:
        id_user = mesa.objects.filter(mesa=mesa_activa).first()
        if id_user:
            try:
                esta_bloqueado = conciliadorbloquedo.objects.get(conciliador=id_user.user.id)
                if esta_bloqueado.bloqueo:
                    print("si esta bloqueado")
                else:
                    print("no esta bloqueado")
            except conciliadorbloquedo.DoesNotExist:
                print("no existe")
        turno = turnos.objects.filter(Q(status='PEN', preferente=True, area=1, estado_revisado = True)).order_by('id').first()
        if not turno:
            turno = turnos.objects.filter(Q(status='PEN', preferente=False, area=1, estado_revisado = True)).order_by('id').first()
        if turno and turno.registro:
            ciudadanos_asociados = ciudadanos.objects.filter(registro=turno.registro)
            datos_ciudadanos = []
            contador=0
            if ciudadanos_asociados.exists():
                for ciudadano in ciudadanos_asociados:
                    if 'Fuente:' not in ciudadano.nombre:
                        
                        solicitud = Solicitud.objects.filter(id_ciudadano = ciudadano.id, registro= turno.registro).last()
                        
                        if solicitud is None:
                            asistencia = True
                        else:
                            
                            asistencia = solicitud.asistencia
                        if asistencia:
                            if ciudadano.tipo_persona == 'Soy Persona Trabajadora':
                                contador += 1
                            testigos_list = testigos.objects.filter(registro=ciudadano.registro)

                            documento_3 = None
                            documento_4 = None
                            documento_5 = None
                            documento_6 = None

                            for testigo in testigos_list:
                                if testigo.documento_3:
                                    documento_3 = testigo.documento_3.url
                                if testigo.documento_4:
                                    documento_4 = testigo.documento_4.url
                                if testigo.documento_5:
                                    documento_5 = testigo.documento_5.url
                                if testigo.documento_6:
                                    documento_6 = testigo.documento_6.url

                            datos_ciudadanos.append({
                                'id_ciudadano': ciudadano.id,
                                'nombre': ciudadano.nombre,
                                'asistencia' : asistencia,
                                'documento_1': ciudadano.documento_1.url if ciudadano.documento_1 else None,
                                'documento_2': ciudadano.documento_2.url if ciudadano.documento_2 else None,
                                'documento_3': documento_3,
                                'documento_4': documento_4,
                                'documento_5': documento_5,
                                'documento_6': documento_6,
                            })
                            print("contador: ", contador)
                            if contador > 1 and esta_bloqueado.bloqueo:
                                turnoses = turnos.objects.filter(Q(status='PEN', preferente=True, area=1, estado_revisado = True))
                                if not turnoses:
                                    turnoses = turnos.objects.filter(Q(status='PEN', preferente=False, area=1, estado_revisado = True))
                                if not turnoses:
                                    return JsonResponse({"error" : "el turno tiene mas de 1 persona"})
                                for turno in turnoses: 
                                    if turno and turno.registro:
                                        ciudadanos_asociados = ciudadanos.objects.filter(registro=turno.registro)
                                        datos_ciudadanos = []
                                        contador=0
                                        if ciudadanos_asociados.exists():
                                            for ciudadano in ciudadanos_asociados:
                                                if 'Fuente:' not in ciudadano.nombre:
                                                    
                                                    solicitud = Solicitud.objects.filter(id_ciudadano = ciudadano.id, registro= turno.registro).last()
                                                    
                                                    if solicitud is None:
                                                        asistencia = True
                                                    else:
                                                        
                                                        asistencia = solicitud.asistencia
                                                    if asistencia:
                                                        if ciudadano.tipo_persona == 'Soy Persona Trabajadora':
                                                            contador += 1
                                                        testigos_list = testigos.objects.filter(registro=ciudadano.registro)

                                                        documento_3 = None
                                                        documento_4 = None
                                                        documento_5 = None
                                                        documento_6 = None

                                                        for testigo in testigos_list:
                                                            if testigo.documento_3:
                                                                documento_3 = testigo.documento_3.url
                                                            if testigo.documento_4:
                                                                documento_4 = testigo.documento_4.url
                                                            if testigo.documento_5:
                                                                documento_5 = testigo.documento_5.url
                                                            if testigo.documento_6:
                                                                documento_6 = testigo.documento_6.url

                                                        datos_ciudadanos.append({
                                                            'id_ciudadano': ciudadano.id,
                                                            'nombre': ciudadano.nombre,
                                                            'asistencia' : asistencia,
                                                            'documento_1': ciudadano.documento_1.url if ciudadano.documento_1 else None,
                                                            'documento_2': ciudadano.documento_2.url if ciudadano.documento_2 else None,
                                                            'documento_3': documento_3,
                                                            'documento_4': documento_4,
                                                            'documento_5': documento_5,
                                                            'documento_6': documento_6,
                                                        })
                                                        print("contador: ", contador)
                                                        if contador == 1 and esta_bloqueado.bloqueo:
                                                            break
                                                        else:
                                                            return JsonResponse({"error" : "el turno tiene mas de 1 persona"})
                                    else:
                                        return JsonResponse({"error" : "el turno tiene mas de 1 persona"})
            else:
                turno.status = 'CAN'
                turno.save()
                return JsonResponse({'error': f'se te asigno el turno {turno.turno} pero este fue cancelado por recepcion, llama un turno nuevo.'}, status=404)
                
            turno_data = {
                'hora_inicio' : turno.hora_notificacion,
                'id': turno.id,
                'area': turno.area if turno.area else None,
                'turno': turno.turno,
                'status': turno.status,
                'registro': turno.registro,
                'datosCiudadanos': datos_ciudadanos
            }
            
            return JsonResponse(turno_data)
        else:
            return JsonResponse({'error': 'Aun no hay turnos disponibles'}, status=404)

##############################################################################################################################################################################################################################  


# funcion para llamar un turno que esta pendiente
def llamar_turnoRati(request):
    usuario = request.GET.get('user')
    if usuario == 'null':
        return JsonResponse({'error': 'No puedes ver si tienes turnos asignados sin tener una mesa.'}, status=404)
    usuario_activo = User.objects.get(username=usuario)
    turno_activo = turnos.objects.filter(Q(status='PRO') | Q(status='NOT'), area=1, usuario=usuario_activo).first()
    if turno_activo:
        ciudadanos_asociados = ciudadanos.objects.filter(registro=turno_activo.registro)
        datos_ciudadanos = []
        for ciudadano in ciudadanos_asociados:
            folio = Solicitud.objects.filter(id_ciudadano=ciudadano.id, registro=ciudadano.registro).first()
            if folio:
                if folio.asistencia:
                    testigos_list = testigos.objects.filter(codigo_ciudadano=ciudadano.codigo_ciudadano)

                    documento_3 = None
                    documento_4 = None
                    documento_5 = None
                    documento_6 = None

                    for testigo in testigos_list:
                        if testigo.documento_3:
                            documento_3 = testigo.documento_3.url
                            
                        if testigo.documento_4:
                            documento_4 = testigo.documento_4.url
                        
                        if testigo.documento_5:
                            documento_5 = testigo.documento_5.url
                            
                        if testigo.documento_6:
                            documento_6 = testigo.documento_6.url
                    datos_ciudadanos.append({
                        'id_ciudadano': ciudadano.id,
                        'nombre': ciudadano.nombre,
                        'tipo_persona' : ciudadano.tipo_persona,
                        'documento_1': ciudadano.documento_1.url if ciudadano.documento_1 else None,
                        'documento_2': ciudadano.documento_2.url if ciudadano.documento_2 else None,
                        'documento_3': documento_3,
                        'documento_4': documento_4,
                        'documento_5': documento_5,
                        'documento_6': documento_6,
                    })
            else:
                testigos_list = testigos.objects.filter(codigo_ciudadano=ciudadano.codigo_ciudadano)
                documento_3 = None
                documento_4 = None
                documento_5 = None
                documento_6 = None
                for testigo in testigos_list:
                    if testigo.documento_3:
                        documento_3 = testigo.documento_3.url
                        
                    if testigo.documento_4:
                        documento_4 = testigo.documento_4.url
                        
                    if testigo.documento_5:
                        documento_5 = testigo.documento_5.url
                        
                    if testigo.documento_6:
                        documento_6 = testigo.documento_6.url
                        

                datos_ciudadanos.append({
                    'id_ciudadano': ciudadano.id,
                    'nombre': ciudadano.nombre,
                    'tipo_persona' : ciudadano.tipo_persona,
                    'documento_1': ciudadano.documento_1.url if ciudadano.documento_1 else None,
                    'documento_2': ciudadano.documento_2.url if ciudadano.documento_2 else None,
                    'documento_3': documento_3,
                    'documento_4': documento_4,
                    'documento_5': documento_5,
                    'documento_6': documento_6,
                })

        turno_data = {
            'id': turno_activo.id,
            'turno': turno_activo.turno,
            'status': turno_activo.status,
            'registro': turno_activo.registro,
            'area': turno_activo.area,
            'inicio': turno_activo.hora_notificacion,
            'datosCiudadanos': datos_ciudadanos
        }
        return JsonResponse(turno_data)
    else: # quiere decir aqui que no tiene turno abierto
        turno = turnos.objects.filter(Q(status='NOT'), area=1, usuario=usuario_activo).order_by('id').first()
        
        if turno:
            ciudadanos_asociados = ciudadanos.objects.filter(registro=turno.registro)
            datos_ciudadanos = []

            for ciudadano in ciudadanos_asociados:
                folio = Solicitud.objects.filter(id_ciudadano=ciudadano.id, registro=ciudadano.registro).first()

                if folio.asistencia:
                    testigos_list = testigos.objects.filter(registro=ciudadano.registro)

                    documento_3 = None
                    documento_4 = None
                    documento_5 = None
                    documento_6 = None

                    for testigo in testigos_list:
                        if testigo.documento_3:
                            documento_3 = testigo.documento_3.url
                        if testigo.documento_4:
                            documento_4 = testigo.documento_4.url
                        if testigo.documento_5:
                            documento_5 = testigo.documento_5.url
                        if testigo.documento_6:
                            documento_6 = testigo.documento_6.url

                    datos_ciudadanos.append({
                        'id_ciudadano': ciudadano.id,
                        'nombre': ciudadano.nombre,
                        'documento_1': ciudadano.documento_1.url if ciudadano.documento_1 else None,
                        'documento_2': ciudadano.documento_2.url if ciudadano.documento_2 else None,
                        'documento_3': documento_3,
                        'documento_4': documento_4,
                        'documento_5': documento_5,
                        'documento_6': documento_6,
                    })

            turno_data = {
                'id': turno.id,
                'area': turno.area if turno.area else None,
                'turno': turno.turno,
                'status': turno.status,
                'registro': turno.registro,
                'inicio': turno.hora_notificacion,
                'datosCiudadanos': datos_ciudadanos
            }
            
            return JsonResponse(turno_data)
        else:
            return JsonResponse({'error': 'No se encontraron turnos'}, status=404)
        






# funcion para validar si los conciliadores dejaron turnos abiertos y si es asi que los muestre primero para que los cierren
def validar_turnos_abiertosRati(request):
    usuario = request.GET.get('user')
    
    if usuario == 'undefined':
        return JsonResponse({'turno': 'none...'})
    else:
        usuario_activo = User.objects.filter(id = usuario).first()
        
        turno_activo = turnos.objects.filter(status='PRO', usuario=usuario_activo.id, area=1).first()
    if turno_activo:
        ciudadanos_en_turno = ciudadanos.objects.filter(registro=turno_activo.registro)
        nombres_ciudadanos = [ciudadano.nombre for ciudadano in ciudadanos_en_turno]
        turno_data = {
            'id': turno_activo.id,
            'turno': turno_activo.turno,
            'status': turno_activo.status,
            'nombreCiudadano': nombres_ciudadanos,  
            #'tipo_persona': ciudadanos_en_turno.tipo_persona
        }
        return JsonResponse(turno_data)
    else:
        return JsonResponse({'turno': 'none'})






# funcion para cambiar el status de un turno
@csrf_exempt
@require_http_methods(["PATCH"])
def cambiar_statusRati(request):
    if request.method == 'PATCH':
        try:
            data = json.loads(request.body)
            turnoactual = data.get('turno')
            registro = data.get('registro')
            nuevo_status = data.get('nuevoStatus')
            nueva_mesa = data.get('mesa')

        

            if not all([turnoactual, registro, nuevo_status, nueva_mesa]):
                return JsonResponse({'error': 'Faltan datos necesarios'}, status=400)

            cambio_status = turnos.objects.filter(id=turnoactual, registro=registro).first()
            
            if not cambio_status:
                return JsonResponse({'error': 'Registro no encontrado'}, status=404)

            # Verifica el estado actual y el nuevo estado
            if cambio_status.status == 'PEN' and nuevo_status == 'NOT':
                return JsonResponse({'message': 'Espera a que el auxiliar te asigne un turno'}, status=200)

            if cambio_status.status == 'NOT' and nuevo_status not in ['PRO', 'FIN', 'CAN']:
                return JsonResponse({'message': 'Da click en Iniciar Ratificación'}, status=200)

            # Actualiza el estado y la mesa solo si las validaciones pasan
            cambio_status.status = nuevo_status
            cambio_status.mesa = nueva_mesa

            if nuevo_status == 'NOT':
                cambio_status.hora_notificacion = timezone.now()
            elif nuevo_status == 'PRO':
                cambio_status.hora_inicio_turno = timezone.now()
            elif nuevo_status in ['FIN', 'CAN']:
                cambio_status.hora_fin_turno = timezone.now()

            cambio_status.save()
            return JsonResponse({'message': 'Turno Actualizado Correctamente'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Formato JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error interno del servidor: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    




    
#funcion para notificar el llamado de un turno
@csrf_exempt
@require_http_methods(["PATCH"])
def notificacion(request):
    try:
        data = json.loads(request.body)
        estado_notificacion = data.get('notificacion')
        turno_notificado = data.get('turno_id')

        if estado_notificacion is not None and turno_notificado:
            cambiar_notificacion = turnos.objects.get(id=turno_notificado)
            cambiar_notificacion.notificacion=estado_notificacion
            cambiar_notificacion.save()
            if cambiar_notificacion:
                return JsonResponse({'message': 'Estado de notificación actualizado correctamente'}, status=200)
            else:
                return JsonResponse({'error': 'No se encontró el turno especificado'}, status=404)
        else:
            return JsonResponse({'error': 'Faltan datos en la solicitud'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Error al parsear JSON'}, status=400)
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=500)
    



    
#funcion para mostrarle la mesa actual al conciliador
def miMesaRati(request):
    try:
        usuarioreq = request.GET.get('usuario')
        
        usuario = get_object_or_404(User,username=usuarioreq)
        mesas = mesa.objects.filter(user=usuario).first()
        if mesas:
            numero_mesa = mesas.mesa
            id_mesa = mesas.id
            return JsonResponse({'numero_mesa': numero_mesa, 'id_mesa' : id_mesa})
        else: 
            salas = sala.objects.filter(user=usuario).first()
            if salas:
                numero_sala = "Sala ", salas.sala
                id_sala = salas.id
                return JsonResponse({'numero_mesa': numero_sala, 'id_mesa' : id_sala})
            else:
                return JsonResponse({'numero_mesa': 'Sin Mesa'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
        
        
        

# funcion para asignar mesa al conciliador
@require_http_methods(["PATCH"])
@csrf_exempt
def asignarMesaRati(request):
    try:
        data = json.loads(request.body)
        conciliador = data.get('conciliador')
        mesanueva = data.get('mesa')
        print(mesanueva)

        if conciliador is None:
            return JsonResponse({'error': 'El campo "conciliador" es requerido'}, status=400)

        user = User.objects.get(username=conciliador)
        user_id = user.id

        # Caso 1: Desocupar la mesa actual del usuario
        if mesanueva == 0 or mesanueva == "0":
            mesa_actual_usuario = mesa.objects.filter(user=user_id, area=1).first()
            if mesa_actual_usuario:
                mesa_actual_usuario.user = None
                mesa_actual_usuario.save()
                return JsonResponse({'success': True, 'message': 'Mesa liberada correctamente'}, status=200)
            else:
                return JsonResponse({'error': 'El usuario no tiene asignada ninguna mesa'}, status=400)

        # Caso 2: Asignar nueva mesa
        mesa_obj_nueva = mesa.objects.get(mesa=mesanueva, area=1)

        # Verificar si la nueva mesa está ocupada por otro usuario
        if mesa_obj_nueva.user_id and mesa_obj_nueva.user_id != user_id:
            mesa_obj_nueva.user_id = None
            mesa_obj_nueva.save()

            

        # Desocupar la mesa actual si es diferente de la nueva
        mesa_actual_usuario = mesa.objects.filter(user=user_id).first()
        if mesa_actual_usuario and mesa_actual_usuario != mesa_obj_nueva:
            mesa_actual_usuario.user = None
            mesa_actual_usuario.save()

        # Asignar la nueva mesa al usuario
        mesa_obj_nueva.user = user
        mesa_obj_nueva.save()

        return JsonResponse({'success': True, 'message': 'Mesa asignada con éxito', 'user_id': user_id})

    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado: ' + conciliador}, status=404)
    except mesa.DoesNotExist:
        return JsonResponse({'error': 'Mesa no encontrada, pide que la agreguen en sistema'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  
    



#funcion para iniciar la conciliador
@csrf_exempt
def iniciar_conciliacion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=200)

        user_conciliador = data.get('conciliador_id')
        mesa_id = data.get('mesa')
        turno_id = data.get('turno')
        area_id = data.get('area')
        registro = data.get('registro')
        

        if not all([user_conciliador, turno_id, area_id, registro]):
            return JsonResponse({'error': 'Faltan datos por capturar'}, status=400)

        try:
            user_instance = User.objects.get(id=user_conciliador)
            mesa_instance = mesa.objects.filter(id=mesa_id).first()
            turno_instance = turnos.objects.get(id=turno_id)
            ciudadanos_instances = ciudadanos.objects.filter(registro=registro)

            if not ciudadanos_instances.exists():
                return JsonResponse({'error': 'Ciudadano no encontrado'}, status=404)

        except User.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404) 
        except mesa.DoesNotExist:
            return JsonResponse({'error': 'Mesa no encontrada'}, status=404)
        except turnos.DoesNotExist:
            return JsonResponse({'error': 'Turno no encontrado'}, status=404)

        try:
            with transaction.atomic():
                for ciudadano_instance in ciudadanos_instances:
                    conciliador_obj, created = ratificacion.objects.update_or_create(
                        user=user_instance,
                        #mesa=mesa_instance,
                        turno_id=turno_instance,
                        area_id=area_id,
                        registro=registro,
                        defaults={
                            'hora_entrada': pendulum.now()
                        }
                    )
                    if created:
                        response_data = {
                            'mensaje': 'Ratificacion Iniciada'
                        }
                    else:
                        response_data = {
                            'mensaje': 'La ratificación se ha actualizado para este usuario.'
                        }
                return JsonResponse(response_data, status=201 if created else 200)

        except IntegrityError as e:
            return JsonResponse({'error': 'Error al iniciar la ratificación: ' + str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)



@csrf_exempt
def terminar_conciliacion(request):
    if request.method == 'PATCH':
        try:
            data = json.loads(request.body)
            general_data = data.get('general', {})
            
            turno_id = general_data.get('turno_id')
            registro_ciudadano = general_data.get('registro')
        
            if  not turno_id or not registro_ciudadano:
                return JsonResponse({'error': 'Datos incompletos en general'}, status=400)

            conciliacion_obj = ratificacion.objects.filter(registro=registro_ciudadano).last()
            if not conciliacion_obj:
                
                return JsonResponse({'error': 'Registro de ratificación no encontrado'}, status=200)

            response_data = {'mensaje': 'Ratificación concluida correctamente. '}
            return JsonResponse(response_data, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)  




    
@csrf_exempt
def actualizar_estado(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        turno_id = data.get('turno_id')
        

        try:
            turno = turnos.objects.get(id=turno_id)
            if turno.estado_revisado:
                turno.estado_revisado = False
            else: 
                turno.estado_revisado = True
            
            turno.status = 'PEN'
            turno.save()

            return JsonResponse({'success': True})

        except turnos.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Turno no encontrado'})

    return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    
    

# Editar (añadir o quitar ciudadanos de un turno)
def turnos_dia_actual(request):
    # Obtener la fecha actual
    fecha_actual = date.today()
    
    # Filtrar los turnos por la fecha actual ignorando la hora
    lista_turnos = turnos.objects.filter(fecha__date=fecha_actual)
    
    informacion_turnos = []
    
    # Iterar sobre los turnos para obtener los ciudadanos asociados
    for turno in lista_turnos:
        # Separar los códigos de ciudadanos en una lista separados por espacios o comas
        codigos_ciudadanos = turno.codigo_ciudadano.split()
        
        # Buscar todos los ciudadanos cuyos códigos coincidan
        ciudadanos_asociados = ciudadanos.objects.filter(codigo_ciudadano__in=codigos_ciudadanos)
        
        # Crear una lista de nombres de los ciudadanos
        nombres_ciudadanos = [ciudadano.nombre for ciudadano in ciudadanos_asociados]
        
        # Añadir la información del turno
        informacion_turnos.append({
            'turno': turno.turno,
            'area': turno.get_area_display(),
            'fecha': turno.fecha,
            'codigo_ciudadano': turno.codigo_ciudadano,
            'nombres_ciudadanos': ', '.join(nombres_ciudadanos),
            'status': turno.get_status_display(),
        })
    
    context = {
        'informacion_turnos': informacion_turnos,
    }
    
    return render(request, 'turnos/recepcion/turnos_dia_actual.html', context)


def buscar_ciudadano_turno(request):
    query = request.GET.get('q', '')
    if query:
        ciudadanos_encontrados = ciudadanos.objects.filter(nombre__icontains=query)
    else:
        ciudadanos_encontrados = ciudadanos.objects.none()
    
    # Devuelve los resultados junto con el código del ciudadano
    results = [{'id': c.id, 'nombre': c.nombre, 'codigo_ciudadano': c.codigo_ciudadano} for c in ciudadanos_encontrados]
    return JsonResponse(results, safe=False)


def agregar_ciudadano_turno(request):
    if request.method == 'POST':
        turno_codigo = request.POST.get('turno_id')
        ciudadano_id = request.POST.get('ciudadano_id')
        area_nombre = request.POST.get('area')
        fecha_actual = datetime.now().date()

        if not turno_codigo or not ciudadano_id or not area_nombre:
            return render(request, 'turnos/recepcion/turnos_dia_actual.html', {'error': 'Datos incompletos'})

        # Convertir el nombre del área al valor numérico
        AREA_CHOICES = {
            'Ratificación': turnos.RATIFICACION,
            'Asesoría jurídica': turnos.ASESORIA_JURIDICA,
        }
        area = AREA_CHOICES.get(area_nombre)

        if area is None:
            print("Error: Área no válida")
            return render(request, 'turnos/recepcion/turnos_dia_actual.html', {'error': 'Área no válida'})

        try:
            # Buscar el turno por su código, área y fecha
            turnos_encontrados = turnos.objects.filter(turno=turno_codigo, area=area, fecha__date=fecha_actual)

            if turnos_encontrados.count() > 1:
                print("Error: Se encontraron múltiples turnos con la misma fecha")
                return render(request, 'turnos/recepcion/turnos_dia_actual.html', {'error': 'Se encontraron múltiples turnos con la misma fecha'})
            elif turnos_encontrados.count() == 0:
                print("Error: Turno no encontrado")
                return render(request, 'turnos/recepcion/turnos_dia_actual.html', {'error': 'Turno no encontrado'})
            
            turno = turnos_encontrados.first()
            ciudadano = ciudadanos.objects.get(id=ciudadano_id)

            # Añadimos el código del ciudadano al turno
            turno.codigo_ciudadano = f"{turno.codigo_ciudadano} {ciudadano.codigo_ciudadano}".strip()
            turno.save()

            # Asignar el número de registro al ciudadano
            ciudadano.registro = turno.registro
            ciudadano.save()

        except turnos.DoesNotExist:
            return render(request, 'turnos/recepcion/turnos_dia_actual.html', {'error': 'Turno no encontrado'})
        except ciudadanos.DoesNotExist:
            return render(request, 'turnos/recepcion/turnos_dia_actual.html', {'error': 'Ciudadano no encontrado'})

        # Después de eliminar el ciudadano, recargar los turnos y obtener los nombres de los ciudadanos
        lista_turnos = turnos.objects.filter(fecha__date=fecha_actual)
        informacion_turnos = []

        for turno in lista_turnos:
            # Obtener los códigos de ciudadanos en el turno
            codigos_ciudadanos_turno = turno.codigo_ciudadano.split()

            # Buscar todos los ciudadanos cuyos códigos coincidan
            ciudadanos_asociados = ciudadanos.objects.filter(codigo_ciudadano__in=codigos_ciudadanos_turno)

            # Crear una lista de nombres de los ciudadanos
            nombres_ciudadanos = [ciudadano.nombre for ciudadano in ciudadanos_asociados]

            # Añadir la información del turno a la lista
            informacion_turnos.append({
                'turno': turno.turno,
                'area': turno.get_area_display(),
                'fecha': turno.fecha,
                'codigo_ciudadano': turno.codigo_ciudadano,
                'nombres_ciudadanos': ', '.join(nombres_ciudadanos),
                'status': turno.get_status_display(),
            })

        return render(request, 'turnos/recepcion/turnos_dia_actual.html', {'informacion_turnos': informacion_turnos})

    return redirect('turnos_dia_actual')


def quitar_ciudadano_de_turno(request):
    if request.method == 'POST':
        # Datos enviados desde el formulario
        turno_codigo = request.POST.get('turno_id')
        nombre_seleccionado = request.POST.get('nombre_seleccionado')
        area = request.POST.get('area-remove')
        fecha_actual = datetime.now().date() 


        # Convertir el nombre del área al valor numérico
        AREA_CHOICES = {
            'Ratificación': turnos.RATIFICACION,
            'Asesoría jurídica': turnos.ASESORIA_JURIDICA,
        }
        area = AREA_CHOICES.get(area)

        if area is None:
            print("Error: Área no válida")
            return render(request, 'turnos/recepcion/turnos_dia_actual.html', {'error': 'Área no válida'})


        # Buscar los turnos por su código, área y fecha
        turnos_encontrados = turnos.objects.filter(turno=turno_codigo, area=area, fecha__date=fecha_actual)

        if turnos_encontrados.count() > 1:
            print("Error: Se encontraron múltiples turnos con la misma fecha")
            return render(request, 'turnos/recepcion/turnos_dia_actual.html', {'error': 'Se encontraron múltiples turnos con la misma fecha'})
        elif turnos_encontrados.count() == 0:
            print("Error: Turno no encontrado")
            return render(request, 'turnos/recepcion/turnos_dia_actual.html', {'error': 'Turno no encontrado'})
        
        turno = turnos_encontrados.first()

    

        # Buscar el ciudadano por nombre
        ciudadanos_encontrados = ciudadanos.objects.filter(nombre__icontains=nombre_seleccionado)

        if not ciudadanos_encontrados:
            print("Error: Ciudadano no encontrado por nombre")
            return render(request, 'turnos/recepcion/turnos_dia_actual.html', {'error': 'Ciudadano no encontrado por nombre'})

        # Procesar el ciudadano encontrado (suponiendo que puede haber más de uno)
        ciudadano_a_quitar = ciudadanos_encontrados.first()

        # Obtener el código del ciudadano
        codigo_ciudadano_a_quitar = ciudadano_a_quitar.codigo_ciudadano


        # Obtener los códigos de ciudadanos en el turno
        codigos_ciudadanos_turno = turno.codigo_ciudadano.split()
    

        # Verificar que el código del ciudadano esté en la lista de códigos del turno
        if codigo_ciudadano_a_quitar not in codigos_ciudadanos_turno:
            print("Error: El código del ciudadano no está en la lista de códigos del turno")
            return render(request, 'turnos/recepcion/turnos_dia_actual.html', {'error': 'Código del ciudadano no encontrado en el turno'})

        # Quitar el código del ciudadano de la lista en el turno
        codigos_ciudadanos_turno.remove(codigo_ciudadano_a_quitar)
        turno.codigo_ciudadano = " ".join(codigos_ciudadanos_turno).strip()
        turno.save()

    

        # 9. Asignar un nuevo número de registro único al ciudadano eliminado
        nuevo_registro = get_next_registro()  # Asegúrate de tener una función que genere un nuevo número de registro
        ciudadano_a_quitar.registro = nuevo_registro
        ciudadano_a_quitar.save()


        # Después de eliminar el ciudadano, recargar los turnos y obtener los nombres de los ciudadanos
        lista_turnos = turnos.objects.filter(fecha__date=fecha_actual)
        informacion_turnos = []

        for turno in lista_turnos:
            # Obtener los códigos de ciudadanos en el turno
            codigos_ciudadanos_turno = turno.codigo_ciudadano.split()

            # Buscar todos los ciudadanos cuyos códigos coincidan
            ciudadanos_asociados = ciudadanos.objects.filter(codigo_ciudadano__in=codigos_ciudadanos_turno)

            # Crear una lista de nombres (ciudadanos)
            nombres_ciudadanos = [ciudadano.nombre for ciudadano in ciudadanos_asociados]

            # Añadir la información del turno a la lista
            informacion_turnos.append({
                'turno': turno.turno,
                'area': turno.get_area_display(),
                'fecha': turno.fecha,
                'codigo_ciudadano': turno.codigo_ciudadano,
                'nombres_ciudadanos': ', '.join(nombres_ciudadanos),
                'status': turno.get_status_display(),
            })

        return render(request, 'turnos/recepcion/turnos_dia_actual.html', {'informacion_turnos': informacion_turnos})

    return redirect('turnos_dia_actual')



def normalizar_nombre(nombre):
    nombre = nombre.lower()
    nombre = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode('ascii')
    nombre = nombre.replace('.', '').replace(',', '').strip()
    return nombre

# Cargar el archivo Excel
def cargar_datos(path):
    no_encontrados = []
    df = pd.read_excel(path, engine='openpyxl')
    df['FECHA'] = pd.to_datetime(df['FECHA']).dt.date
    df['HORA'] = pd.to_datetime(df['HORA'], format='%H:%M:%S').dt.time
    

    ciudadanos_bulk = []
    ciudadanos_to_update = []

    for index, row in df.iterrows():
        # Ignorar filas con valores vacíos
        if pd.isnull(row['EXPEDIENTE']) or pd.isnull(row['CITADO']) or pd.isnull(row['CONCILIADOR']) or pd.isnull(row['FECHA']) or pd.isnull(row['HORA']) or pd.isnull(row['SALA']) or pd.isnull(row['SOLICITANTE']):
            continue

        conciliador_name = row['CONCILIADOR']
        conciliador_name_normalizado = normalizar_nombre(conciliador_name)
        posibles_conciliadores = User.objects.annotate(
            nombre_completo=Concat('first_name', Value(' '), 'last_name')
        )
        posibles_conciliadores_normalizados = [
            normalizar_nombre(usuario.nombre_completo) for usuario in posibles_conciliadores
        ]

        if conciliador_name_normalizado in posibles_conciliadores_normalizados:
            index_match = posibles_conciliadores_normalizados.index(conciliador_name_normalizado)
            conciliador_user = posibles_conciliadores[index_match]
        else:
            conciliador_user = None
            if conciliador_name in no_encontrados:
                continue
            else:
                no_encontrados.append(conciliador_name)

        # Obtener o crear la audiencia
        expediente, created = Audiencia.objects.get_or_create(
            expediente=row['EXPEDIENTE'],
            defaults={
                'fecha_audiencia': row['FECHA'],
                'hora_audiencia': row['HORA'],
                'sala_audiencia': row['SALA'],
                'conciliador_audiencia': row['CONCILIADOR'],
                'user' : conciliador_user,
                'status_audiencia': 'Pendiente'
            }
        )

        # Si el expediente ya existe, actualiza los campos relacionados
        if not created:
            expediente.fecha_audiencia = row['FECHA']
            expediente.hora_audiencia = row['HORA']
            expediente.sala_audiencia = row['SALA']
            expediente.conciliador_audiencia = row['CONCILIADOR']
            expediente.user = conciliador_user
            expediente.status_audiencia = 'Pendiente'
            expediente.hora_inicio_audiencia = None
            expediente.hora_fin_audiencia = None
            expediente.save()

        # Procesar solicitantes
        solicitantes = row['SOLICITANTE'].split('/')
        for solicitante in solicitantes:
            codigo = generate_10_digit_code()
            ciudadano_queryset = ciudadanos.objects.filter(
                nombre=solicitante.strip(),
                expediente=expediente
            )

            if ciudadano_queryset.exists():
                ciudadano = ciudadano_queryset.first()
                ciudadano.asistencia = False
                ciudadanos_to_update.append(ciudadano)
            else:
                ciudadanos_bulk.append(ciudadanos(
                    nombre=solicitante.strip(),
                    expediente=expediente,
                    codigo_ciudadano=codigo,
                    tipo_persona="Persona Trabajadora"
                ))

        # Procesar citados
        if 'CITADO' in row and row['CITADO']:
            citados = row['CITADO'].split('/')  
            for citado in citados:
                codigo = generate_10_digit_code()
                ciudadano_queryset = ciudadanos.objects.filter(
                    nombre=citado.strip(),
                    expediente=expediente
                )

                if ciudadano_queryset.exists():
                    ciudadano = ciudadano_queryset.first()
                    ciudadano.asistencia = False
                    ciudadanos_to_update.append(ciudadano)
                else:
                    ciudadanos_bulk.append(ciudadanos(
                        nombre=citado.strip(),
                        expediente=expediente,
                        codigo_ciudadano=codigo,
                        tipo_persona="Persona Juridica empleadora"
                    ))

    # Realizar bulk insert y update
    if ciudadanos_bulk:
        ciudadanos.objects.bulk_create(ciudadanos_bulk)

    if ciudadanos_to_update:
        ciudadanos.objects.bulk_update(ciudadanos_to_update, ['asistencia'])

    return no_encontrados



@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            conciliadores_no_encontrados = cargar_datos(file)
            return render(request, 'audiencia/success_upload.html', {
                'conciliadores_no_encontrados': conciliadores_no_encontrados
            })
    else:
        form = UploadFileForm()
    return render(request, 'audiencia/cargaxls.html', {'form': form})




def obtener_dias_laborables(fecha_inicio, fecha_fin):
    dias_laborables = []
    fecha_actual = fecha_inicio
    while fecha_actual <= fecha_fin:
        if fecha_actual.weekday() < 5:  # De lunes a viernes (0-4)
            dias_laborables.append(fecha_actual)
        fecha_actual += timedelta(days=1)
    return dias_laborables

@login_required
def audiencias_auxiliares(request):
    return HttpResponseRedirect(reverse('audiencias_auxiliares_api'))

@login_required
def llamar_audiencia(request, audiencias_id):
    if request.method == 'POST':
        audiencia = get_object_or_404(Audiencia, id=audiencias_id)
        audiencia.status_audiencia = 'Llamando'
        audiencia.save()
    return HttpResponseRedirect(reverse('audiencias_auxiliares'))

def obtener_notificaciones(request):
    try:
        notificaciones = Notificacion.objects.filter(se_leyo=False).order_by('-creada_el')
        data = [{
            "id": notificacion.id,
            "expediente": notificacion.audiencia.expediente,
            "conciliador": notificacion.audiencia.conciliador_audiencia,
            "sala": notificacion.audiencia.sala_audiencia,
            "status": notificacion.audiencia.status_audiencia,
            'audiencias_id': notificacion.audiencia.id,
        } for notificacion in notificaciones]
        return JsonResponse({"notificaciones": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def notificacion_leida(request, notificacion_id):
    try:
        Notificacion.objects.filter(id=notificacion_id).update(se_leyo=True)
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def audiencia_asistencia(request, pk):
    # Obtener la audiencia por su id
    audiencia = get_object_or_404(Audiencia, id=pk)
    
    # Obtener todos los ciudadanos relacionados con la audiencia
    ciudadanos_relacionados = ciudadanos.objects.filter(expediente=audiencia)

    if request.method == 'POST':
        # Procesar el formulario: actualizar las asistencias
        if 'asistencias' in request.POST:
            for ciudadano in ciudadanos_relacionados:
                asistencia_checkbox = f'asistencia_{ciudadano.id}'
                # Verificamos si el checkbox fue marcado o no
                ciudadano.asistencia = asistencia_checkbox in request.POST
                ciudadano.save()

            # Agregar un mensaje de éxito después de actualizar las asistencias
            messages.success(request, 'Las asistencias se han actualizado con éxito.')

            # Redirigir a la misma página para mostrar el mensaje
            return HttpResponseRedirect(reverse('audiencia_asistencia', args=[pk]))
        if 'archivar' in request.POST:
            audiencia.status_audiencia = 'Archivada'
            audiencia.hora_fin_audiencia = timezone.now()
            audiencia.save()
            messages.success(request, 'La audiencia ha sido archivada.')
            return HttpResponseRedirect(reverse('audiencia_asistencia', args=[pk]))

    # Renderizar la página con la audiencia y los ciudadanos
    return render(request, 'audiencia/asistencias_audiencia.html', {
        'audiencia': audiencia,
        'ciudadanos_relacionados': ciudadanos_relacionados,
    })

@login_required
def celebrar_audiencia(request, pk):
    # Obtener la audiencia por su id
    usuario = request.user
    audiencia = get_object_or_404(Audiencia, id=pk)
    #estadisticas = Estadisticas.objects.get(user=request.user)
    
    # Obtener todos los ciudadanos relacionados con la audiencia
    ciudadanos_relacionados = ciudadanos.objects.filter(expediente=audiencia)

    if request.method == 'POST':
        # Revisar cuál botón fue presionado
        if 'iniciar' in request.POST:
            audiencia.status_audiencia = 'En audiencia'
            audiencia.hora_inicio_audiencia = timezone.now()
            messages.success(request, 'La audiencia ha comenzado.')
        elif 'concluir' in request.POST:
            audiencia.status_audiencia = 'Concluida'
            audiencia.hora_fin_audiencia = timezone.now()
            #estadisticas.audiencias_concluidas += 1
            messages.success(request, 'La audiencia ha sido concluida.')
        elif 'archivar' in request.POST:
            audiencia.status_audiencia = 'Archivada'
            audiencia.hora_fin_audiencia = timezone.now()
            #estadisticas.audiencias_archivadas += 1
            messages.success(request, 'La audiencia ha sido archivada.')

        # Guardar los cambios en la audiencia
        audiencia.save()
        #estadisticas.actualizar_promedios()
        #estadisticas.save()

        # Redirigir a la misma página para evitar reenvío del formulario
        return HttpResponseRedirect(reverse('celebrar_audiencia', args=[pk]))

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if audiencia.hora_inicio_audiencia:
            tiempo_transcurrido = timezone.now() - audiencia.hora_inicio_audiencia
            horas, remainder = divmod(tiempo_transcurrido.seconds, 3600)
            minutos, segundos = divmod(remainder, 60)
            tiempo_formateado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
            return JsonResponse({'tiempo': tiempo_formateado})
        else:
            return JsonResponse({'tiempo': '00:00:00'})

    # Renderizar la página con la audiencia y los ciudadanos
    return render(request, 'audiencia/audiencias_conciliador.html', {
        'audiencia': audiencia,
        'ciudadanos_relacionados': ciudadanos_relacionados,
    })

@login_required
def editar_audiencia(request, pk):
    # Obtener la audiencia por su id
    audiencia = get_object_or_404(Audiencia, id=pk)

    # Obtener todos los ciudadanos relacionados con la audiencia
    ciudadanos_relacionados = ciudadanos.objects.filter(expediente=audiencia)

    if request.method == 'POST':
        # Llenar el formulario con los datos enviados
        form = EditAudienciaForm(request.POST, instance=audiencia)
        if form.is_valid():
            # Guardar los cambios
            form.save()
            messages.success(request, 'Los datos de la audiencia se han actualizado correctamente.')
            return HttpResponseRedirect(reverse('editar_audiencia',args=[pk]))
    else:
        # Mostrar el formulario con los datos actuales
        form = EditAudienciaForm(instance=audiencia)

    return render(request, 'audiencia/audiencias_coordis.html', {'form': form, 'audiencia': audiencia, 'ciudadanos_relacionados':ciudadanos_relacionados})

@login_required
def asignar_auxiliar_api(request, pk):
    audiencia = get_object_or_404(AudienciaAPI, id=pk)
    usuario = request.user
    #estadisticas, created = Estadisticas.objects.get_or_create(user=usuario)

    if request.method == 'POST':
        # Asignar el usuario actual como auxiliar_audiencia
        audiencia.auxiliar_audiencia = request.user
        audiencia.auxiliar_asignado_el = timezone.now()
        audiencia.status_audiencia = 'En audiencia'
        audiencia.hora_inicio_audiencia = timezone.now()
        audiencia.save()

        #estadisticas.audiencias += 1
        #estadisticas.actualizar_promedios()

        # Redirigir a la vista de asistencia
        
        return HttpResponseRedirect(reverse('audiencia_asistencia_api', args=[pk]))
    return HttpResponse("Método no permitido", status=405)

# @login_required
# def pantalla_audiencia(request):
#     # Zona horaria de Guadalajara
#     tz = pytz.timezone('America/Mexico_City')
    
#     # Obtén la fecha y hora actual en la zona horaria local
#     ahora_utc = timezone.now()
#     ahora_local = ahora_utc.astimezone(tz)
#     ahora_local = ahora_local.replace(second=0, microsecond=0)  # Elimina segundos y microsegundos
#     hoy = ahora_local.date()
#     hora_actual = ahora_local.time()
#     time_threshold = timezone.now() - timedelta(seconds=30)

#     # Filtro para audiencias llamando (por fecha de hoy)
#     audiencias_llamando = Audiencia.objects.filter(
#         fecha_audiencia=hoy
#     ).filter(
#         Q(status_audiencia='Llamando') | 
#         Q(status_audiencia='En audiencia', status_changed_at__gte=time_threshold)
#     )       

#     # Filtro para audiencias pendientes que incluyan la hora actual (12:00 pm en adelante hasta una hora después)
#     audiencias_pendientes = Audiencia.objects.filter(
#         status_audiencia='Pendiente',
#         fecha_audiencia=hoy,
#         hora_audiencia__gte=hora_actual.replace(minute=0),  # Incluye toda la hora actual (desde xx:00)
#         hora_audiencia__lt=(ahora_local + timedelta(hours=1)).time()  # Menor a una hora más tarde
#     )

#     # Obtener la última audiencia asignada
#     audiencia_mostrada = Audiencia.objects.filter(
#         auxiliar_audiencia__isnull=False
#     ).order_by('-auxiliar_asignado_el').first()

#     context = {
#         'audiencias_llamando': audiencias_llamando,
#         'audiencias_pendientes': audiencias_pendientes,
#         'audiencia_mostrada': audiencia_mostrada,
#     }

    return render(request, 'audiencia/pantalla.html', context)

def audiencias_ajax_view(request):
    # Zona horaria de Guadalajara
    tz = pytz.timezone('America/Mexico_City')
    
    # Obtén la fecha y hora actual en la zona horaria local
    ahora_utc = timezone.now()
    ahora_local = ahora_utc.astimezone(tz)
    ahora_local = ahora_local.replace(second=0, microsecond=0)  # Elimina segundos y microsegundos
    hoy = ahora_local.date()
    hora_actual = ahora_local.time()
    time_threshold = timezone.now() - timedelta(seconds=30)

    # Filtro para audiencias llamando (por fecha de hoy)
    audiencias_llamando = Audiencia.objects.filter(
        fecha_audiencia=hoy,
        hora_audiencia__gte=hora_actual.replace(minute=0),  # Incluye toda la hora actual (desde xx:00)
        hora_audiencia__lt=(ahora_local + timedelta(hours=1)).time()  # Menor a una hora más tarde
    ).filter(
        Q(status_audiencia='Llamando') |
        Q(status_audiencia='En audiencia', status_changed_at__gte=time_threshold)
    )

    context = {
        'audiencias_llamando': audiencias_llamando,
    }

    # Renderiza solo el fragmento HTML que será actualizado por AJAX
    return render(request, 'audiencia/audiencias_fragment.html', context)

def audiencias_pendientes_ajax(request):
    # Zona horaria de Guadalajara
    tz = pytz.timezone('America/Mexico_City')
    
    # Obtén la fecha y hora actual en la zona horaria local
    ahora_utc = timezone.now()
    ahora_local = ahora_utc.astimezone(tz)
    ahora_local = ahora_local.replace(second=0, microsecond=0)  # Elimina segundos y microsegundos
    hoy = ahora_local.date()
    hora_actual = ahora_local.time()

    # Filtro para audiencias llamando (por fecha de hoy)
    audiencias_pendientes = Audiencia.objects.filter(
        status_audiencia='Pendiente',
        fecha_audiencia=hoy,
        hora_audiencia__gte=hora_actual.replace(minute=0),  # Incluye toda la hora actual (desde xx:00)
        hora_audiencia__lt=(ahora_local + timedelta(hours=1)).time()  # Menor a una hora más tarde
    )

    context = {
        'audiencias_pendientes': audiencias_pendientes,
    }

    # Renderiza solo el fragmento HTML que será actualizado por AJAX
    return render(request, 'audiencia/audiencias_pendientes_fragment.html', context)

def audiencia_mostrada_ajax(request):
    # Obtener la última audiencia asignada
    audiencia_mostrada = AudienciaAPI.objects.filter(
        auxiliar_audiencia__isnull=False
    ).order_by('-auxiliar_asignado_el').first()

    if audiencia_mostrada:
        auxiliar = audiencia_mostrada.auxiliar_audiencia
        context = {
            'audiencia_mostrada': {
                'id': audiencia_mostrada.id,
                'expediente': audiencia_mostrada.expediente,
                'fecha_audiencia': format(audiencia_mostrada.fecha_audiencia, 'd/m/Y'),
                'hora_audiencia': format(audiencia_mostrada.hora_audiencia, 'H:i A'),
                'sala_audiencia': str(audiencia_mostrada.sala_audiencia),
                'auxiliar_audiencia': {
                    'get_full_name': audiencia_mostrada.auxiliar_audiencia.get_full_name() if audiencia_mostrada.auxiliar_audiencia else None,
                    'image_url': auxiliar.profile.image.url if hasattr(auxiliar, 'profile') else None,
                },
            }
        }
    else:
        context = {'audiencia_mostrada': None}

    return JsonResponse(context, encoder=DjangoJSONEncoder)

@login_required
def consultar_estadisticas(request):
    usuario = request.user
    #estadisticas = get_object_or_404(Estadisticas, user=usuario)
    es_admin = request.user.groups.filter(name='Administrador').exists()
    conciliador_data = []

    if es_admin:
        grupo_seleccionado = request.GET.get('grupo', '')
        mesas = mesa.objects.all()

        if grupo_seleccionado:
            mesas = mesas.filter(user__groups__name=grupo_seleccionado)

        ahora = timezone.now()
        inicio_del_dia = ahora.replace(hour=0, minute=0, second=0, microsecond=0)

        for mesa_obj in mesas:
            turnos_del_dia = turnos.objects.filter(
                mesa=mesa_obj.mesa,
                hora_inicio_turno__gte=inicio_del_dia
            ).order_by('hora_inicio_turno')

            datos_mesa = []
            ultimo_fin = inicio_del_dia

            for turno in turnos_del_dia:
                # Tiempo sin atención antes del turno
                if ultimo_fin < turno.hora_inicio_turno:
                    datos_mesa.append({
                        'tipo': 'sin_atencion',
                        'inicio': ultimo_fin,
                        'fin': turno.hora_inicio_turno
                    })

                # Tiempo de atención
                datos_mesa.append({
                    'tipo': 'atencion',
                    'inicio': turno.hora_inicio_turno,
                    'fin': turno.hora_fin_turno if turno.status == 'FIN' else ahora,
                    'turno': turno.turno,
                    'status': turno.status
                })

                ultimo_fin = turno.hora_fin_turno if turno.status == 'FIN' else ahora

            # Tiempo sin atención después del último turno
            if ultimo_fin < ahora:
                datos_mesa.append({
                    'tipo': 'sin_atencion',
                    'inicio': ultimo_fin,
                    'fin': ahora
                })

            conciliador_data.append({
                'conciliador': f"{mesa_obj.user.get_full_name() if mesa_obj.user and mesa_obj.user.get_full_name() else 'Desconocido'} (Mesa {mesa_obj.mesa})",
                'datos': datos_mesa
            })

    return JsonResponse({'conciliador_data': conciliador_data, 'hay_datos': len(conciliador_data) > 0})

"""@login_required
def estadisticas(request):
    usuario = request.user
    #estadisticas_usuario = get_object_or_404(Estadisticas, user=usuario)
    es_admin = request.user.groups.filter(name='Administrador').exists()
    grupos = Group.objects.all()

    filtro = request.GET.get('filtro', '1')
    hoy = timezone.now().date()

    # Obtener estadísticas totales
    if es_admin:
        estadisticas_totales = Estadisticas.objects.aggregate(
            turnos_atendidos=Sum('turnos_atendidos'),
            turnos_cancelados=Sum('turnos_cancelados'),
            pagos_realizados=Sum('pagos_realizados'),
            pagos_no_realizados=Sum('pagos_no_realizados'),
            solicitudes_confirmadas=Sum('solicitudes_confirmadas'),
            solicitudes_no_confirmadas=Sum('solicitudes_no_confirmadas'),
            conciliaciones_exitosas=Sum('conciliaciones_exitosas'),
            conciliaciones_fallidas=Sum('conciliaciones_fallidas'),
            audiencias_concluidas=Sum('audiencias_concluidas'),
            audiencias_archivadas=Sum('audiencias_archivadas'),
        )
    else:
        estadisticas_totales = {
            'turnos_atendidos': estadisticas_usuario.turnos_atendidos,
            'turnos_cancelados': estadisticas_usuario.turnos_cancelados,
            'pagos_realizados': estadisticas_usuario.pagos_realizados,
            'pagos_no_realizados': estadisticas_usuario.pagos_no_realizados,
            'solicitudes_confirmadas': estadisticas_usuario.solicitudes_confirmadas,
            'solicitudes_no_confirmadas': estadisticas_usuario.solicitudes_no_confirmadas,
            'conciliaciones_exitosas': estadisticas_usuario.conciliaciones_exitosas,
            'conciliaciones_fallidas': estadisticas_usuario.conciliaciones_fallidas,
            'audiencias_concluidas': estadisticas_usuario.audiencias_concluidas,
            'audiencias_archivadas': estadisticas_usuario.audiencias_archivadas,
        }

    # Calcular el rango de fechas basado en el filtro
    if filtro == '1':  # Mes actual
        primer_dia_mes = hoy.replace(day=1)
    elif filtro == '2':  # Mes anterior
        primer_dia_mes = (hoy.replace(day=1) - timedelta(days=1)).replace(day=1)
    elif filtro == '3':  # Hace 2 meses
        primer_dia_mes = (hoy.replace(day=1) - timedelta(days=1)).replace(day=1)
        primer_dia_mes = (primer_dia_mes - timedelta(days=1)).replace(day=1)
    elif filtro == '4':  # Semanal
        primer_dia_mes = hoy - timedelta(days=hoy.weekday())
    else:
        primer_dia_mes = hoy.replace(day=1)  # Valor predeterminado

    ultimo_dia_mes = primer_dia_mes + timedelta(days=monthrange(primer_dia_mes.year, primer_dia_mes.month)[1] - 1)

    # Obtener fechas de semanas completas dentro del rango
    semanas = []
    fecha_actual = primer_dia_mes
    while fecha_actual <= ultimo_dia_mes:
        inicio_semana = fecha_actual - timedelta(days=fecha_actual.weekday())
        fin_semana = inicio_semana + timedelta(days=4)  # Viernes
        if fin_semana > ultimo_dia_mes:
            fin_semana = ultimo_dia_mes
        if isinstance(inicio_semana, datetime):
            inicio_semana = inicio_semana.date()
        if isinstance(fin_semana, datetime):
            fin_semana = fin_semana.date()
        semanas.append((inicio_semana, fin_semana))
        fecha_actual = fin_semana + timedelta(days=3)  # Siguiente lunes

    # Calcular total de días laborables entre fecha_mas_antigua y fecha_actual
    fecha_mas_antigua = Estadisticas.objects.aggregate(Min('fecha'))['fecha__min'] or timezone.now().date()
    fecha_actual = timezone.now().date()

    mexico_holidays = holidays.Mexico(years=range(fecha_mas_antigua.year, fecha_actual.year + 1))

    total_dias = (fecha_actual - fecha_mas_antigua).days + 1
    total_fines_semana = ((total_dias // 7) * 2) + max(0, (fecha_actual.weekday() - fecha_mas_antigua.weekday() + 1) % 7 - 5)
    total_festivos = sum(1 for d in mexico_holidays if fecha_mas_antigua <= d <= fecha_actual and d.weekday() < 5)
    total_dias_laborables = total_dias - total_fines_semana - total_festivos

    # Calcular total de audiencias
    if es_admin:
        total_audiencias = Estadisticas.objects.aggregate(
            total=Sum(F('audiencias_concluidas') + F('audiencias_archivadas'))
        )['total'] or 0
    else:
        total_audiencias = Estadisticas.objects.filter(user=usuario).aggregate(
            total=Sum(F('audiencias_concluidas') + F('audiencias_archivadas'))
        )['total'] or 0

    # Calcular promedio total de audiencias por día laborable
    promedio_total_audiencias_por_dia = total_audiencias / total_dias_laborables if total_dias_laborables > 0 else 0

    # Preparar listas para datos semanales
    datos_semanales = []

    # Pre-fetch de datos estadísticos semanales
    filtro_estadisticas = Q(fecha__range=[primer_dia_mes, ultimo_dia_mes])
    if not es_admin:
        filtro_estadisticas &= Q(user=usuario)

    estadisticas_semanales = Estadisticas.objects.filter(filtro_estadisticas).values(
        'fecha'
    ).annotate(
        pagos_realizados=Sum('pagos_realizados'),
        pagos_no_realizados=Sum('pagos_no_realizados'),
        solicitudes_confirmadas=Sum('solicitudes_confirmadas'),
        solicitudes_no_confirmadas=Sum('solicitudes_no_confirmadas'),
        conciliaciones_exitosas=Sum('conciliaciones_exitosas'),
        conciliaciones_fallidas=Sum('conciliaciones_fallidas'),
        audiencias_concluidas=Sum('audiencias_concluidas'),
        audiencias_archivadas=Sum('audiencias_archivadas'),
    )

    # Organizar estadísticas por semana
    estadisticas_por_semana = defaultdict(lambda: defaultdict(int))
    for stat in estadisticas_semanales:
        fecha = stat['fecha']
        if isinstance(fecha, datetime):
            fecha = fecha.date()
        for inicio_semana, fin_semana in semanas:
            if inicio_semana <= fecha <= fin_semana:
                semana_key = (inicio_semana, fin_semana)
                for key, value in stat.items():
                    if key != 'fecha':
                        estadisticas_por_semana[semana_key][key] += value
                break

    # Obtener turnos atendidos y cancelados por semana
    filtro_turnos = Q(fecha__range=[primer_dia_mes, ultimo_dia_mes], fecha__week_day__in=[2, 3, 4, 5, 6])
    if not es_admin:
        filtro_turnos &= Q(usuario=usuario)

    turnos_semanales = turnos.objects.filter(filtro_turnos).values('fecha', 'status')

    # Organizar turnos por semana
    turnos_por_semana = defaultdict(lambda: {'FIN': 0, 'CAN': 0})
    for turno in turnos_semanales:
        fecha = turno['fecha']
        status = turno['status']
        for inicio_semana, fin_semana in semanas:
            if inicio_semana <= fecha <= fin_semana:
                semana_key = (inicio_semana, fin_semana)
                turnos_por_semana[semana_key][status] += 1
                break

    # Construir datos para el contexto
    etiquetas_semana = []
    turnos_atendidos_semanal = []
    turnos_cancelados_semanal = []
    pagos_realizados_semanal = []
    pagos_no_realizados_semanal = []
    solicitudes_confirmadas_semanal = []
    solicitudes_no_confirmadas_semanal = []
    conciliaciones_exitosas_semanal = []
    conciliaciones_fallidas_semanal = []
    audiencias_concluidas_semanal = []
    audiencias_archivadas_semanal = []

    for inicio_semana, fin_semana in semanas:
        semana_key = (inicio_semana, fin_semana)
        etiqueta_semana = f"{inicio_semana.strftime('%d/%m')} al {fin_semana.strftime('%d/%m')}"
        etiquetas_semana.append(etiqueta_semana)

        # Turnos
        turnos_data = turnos_por_semana.get(semana_key, {'FIN': 0, 'CAN': 0})
        turnos_atendidos_semanal.append(turnos_data.get('FIN', 0))
        turnos_cancelados_semanal.append(turnos_data.get('CAN', 0))

        # Estadísticas
        stats = estadisticas_por_semana.get(semana_key, {})
        pagos_realizados_semanal.append(stats.get('pagos_realizados', 0))
        pagos_no_realizados_semanal.append(stats.get('pagos_no_realizados', 0))
        solicitudes_confirmadas_semanal.append(stats.get('solicitudes_confirmadas', 0))
        solicitudes_no_confirmadas_semanal.append(stats.get('solicitudes_no_confirmadas', 0))
        conciliaciones_exitosas_semanal.append(stats.get('conciliaciones_exitosas', 0))
        conciliaciones_fallidas_semanal.append(stats.get('conciliaciones_fallidas', 0))
        audiencias_concluidas_semanal.append(stats.get('audiencias_concluidas', 0))
        audiencias_archivadas_semanal.append(stats.get('audiencias_archivadas', 0))

    # Obtener estadísticas diarias para los últimos 5 días
    dias = [timezone.now().date() - timedelta(days=i) for i in range(5)]
    filtro_diario = Q(fecha__in=dias)
    if not es_admin:
        filtro_diario &= Q(user=usuario)

    estadisticas_diarias = Estadisticas.objects.filter(filtro_diario).values(
        'fecha'
    ).annotate(
        pagos_realizados=Sum('pagos_realizados'),
        solicitudes_confirmadas=Sum('solicitudes_confirmadas'),
        conciliaciones_exitosas=Sum('conciliaciones_exitosas'),
        audiencias_concluidas=Sum('audiencias_concluidas'),
    )

    estadisticas_por_dia = {stat['fecha']: stat for stat in estadisticas_diarias}

    pagos_diarios = []
    solicitudes_diarias = []
    conciliaciones_diarias = []
    audiencias_diarias = []

    for dia in dias:
        stat = estadisticas_por_dia.get(dia, {})
        pagos_diarios.append(stat.get('pagos_realizados', 0))
        solicitudes_diarias.append(stat.get('solicitudes_confirmadas', 0))
        conciliaciones_diarias.append(stat.get('conciliaciones_exitosas', 0))
        audiencias_diarias.append(stat.get('audiencias_concluidas', 0))

    context = {
        'hoy': dias[0],
        'ayer': dias[1],
        'hace_2_dias': dias[2],
        'hace_3_dias': dias[3],
        'hace_4_dias': dias[4],
        'pagos_hoy': pagos_diarios[0],
        'pagos_ayer': pagos_diarios[1],
        'pagos_hace_2_dias': pagos_diarios[2],
        'pagos_hace_3_dias': pagos_diarios[3],
        'pagos_hace_4_dias': pagos_diarios[4],
        'solicitudes_hoy': solicitudes_diarias[0],
        'solicitudes_ayer': solicitudes_diarias[1],
        'solicitudes_hace_2_dias': solicitudes_diarias[2],
        'solicitudes_hace_3_dias': solicitudes_diarias[3],
        'solicitudes_hace_4_dias': solicitudes_diarias[4],
        'conciliaciones_hoy': conciliaciones_diarias[0],
        'conciliaciones_ayer': conciliaciones_diarias[1],
        'conciliaciones_hace_2_dias': conciliaciones_diarias[2],
        'conciliaciones_hace_3_dias': conciliaciones_diarias[3],
        'conciliaciones_hace_4_dias': conciliaciones_diarias[4],
        'audiencias_hoy': audiencias_diarias[0],
        'audiencias_ayer': audiencias_diarias[1],
        'audiencias_hace_2_dias': audiencias_diarias[2],
        'audiencias_hace_3_dias': audiencias_diarias[3],
        'audiencias_hace_4_dias': audiencias_diarias[4],
        'turnos_atendidos_semanal': turnos_atendidos_semanal,
        'turnos_cancelados_semanal': turnos_cancelados_semanal,
        'pagos_realizados_semanal': pagos_realizados_semanal,
        'pagos_no_realizados_semanal': pagos_no_realizados_semanal,
        'solicitudes_confirmadas_semanal': solicitudes_confirmadas_semanal,
        'solicitudes_no_confirmadas_semanal': solicitudes_no_confirmadas_semanal,
        'conciliaciones_exitosas_semanal': conciliaciones_exitosas_semanal,
        'conciliaciones_fallidas_semanal': conciliaciones_fallidas_semanal,
        'audiencias_concluidas_semanal': audiencias_concluidas_semanal,
        'audiencias_archivadas_semanal': audiencias_archivadas_semanal,
        'filtro': filtro,
        'es_admin': es_admin,
        'etiquetas_semana': etiquetas_semana,
        'estadisticas_totales': estadisticas_totales,
        'grupos': grupos,
        'promedio_total_audiencias_por_dia': promedio_total_audiencias_por_dia,
        'estadisticas': estadisticas_usuario,
    }

    return render(request, 'general/estadisticas.html', context)"""


def upload_and_send(request):
    if request.method == 'POST' and request.FILES['myfile']:
        excel_file = request.FILES['myfile']
        data = pd.read_excel(excel_file)

        #variable formulario
        base_url = 'https://api.botmaker.com/v2.0/notifications' 
        access_token = 'eyJhbGciOiJIUzUxMiJ9.eyJidXNpbmVzc0lkIjoiY2VudHJvZGVjb25jaWxpYWNpb25sYWJvcmFsZGVsIiwibmFtZSI6IkVkbXVuZG8gTWFjaWVsIE1hcnRpbmV6IiwiYXBpIjp0cnVlLCJpZCI6IkZLNklaemZydVhUb2hHR3pTcGNEalVEUXB1QTMiLCJleHAiOjE4NzQ1MjQ0MTcsImp0aSI6IkZLNklaemZydVhUb2hHR3pTcGNEalVEUXB1QTMifQ.9GbwqZ06DowPg2ZbhvlWwJ55B3nk9BnHfUqhPZYm0PrtJX79CvDU5XXMutkT6J8I-0cMo9ZFO4fJewayu6vMfg'
        
        headers = {
            'Content-Type': 'application/json',
            'access-token': f'{access_token}' 
        }

        for index, row in data.iterrows():

            encuesta = row['encuesta']

            if encuesta == 1:
                #Formulario resolucion con convenio
                payload = {
                    "campaign": "EnvioMensajes",
                    "channelId": "centrodeconciliacionlaboraldel-whatsapp-5213319252459",
                    "name": "ENCUESTA DE SATISFACCIÓN DEL SERVICIO BRINDADO EN EL CCL 1.0",
                    "intentIdOrName": "encuesta",
                    "contacts": [
                        {
                            "contactId": '521'+str(row['contacto']),
                            "webhookPayload": "",
                            "variables":{
                            "folioSinacol": "folioExpediente",
                            "conciliador": "nombreConciliador"
                            }

                        }
                    ]
                }
            elif encuesta == 2:

                #Formulario audiencias archivadas
                payload = {
                    "campaign": "EnvioMensajes",
                    "channelId": "centrodeconciliacionlaboraldel-whatsapp-5213319252459",
                    "name": "ENCUESTA DE SATISFACCIÓN DEL SERVICIO BRINDADO EN EL CCL 2",
                    "intentIdOrName": "encuesta2",
                    "contacts": [
                        {
                            "contactId": '521'+str(row['contacto']),
                            "webhookPayload": "",
                            "variables":{   
                            "folioSinacol": "folioExpediente",
                            "conciliador": "nombreConciliador"
                            }
                        }
                    ]
                }
            elif encuesta == 3:
                #Formulario audiencia sin asistencia del coitad , sin convenio, archivada
                payload = {
                    "campaign": "EnvioMensajes",
                    "channelId": "centrodeconciliacionlaboraldel-whatsapp-5213319252459",
                    "name": "ENCUESTA DE SATISFACCIÓN DEL SERVICIO BRINDADO EN EL CCL 3",
                    "intentIdOrName": "encuesta3",
                    "contacts": [
                        {
                            "contactId": '521'+str(row['contacto']),
                            "webhookPayload": "",
                            "variables":{
                            "folioSinacol": "folioExpediente",
                            "conciliador": "nombreConciliador"
                            }
                        }
                    ]
                }
            elif encuesta == 4:
                #Formulario audiencias celebrada sin convenio
                payload = {
                    "campaign": "EnvioMensajes",
                    "channelId": "centrodeconciliacionlaboraldel-whatsapp-5213319252459",
                    "name": "ENCUESTA DE SATISFACCIÓN DEL SERVICIO BRINDADO EN EL CCL 4",
                    "intentIdOrName": "encuesta4",
                    "contacts": [
                        {
                            "contactId": '521'+str(row['contacto']),
                            "webhookPayload": "",
                            "variables":{
                            "folioSinacol": "folioExpediente",
                            "conciliador": "nombreConciliador"
                            }
                        }
                    ]
                }
            elif encuesta == 5:
                #Formulario ratificacion con termino de convenio
                payload = {
                    "campaign": "EnvioMensajes",
                    "channelId": "centrodeconciliacionlaboraldel-whatsapp-5213319252459",
                    "name": "ENCUESTA DE SATISFACCIÓN DEL SERVICIO BRINDADO EN EL CCL 5",
                    "intentIdOrName": "encuesta5",
                    "contacts": [
                        {
                            "contactId": '521'+str(row['contacto']),
                            "webhookPayload": "",
                            "variables":{
                            "folioSinacol": "folioExpediente",
                            "conciliador": "nombreConciliador"
                            }
                        }
                    ]
                }

            response = requests.post(base_url, json=payload, headers=headers)
            if response.status_code != 200:
                print(f'Error al enviar el mensaje: {response.text}')
                print(f"Error al enviar mensaje a {row['contacto']}")

        return JsonResponse({"status": "completed"})
    return render(request, 'encuestas/upload_form.html')


#Funciones para apartado api audiencias

def get_audiencias(request):
    URL_API = "https://rarely-assured-kit.ngrok-free.app/audiencias/por-dia"
    parametro = request.GET.get('fecha')

    if parametro:
        URL_API = f"https://rarely-assured-kit.ngrok-free.app/audiencias/por-dia?fecha={parametro}"

    response = requests.get(URL_API)

    if response.status_code == 200:
        audiencias_data = response.json()
        conciliador_id = User.objects.all()

        for audiencia_data in audiencias_data:
            # Extraer los campos de la audiencia
            expediente = audiencia_data.get('Expediente')
            folio_soli = audiencia_data.get('Folio solicitud')
            folio_audiencia = audiencia_data.get('Folio audiencia')
            fecha_audiencia = audiencia_data.get('Fecha audiencia')
            hora_inicio = audiencia_data.get('Hora de inicio')
            hora_fin = audiencia_data.get('Hora Fin')
            conciliador = audiencia_data.get('Conciliador')
            estatus = audiencia_data.get('Estatus')
            nombre_normalizado = normalizar_nombre(conciliador)

            # Campos adicionales de tu modelo
            hora_audiencia = hora_inicio  # Asignamos hora_inicio a hora_audiencia
            sala_audiencia = 'Sin sala asignada'  # Puedes ajustar esto según tus necesidades
            conciliador_audiencia = conciliador
            status_audiencia = 'Pendiente'
            estatus = estatus
            user = None


            for concil in conciliador_id:
                conciliador_normalizado = normalizar_nombre(concil.get_full_name())
                if conciliador_normalizado == nombre_normalizado:
                    print("encontro una coincidencia", concil.get_full_name())
                    user = concil
                    

            

            # Crear o actualizar la audiencia
            audiencia, created = AudienciaAPI.objects.update_or_create(
                expediente=expediente,
                fecha_audiencia=fecha_audiencia,
                defaults={
                    'folio_soli': folio_soli,
                    'folio_audiencia': folio_audiencia,
                    'hora_inicio': hora_inicio,
                    'hora_fin': hora_fin,
                    'hora_audiencia': hora_audiencia,
                    'sala_audiencia': sala_audiencia,
                    'conciliador': conciliador,
                    'conciliador_audiencia': conciliador_audiencia,
                    'estatus': estatus,
                    'status_audiencia': status_audiencia,
                    'user' : user
                    # Añade otros campos necesarios

                }
            )

            # Limpiar solicitantes y citados existentes
            audiencia.solicitantes.all().delete()
            audiencia.citados.all().delete()

            # Procesar solicitantes
            solicitantes_data = audiencia_data.get('Solicitantes', [])
            for solicitante_obj in solicitantes_data:
                nombre = solicitante_obj.get('Solicitante')
                if nombre:
                    SolicitanteAPI.objects.create(audiencia=audiencia, nombre=nombre)

            # Procesar citados
            citados_data = audiencia_data.get('Citados', [])
            for citado_obj in citados_data:
                nombre = citado_obj.get('Citado')
                if nombre:
                    CitadoAPI.objects.create(audiencia=audiencia, nombre=nombre)
    else:
        return JsonResponse({'error': 'No se pudo obtener los datos'}, status=500)

    return JsonResponse({'message': 'Datos guardados exitosamente'})
    


#metodos api templates
@login_required
def audiencias_auxiliares_api(request):
    fecha_actual = timezone.now().date()
    dia_semana = fecha_actual.weekday()

    fechas = []

    if request.user.groups.filter(name='Coordinador').exists():
        # Usuarios del grupo 'Coordinador'
        audiencias = AudienciaAPI.objects.prefetch_related(
            Prefetch('solicitantes', to_attr='ciudadanos_solicitantes'),
            Prefetch('citados', to_attr='ciudadanos_citados')
        ).all()
        fechas = audiencias.values_list('fecha_audiencia', flat=True).distinct().order_by('fecha_audiencia')
    elif request.user.groups.filter(name='Auxiliar').exists():
        # Usuarios del grupo 'Auxiliar'
        fecha_inicio = fecha_actual - timedelta(days=90)
        fechas = obtener_dias_laborables(fecha_inicio, fecha_actual)
        audiencias = AudienciaAPI.objects.filter(
            fecha_audiencia__in=fechas
        ).prefetch_related(
            Prefetch('solicitantes', to_attr='ciudadanos_solicitantes'),
            Prefetch('citados', to_attr='ciudadanos_citados')
        )
    else:
        # Otros usuarios
        if dia_semana == 4:  # Si es viernes
            dias_a_lunes = (7 - dia_semana) % 7
            next_monday = fecha_actual + timedelta(days=dias_a_lunes)
            fechas = [fecha_actual, next_monday]
        else:
            fechas = [fecha_actual]

        audiencias = AudienciaAPI.objects.filter(
            fecha_audiencia__in=fechas
        ).prefetch_related(
            Prefetch('solicitantes', to_attr='ciudadanos_solicitantes'),
            Prefetch('citados', to_attr='ciudadanos_citados')
        )

    # Obtener listas y conteos
    conciliadores = audiencias.values_list(
        'conciliador_audiencia', flat=True
    ).distinct().order_by('conciliador_audiencia')
    estatus = audiencias.values_list('status_audiencia', flat=True).distinct()
    horas = audiencias.values_list('hora_audiencia', flat=True).distinct().order_by('hora_audiencia')

    status_counts = {}
    for status in ['Pendiente', 'Llamando', 'En audiencia', 'Concluida', 'Archivada']:
        status_counts[status] = audiencias.filter(status_audiencia=status).count()

    context = {
        'audiencias': audiencias,
        'conciliadores': conciliadores,
        'estatus': estatus,
        'fechas': fechas,
        'horas': horas,
        'audiencias_pendientes': status_counts.get('Pendiente', 0),
        'audiencias_llamando': status_counts.get('Llamando', 0),
        'audiencias_en_sala': status_counts.get('En audiencia', 0),
        'audiencias_concluidas': status_counts.get('Concluida', 0),
        'audiencias_archivadas': status_counts.get('Archivada', 0),
    }

    return render(request, 'audiencia/audiencias_api.html', context)

@login_required
def asignacion_salas(request):
    tz = pytz.timezone('America/Mexico_City')
    salas = [i for i in range(1, 36) if i not in [5, 6, 7, 8]]
    salas_list = [{'id': i, 'nombre': f'Sala {i}'} for i in salas]
    
    # Obtén la fecha y hora actual en la zona horaria local
    ahora_utc = timezone.now()
    ahora_local = ahora_utc.astimezone(tz)
    ahora_local = ahora_local.replace(second=0, microsecond=0)
    hoy = ahora_local.date()
    audiencias = AudienciaAPI.objects.filter(fecha_audiencia=hoy).order_by('conciliador_audiencia','hora_audiencia').distinct('conciliador_audiencia')
    return render(request, 'audiencia/asignacion_salas.html', {'audiencias': audiencias, 'salas_list': salas_list})

@login_required
def desocupar_sala(request):
    tz = pytz.timezone('America/Mexico_City')
    ahora_utc = timezone.now()
    hoy_local = ahora_utc.astimezone(tz).date()
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            conciliadores = data.get('conciliadores', [])

            try:
                AudienciaAPI.objects.filter(
                    conciliador_audiencia__in=conciliadores,
                    fecha_audiencia=hoy_local
                ).update(sala_audiencia='Sin sala asignada')
                messages.info(request, 'Salas desocupadas exitosamente')
                return JsonResponse({'status': 'success', 'message': 'Salas desocupadas exitosamente'})
            except Exception as e:
                messages.error(request, f'Error al desocupar salas: {e}')
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else: 
            conciliador = request.POST.get('conciliador')
            if conciliador:
                try:
                    AudienciaAPI.objects.filter(
                        conciliador_audiencia=conciliador,
                        fecha_audiencia=hoy_local
                    ).update(sala_audiencia='Sin sala asignada')
                    messages.info(request, 'Sala desocupada exitosamente')
                    return HttpResponseRedirect(reverse('asignacion_salas'))
                except Exception as e:
                    messages.error(request, f'Error al desocupar sala: {e}')
                    return HttpResponseRedirect(reverse('asignacion_salas'))
            else:
                messages.error(request, 'No se proporcionó el nombre del conciliador')
                return HttpResponseRedirect(reverse('asignacion_salas'))
    return HttpResponseRedirect(reverse('asignacion_salas'))

@login_required
def asignar_sala(request):
    tz = pytz.timezone('America/Mexico_City')
    ahora_utc = timezone.now()
    hoy_local = ahora_utc.astimezone(tz).date()
    
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            asignaciones = data.get('asignaciones', [])

            try:
                for asignacion in asignaciones:
                    conciliador = asignacion['conciliador']
                    sala = asignacion['sala']

                    AudienciaAPI.objects.filter(
                        conciliador_audiencia=conciliador,
                        fecha_audiencia=hoy_local
                    ).update(sala_audiencia=sala)
                messages.info(request, 'Salas asignadas exitosamente')
                return JsonResponse({'status': 'success', 'message': 'Salas asignadas exitosamente'})
            except Exception as e:
                messages.error(request, f'Error al asignar salas: {e}')
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            # Para peticiones normales de formulario
            conciliador = request.POST.get('conciliador')
            sala = request.POST.get('salas')
            
            if conciliador and sala:
                try:
                    AudienciaAPI.objects.filter(
                        conciliador_audiencia=conciliador,
                        fecha_audiencia=hoy_local
                    ).update(sala_audiencia=sala)
                    messages.info(request, 'Sala asignada exitosamente')
                    return HttpResponseRedirect(reverse('asignacion_salas'))
                except Exception as e:
                    messages.error(request, f'Error al asignar sala: {e}')
                    return HttpResponseRedirect(reverse('asignacion_salas'))
            else:
                messages.error(request, 'No se proporcionó el nombre del conciliador o la sala')
                return HttpResponseRedirect(reverse('asignacion_salas'))
    return HttpResponseRedirect(reverse('asignacion_salas'))

@login_required
def llamar_audiencia_api(request, audiencias_id):
    if request.method == 'POST':
        audiencia = get_object_or_404(AudienciaAPI, id=audiencias_id)
        audiencia.status_audiencia = 'Llamando'
        audiencia.save()
    return HttpResponseRedirect(reverse('audiencias_auxiliares_api'))

@login_required
def obtener_notificaciones_api(request):
    try:
        notificaciones = NotificacionAPI.objects.filter(se_leyo=False).order_by('-creada_el')
        data = [{
            "id": notificacion.id,
            "expediente": notificacion.audiencia.expediente,
            "conciliador": notificacion.audiencia.conciliador_audiencia,
            "sala": notificacion.audiencia.sala_audiencia,
            "status": notificacion.audiencia.status_audiencia,
            'audiencias_id': notificacion.audiencia.id,
        } for notificacion in notificaciones]
        return JsonResponse({"notificaciones": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def notificacion_leida_api(request, notificacion_id):
    try:
        NotificacionAPI.objects.filter(id=notificacion_id).update(se_leyo=True)
        return JsonResponse({"status": "success"})
    


    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

@login_required
def audiencia_asistencia_api(request, pk):
    # Obtener la audiencia por su id
    audiencia = get_object_or_404(AudienciaAPI, id=pk)
    
    # Obtener todos los solicitantes y citados relacionados con la audiencia
    solicitantes_relacionados = SolicitanteAPI.objects.filter(audiencia=audiencia)
    citados_relacionados = CitadoAPI.objects.filter(audiencia=audiencia)

    if request.method == 'POST':
        # Procesar el formulario: actualizar las asistencias
        if 'asistencias' in request.POST:
            # Actualizar asistencia de solicitantes
            for solicitante in solicitantes_relacionados:
                asistencia_checkbox = f'asistencia_solicitante_{solicitante.id}'
                # Nuevo estado de asistencia basado en el formulario
                nueva_asistencia = asistencia_checkbox in request.POST
                
                # Verificar si la asistencia ha cambiado
                if solicitante.asistencia != nueva_asistencia:
                    solicitante.asistencia = nueva_asistencia
                    if nueva_asistencia and not solicitante.hora_asistencia:
                        solicitante.hora_asistencia = timezone.now()
                    elif not nueva_asistencia:
                        solicitante.hora_asistencia = None
                    solicitante.save()

            # Actualizar asistencia de citados
            for citado in citados_relacionados:
                asistencia_checkbox = f'asistencia_citado_{citado.id}'
                nueva_asistencia = asistencia_checkbox in request.POST

                if citado.asistencia != nueva_asistencia:
                    citado.asistencia = nueva_asistencia
                    if nueva_asistencia and not citado.hora_asistencia:
                        citado.hora_asistencia = timezone.now()
                    elif not nueva_asistencia:
                        citado.hora_asistencia = None
                    citado.save()
                    
            # Agregar un mensaje de éxito después de actualizar las asistencias
            messages.success(request, 'Las asistencias se han actualizado con éxito.')

            # Redirigir a la misma página para mostrar el mensaje
            return HttpResponseRedirect(reverse('audiencia_asistencia_api', args=[pk]))
        
        if 'archivar' in request.POST:
            audiencia.status_audiencia = 'Archivada'
            audiencia.hora_fin_audiencia = timezone.now()
            audiencia.save()
            messages.success(request, 'La audiencia ha sido archivada.')
            return HttpResponseRedirect(reverse('audiencia_asistencia_api', args=[pk]))

    # Renderizar la página con la audiencia y los ciudadanos relacionados
    return render(request, 'audiencia/asistencias_audiencia_api.html', {
        'audiencia': audiencia,
        'solicitantes_relacionados': solicitantes_relacionados,
        'citados_relacionados': citados_relacionados,
    })


@login_required
def celebrar_audiencia_api(request, pk):
    # Obtener la audiencia por su id
    usuario = request.user
    audiencia = get_object_or_404(AudienciaAPI, id=pk)
    #estadisticas = Estadisticas.objects.get(user=request.user)
    
    # Obtener todos los ciudadanos relacionados con la audiencia
    # Obtener todos los solicitantes y citados relacionados con la audiencia
    solicitantes_relacionados = SolicitanteAPI.objects.filter(audiencia=audiencia)
    citados_relacionados = CitadoAPI.objects.filter(audiencia=audiencia)

    if request.method == 'POST':
        # Revisar cuál botón fue presionado
        if 'iniciar' in request.POST:
            print("inicia la audiencia")
            audiencia.status_audiencia = 'En audiencia'
            audiencia.hora_inicio_audiencia = timezone.now()
            messages.success(request, 'La audiencia ha comenzado.')
        elif 'concluir' in request.POST:
            audiencia.status_audiencia = 'Concluida'
            audiencia.hora_fin_audiencia = timezone.now()
            #estadisticas.audiencias_concluidas += 1
            messages.success(request, 'La audiencia ha sido concluida.')
        elif 'archivar' in request.POST:
            audiencia.status_audiencia = 'Archivada'
            audiencia.hora_fin_audiencia = timezone.now()
            #estadisticas.audiencias_archivadas += 1
            messages.success(request, 'La audiencia ha sido archivada.')

        # Guardar los cambios en la audiencia
        audiencia.save()
        #estadisticas.actualizar_promedios()
        #estadisticas.save()

        # Redirigir a la misma página para evitar reenvío del formulario
        return HttpResponseRedirect(reverse('celebrar_audiencia_api', args=[pk]))

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if audiencia.hora_inicio_audiencia:
            tiempo_transcurrido = timezone.now() - audiencia.hora_inicio_audiencia
            horas, remainder = divmod(tiempo_transcurrido.seconds, 3600)
            minutos, segundos = divmod(remainder, 60)
            tiempo_formateado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
            return JsonResponse({'tiempo': tiempo_formateado})
        else:
            return JsonResponse({'tiempo': '00:00:00'})

    # Renderizar la página con la audiencia y los ciudadanos
    return render(request, 'audiencia/audiencias_conciliador_api.html', {
        'audiencia': audiencia,
        'solicitantes_relacionados': solicitantes_relacionados,
        'citados_relacionados': citados_relacionados,
    })

@login_required
def editar_audiencia_api(request, pk):
    # Obtener la audiencia por su id
    audiencia = get_object_or_404(AudienciaAPI, id=pk)

    # # Obtener todos los ciudadanos relacionados con la audiencia
    # ciudadanos_relacionados = ciudadanos.objects.filter(expediente=audiencia)

    if request.method == 'POST':
        # Llenar el formulario con los datos enviados
        form = EditAudienciaForm(request.POST, instance=audiencia)
        if form.is_valid():
            # Guardar los cambios
            form.save()
            messages.success(request, 'Los datos de la audiencia se han actualizado correctamente.')
            return HttpResponseRedirect(reverse('editar_audiencia',args=[pk]))
    else:
        # Mostrar el formulario con los datos actuales
        form = EditAudienciaForm(instance=audiencia)

    return render(request, 'audiencia/audiencias_coordis.html', {'form': form, 'audiencia': audiencia})

@login_required
def asignar_auxiliar(request, pk):
    audiencia = get_object_or_404(AudienciaAPI, id=pk)
    usuario = request.user
    #estadisticas, created = Estadisticas.objects.get_or_create(user=usuario)

    if request.method == 'POST':
        # Asignar el usuario actual como auxiliar_audiencia
        audiencia.auxiliar_audiencia = request.user
        audiencia.auxiliar_asignado_el = timezone.now()
        audiencia.status_audiencia = 'En audiencia'
        audiencia.hora_inicio_audiencia = timezone.now()
        audiencia.save()

        #estadisticas.audiencias += 1
        #estadisticas.actualizar_promedios()
        audiencia.save()

        # Redirigir a la vista de asistencia
        
        return HttpResponseRedirect(reverse('audiencia_asistencia', args=[pk]))
    return HttpResponse("Método no permitido", status=405)

@login_required
def pantalla_audiencia_api(request):
    # Zona horaria de Guadalajara
    tz = pytz.timezone('America/Mexico_City')
    
    # Obtén la fecha y hora actual en la zona horaria local
    ahora_utc = timezone.now()
    ahora_local = ahora_utc.astimezone(tz)
    ahora_local = ahora_local.replace(second=0, microsecond=0)  # Elimina segundos y microsegundos
    hoy = ahora_local.date()
    hora_actual = ahora_local.time()
    time_threshold = timezone.now() - timedelta(seconds=30)

    # Filtro para audiencias llamando (por fecha de hoy)
    audiencias_llamando = AudienciaAPI.objects.filter(
        fecha_audiencia=hoy
    ).filter(
        Q(status_audiencia='Llamando') | 
        Q(status_audiencia='En audiencia', status_changed_at__gte=time_threshold)
    )       

    # Filtro para audiencias pendientes que incluyan la hora actual (12:00 pm en adelante hasta una hora después)
    audiencias_pendientes = AudienciaAPI.objects.filter(
        status_audiencia='Pendiente',
        fecha_audiencia=hoy,
        hora_audiencia__gte=hora_actual.replace(minute=0),  # Incluye toda la hora actual (desde xx:00)
        hora_audiencia__lt=(ahora_local + timedelta(hours=1)).time()  # Menor a una hora más tarde
    )

    # Obtener la última audiencia asignada
    audiencia_mostrada = AudienciaAPI.objects.filter(
        auxiliar_audiencia__isnull=False
    ).order_by('-auxiliar_asignado_el').first()

    context = {
        'audiencias_llamando': audiencias_llamando,
        'audiencias_pendientes': audiencias_pendientes,
        'audiencia_mostrada': audiencia_mostrada,
    }

    return render(request, 'audiencia/pantalla.html', context)