import io
from .models import *
from PIL import Image
from django import forms
from django.utils import timezone
from accounts.models import Profile
from django.forms.widgets import DateInput
from crispy_forms.helper import FormHelper
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django_recaptcha.fields import ReCaptchaField
from django.core.files.uploadedfile import SimpleUploadedFile
from crispy_forms.layout import Layout, Field, Submit, Row, Column
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class formularioLogin(AuthenticationForm):
    pass

class formularioRegistro(UserCreationForm):
    captcha = ReCaptchaField(label='Verificación')
    nombramiento = forms.CharField(label='Nombramiento')  
    email = forms.EmailField(label='Correo electrónico')
    nombre = forms.CharField(label='Nombre (s)')
    apellido = forms.CharField(label='Apellidos')
    class Meta:
        model = User
        fields = ['username', 'nombramiento', 'email', 'nombre', 'apellido', 'password1', 'password2', 'captcha']

    def __init__(self, *args, **kwargs):
        super(formularioRegistro, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6 mb-0'),
                Column('nombramiento', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('email', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('nombre', css_class='form-group col-md-6 mb-0'),
                Column('apellido', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('password1', css_class='form-group col-md-6 mb-0'),
                Column('password2', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row('captcha', css_class='form-group col-md-6 mb-0')
        )
            
    def clean_email(self):
        emailFormulario = self.cleaned_data['email']

        if User.objects.filter(email = emailFormulario):
            raise forms.ValidationError('Este correo ya esta registrado')
        return emailFormulario
    
def validarLongitudCurpRFC(value):
    if len(value) < 13:
        raise ValidationError('Debe escribir su RFC o CURP')

class formularioRegistroManual(forms.ModelForm):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    TIPO_PERSONA_CHOICES = [
        ('Soy Persona Trabajadora', 'Trabajo en una empresa'),
        ('Soy Persona Física Empleadora', 'Soy dueño de la empresa'),
        ('Soy Persona Jurídica Empleadora', 'Soy representante legal de la empresa'),
        ('Soy Persona de Confianza', 'Soy persona de confianza'),
    ]

    sexo = forms.ChoiceField(label='Sexo', choices=SEXO_CHOICES, widget=forms.RadioSelect(attrs={'class': 'form-check-input', 'name': 'sexo'}))
    tipo_persona = forms.ChoiceField(label='', required=True, choices=TIPO_PERSONA_CHOICES, widget=forms.RadioSelect(attrs={'class': 'form-check-input', 'name': 'tipo_persona'}))
    documento_1 = forms.ImageField(label='', required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file','style': 'visibility: hidden; position: absolute; left: -9999px;'}))
    documento_2 = forms.ImageField(label='', required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file','style': 'visibility: hidden; position: absolute; left: -9999px;'}))
    documento_3 = forms.ImageField(label='', required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file','style': 'visibility: hidden; position: absolute; left: -9999px;'}))
    documento_4 = forms.ImageField(label='', required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file','style': 'visibility: hidden; position: absolute; left: -9999px;'}))
    documento_5 = forms.ImageField(label='', required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file','style': 'visibility: hidden; position: absolute; left: -9999px;'}))
    documento_6 = forms.ImageField(label='', required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file','style': 'visibility: hidden; position: absolute; left: -9999px;'}))
    curp_rfc = forms.CharField(label='CURP / RFC', max_length=18, required=False, validators=[validarLongitudCurpRFC], widget=forms.HiddenInput())
    correo = forms.EmailField(label='Correo Electrónico', required=False, widget=forms.HiddenInput())

    class Meta:
        model = ciudadanos
        fields = '__all__'
        widgets = {
            'municipio': forms.TextInput(attrs={'id': 'id_municipio', 'name': 'id_municipio'}),
            'sexo': forms.RadioSelect(attrs={'class': 'form-check-input', 'name': 'sexo'}),
            'tipo_persona': forms.RadioSelect(attrs={'class': 'form-check-input', 'name': 'tipo_persona'}),
        }
        exclude = ['registro', 'qr_code', 'codigo_ciudadano','asistencia','expediente','hora_asistencia']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curp_rfc'].required = False
        self.fields['correo'].required = False 



class CitaForm(forms.ModelForm):
    TIPO_PERSONA_CHOICES = [
        ('Soy Persona Trabajadora', 'Trabajo en una empresa'),
        ('Soy Persona Física Empleadora', 'Soy dueño de la empresa'),
        ('Soy Persona Jurídica Empleadora', 'Soy representante legal de la empresa'),
    ]

    tipo_persona = forms.ChoiceField(label='Tipo de persona', choices=TIPO_PERSONA_CHOICES, widget=forms.RadioSelect(attrs={'class': 'form-check-input'}))
    class Meta:
        model = ciudadanos
        fields = '__all__'
        widgets = {
            'municipio': forms.TextInput(attrs={'id': 'id_municipio'})
        }
        exclude = ['registro', 'qr_code', 'codigo_ciudadano']

# formulario de ciudadano
class ciudadanoForm(forms.ModelForm):
    class Meta:
        model = ciudadanos
        fields = ['nombre', 'sexo', 'correo', 'municipio', 'curp_rfc', 'tipo_persona', 'documento_1', 'documento_2', 'codigo_ciudadano', 'qr_code']

class turnoForm(forms.ModelForm):
    class Meta:
        model = turnos
        fields = ['area', 'mesa', 'status', 'registro']
        widgets = {
            'status': forms.HiddenInput(),
        }        

# clase para remplazar video
class VideoUploadForm(forms.Form):
    video = forms.FileField()

#  prueba formularios area       
class operacionAreaForm(forms.ModelForm):
    class Meta:
        model = operacionArea
        fields = [
            'turno_id', 'idCiudadano', 'observaciones', 'documentacion', 'finalizacion', 'cita_id','area_id', 'folio_sinacol'
        ]
        widgets = {
            'turno_id': forms.TextInput(attrs={'class': 'form-control'}),
            #'idCiudadano': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control'}),
            'documentacion': forms.FileInput(attrs={'class': 'form-control'}),
            'finalizacion': forms.TextInput(attrs={'class': 'form-control'}),
            'cita_id': forms.TextInput(attrs={'class': 'form-control'}),
            'area_id': forms.TextInput(attrs={'class': 'form-control'}),
            'folio_sinacol': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.hora_entrada = timezone.now()  # O establece el valor de acuerdo a tus necesidades
        if commit:
            instance.save()
        return instance

class asesoriaJuridicaForm(operacionAreaForm):
    class Meta(operacionAreaForm.Meta):
        model = asesoriaJuridica
        fields = operacionAreaForm.Meta.fields + ['mesa']
        widgets = operacionAreaForm.Meta.widgets
        widgets.update({'mesa': forms.TextInput(attrs={'class': 'form-control'})})

class pagosForm(operacionAreaForm):
    class Meta(operacionAreaForm.Meta):
        model = pagos
        fields = operacionAreaForm.Meta.fields + ['mesa', 'empleador', 'empleado']
        widgets = operacionAreaForm.Meta.widgets
        widgets.update({
            'mesa': forms.TextInput(attrs={'class': 'form-control'}),
            'empleador': forms.TextInput(attrs={'class': 'form-control'}),
            'empleado': forms.TextInput(attrs={'class': 'form-control'}),
        })

class conciliacionForm(operacionAreaForm):
    class Meta(operacionAreaForm.Meta):
        model = conciliacion
        fields = operacionAreaForm.Meta.fields + ['sala']
        widgets = operacionAreaForm.Meta.widgets
        widgets.update({'sala': forms.TextInput(attrs={'class': 'form-control'})})

class ratificacionForm(operacionAreaForm):
    class Meta(operacionAreaForm.Meta):
        model = ratificacion
        fields = operacionAreaForm.Meta.fields + ['mesa']
        widgets = operacionAreaForm.Meta.widgets
        widgets.update({'mesa': forms.TextInput(attrs={'class': 'form-control'})})

class procuraduriaForm(operacionAreaForm):
    class Meta(operacionAreaForm.Meta):
        model = procuraduria
        fields = operacionAreaForm.Meta.fields + ['mesa']
        widgets = operacionAreaForm.Meta.widgets
        widgets.update({'mesa': forms.TextInput(attrs={'class': 'form-control'})})


class MesaForm(forms.ModelForm):
    class Meta:
        model = mesa
        fields = ['mesa', 'user', 'area']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].required = False
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Guardar'))

    def clean(self):
        cleaned_data = super().clean()
        mesa_name = cleaned_data.get('mesa')
        area = cleaned_data.get('area')

        if mesa.objects.filter(mesa=mesa_name, area=area).exists():
            raise forms.ValidationError('La mesa ya existe en esta área.')
        
        return cleaned_data

class UserPerfilForm(forms.ModelForm):
    image = forms.ImageField(label='Foto de perfil', required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UserPerfilForm, self).__init__(*args, **kwargs)
        
        if user and not user.groups.filter(name='Administrador').exists():
            self.fields['username'].disabled = True
        
        self.fields['groups'] = forms.ModelChoiceField(queryset=Group.objects.all(), required=False, label="Rol actual")
        
        if user and not user.groups.filter(name='Administrador').exists():
            self.fields['groups'].disabled = True

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class SalaForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Conciliador", required=False)
    class Meta:
        model = sala
        fields = ['sala', 'user']
        # Asegúrate de que los widgets estén definidos si los necesitas
        widgets = {
            'sala': forms.TextInput(attrs={'class': 'form-control', 'id': 'room-name'}),
            'user': forms.Select(attrs={'class': 'form-control', 'id': 'conciliator-name'}),
        }

#Form carga de form
class UploadFileForm(forms.Form):
    file = forms.FileField()



class EditAudienciaForm(forms.ModelForm):
    class Meta:
        model = Audiencia
        fields = ['sala_audiencia', 'conciliador_audiencia', 'status_audiencia', 'fecha_audiencia']  # Campos que quieres editar
        labels = {
            'sala_audiencia': 'Sala',
            'conciliador_audiencia': 'Conciliador',
            'status_audiencia': 'Estado',
            'fecha_audiencia': 'Fecha de la Audiencia',
        }
        widgets = {
            'sala_audiencia': forms.TextInput(attrs={'class': 'form-control'}),
            'conciliador_audiencia': forms.TextInput(attrs={'class': 'form-control'}),
            'status_audiencia': forms.Select(attrs={'class': 'form-control'}),  # Correct widget for status
            'fecha_audiencia': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),  # Widget for date input
        }
