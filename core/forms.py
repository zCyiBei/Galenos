from django import forms
from django.forms import ModelForm, Form
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Perfil, Cita, Especialidad, Medico

# *********************************************************************************************************#
#                                                                                                          #
# INSTRUCCIONES PARA EL ALUMNO, PUEDES SEGUIR EL VIDEO TUTORIAL, COMPLETAR EL CODIGO E INCORPORAR EL TUYO: #
#                                                                                                          #
# https://drive.google.com/drive/folders/1ObwMnpKmCXVbq3SMwJKlSRE0PCn0buk8?usp=drive_link                  #
#                                                                                                          #
# *********************************************************************************************************#

class ReservaCitaForm(forms.ModelForm):
    tipo_documento = forms.ChoiceField(choices=[('DNI', 'DNI'), ('Pasaporte', 'Pasaporte')], required=True)
    numero_documento = forms.CharField(max_length=20, required=True)
    especialidad = forms.ModelChoiceField(queryset=Especialidad.objects.all(), required=True)
    doctor = forms.ModelChoiceField(queryset=Medico.objects.all(), required=True)

    class Meta:
        model = Cita
        fields = ['usuario', 'medico', 'especialidad', 'doctor', 'fecha', 'hora', 'tipo_documento', 'numero_documento']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'usuario': forms.Select(attrs={'class': 'form-control'}),
            'especialidad': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-control'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ReservaCitaForm, self).__init__(*args, **kwargs)
        
        # Inicializamos el campo 'doctor' con doctores de la especialidad seleccionada
        if 'especialidad' in self.data:
            especialidad_id = self.data.get('especialidad')
            self.fields['doctor'].queryset = Medico.objects.filter(especialidad_id=especialidad_id)
        elif self.instance.pk:
            self.fields['doctor'].queryset = self.instance.especialidad.medico_set.all()

    # Método para actualizar los médicos según la especialidad seleccionada
    def clean(self):
        cleaned_data = super().clean()
        especialidad = cleaned_data.get("especialidad")
        doctor = cleaned_data.get("doctor")

        if especialidad and doctor:
            # Verifica que el doctor pertenezca a la especialidad seleccionada
            if doctor.especialidad != especialidad:
                self.add_error('doctor', 'El doctor seleccionado no pertenece a la especialidad elegida.')

        return cleaned_data

class ReporteForm(forms.Form):
    medico = forms.ModelChoiceField(queryset=User.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False)
    fecha_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False)

# El formulario de ingreso está listo, no necesitas modificarlo
class IngresarForm(Form):
    username = forms.CharField(widget=forms.TextInput(), label="Cuenta")
    password = forms.CharField(widget=forms.PasswordInput(), label="Contraseña")
    class Meta:
        fields = ['username', 'password']

# LA PAGINA DE REGISTRO DE NUEVO CLIENTE:
class RegistroUsuarioForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'email': 'E-mail',
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(RegistroUsuarioForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        contraseña = cleaned_data.get("password1")
        contraseña2 = cleaned_data.get("password2")

        if contraseña and contraseña2 and contraseña != contraseña2:
            self.add_error('password2', "Las contraseñas no coinciden")

        return cleaned_data


# LA PAGINA DE REGISTRO DE NUEVO CLIENTE Y MIS DATOS:
class RegistroPerfilForm(ModelForm):

    class Meta:
        model = Perfil
        fields = ('rut','direccion','imagen', 'subscrito')
        exclude = ('tipo_usuario',)
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
            'imagen': forms.FileInput(attrs={'style': 'displaynone;'}),
        }
        labels = {
            'rut': 'RUT',
            'direccion': 'Direccion',
            'imagen': 'Foto',
            'subscrito': 'Suscribirse'
        }
# LA PAGINA MIS DATOS Y MANTENEDOR DE USUARIOS:
class UsuarioForm(ModelForm):
   class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = {
            'email': 'E-mail',
        }


# LA PAGINA MANTENEDOR DE USUARIOS:
class PerfilForm(ModelForm):
    class Meta:
        model = Perfil
        fields = ('tipo_usuario', 'rut', 'direccion', 'subscrito', 'imagen')
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 2}),
            'imagen': forms.FileInput(attrs={'style': 'displaynone;'}),
        }