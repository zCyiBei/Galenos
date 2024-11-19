from datetime import date
from .zpoblar import poblar_bd
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from django.utils.safestring import SafeString
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Perfil
from .forms import IngresarForm, UsuarioForm, PerfilForm
from .forms import RegistroUsuarioForm, RegistroPerfilForm
from .tools import eliminar_registro, verificar_eliminar_registro, show_form_errors
from django.core.mail import send_mail
from .forms import ReservaCitaForm, ReporteForm, EditarCitaForm
from .models import Cita, Medico, Especialidad
from django.http import HttpResponse
import csv
from io import StringIO

@login_required
def reserva_cita(request):
    especialidades = Especialidad.objects.all()  # Obtener todas las especialidades
    doctores = Medico.objects.all()  # Obtener todos los doctores

    # Filtrar doctores si ya se ha seleccionado una especialidad
    if 'especialidad' in request.POST:
        especialidad_id = request.POST.get('especialidad')
        doctores = Medico.objects.filter(especialidad_id=especialidad_id)  # Filtrar doctores según especialidad seleccionada

    if request.method == 'POST':
        form = ReservaCitaForm(request.POST)
        
        if form.is_valid():
            especialidad = form.cleaned_data['especialidad']
            doctor = form.cleaned_data['doctor']
            
            # Crear una nueva cita con la información del formulario
            cita = Cita(
                usuario=request.user,  # Usar el usuario autenticado
                medico=doctor,  # Usar el médico seleccionado
                especialidad=especialidad,  # Guardar la especialidad como objeto
                fecha=form.cleaned_data['fecha'],
                hora=form.cleaned_data['hora'],
                tipo_documento=form.cleaned_data['tipo_documento'],
                numero_documento=form.cleaned_data['numero_documento'],
                estado='pendiente'  # Asignamos estado pendiente
            )
            cita.save()  # Guardar la cita en la base de datos

            # Enviar correo de confirmación al usuario
            send_mail(
                'Confirmación de tu cita médica',
                f'Hola {cita.usuario.username},\n\nTu cita médica ha sido reservada para el día {cita.fecha} a las {cita.hora}.',
                'zi.yuan@duocuc.cl',  # Remitente
                [cita.usuario.email],  # Destinatario (usuario)
                fail_silently=False,
            )

            # Enviar un correo al médico con los detalles de la cita
            send_mail(
                'Nueva cita médica reservada',
                f'Se ha reservado una nueva cita médica para {cita.usuario.username} (DNI: {cita.numero_documento}) el día {cita.fecha} a las {cita.hora}.',
                'zi.yuan@duocuc.cl',  # Remitente
                [doctor.email],  # Destinatario (doctor)
                fail_silently=False,
            )

            # Mostrar mensaje de éxito en la interfaz
            messages.success(request, '¡Cita reservada con éxito! Se ha enviado un correo de confirmación.')
            
            return redirect('ver_reservas')  # Redirigir a la página de citas reservadas
        else:
            # Si el formulario no es válido, pasamos los doctores filtrados
            return render(request, 'core/reserva_cita.html', {
                'form': form, 
                'especialidades': especialidades, 
                'doctores': doctores
            })
    else:
        form = ReservaCitaForm()

    return render(request, 'core/reserva_cita.html', {
        'form': form,
        'especialidades': especialidades,
        'doctores': doctores
    })

@login_required
def ver_reservas(request):
    # Si el usuario es superusuario  o administrador puede ver todas las citas
    if request.user.is_superuser or request.user.is_staff:
        citas = Cita.objects.all()  # Mostrar todas las citas si es superusuario o admin
    else:
        # Si no es superusuario o admin solo verá sus propias citas
        citas = Cita.objects.filter(usuario=request.user)

    if request.method == 'POST':
        # Si se recibe un POST para editar una cita
        form = EditarCitaForm(request.POST)
        if form.is_valid():
            cita_id = form.cleaned_data['cita_id']  # Añadimos un campo hidden para el ID de la cita
            cita = get_object_or_404(Cita, id=cita_id)
            cita.fecha = form.cleaned_data['fecha']
            cita.hora = form.cleaned_data['hora']
            cita.save()
            return redirect('ver_reservas')  # Redirige a la misma página después de guardar la cita editada
    else:
        form = EditarCitaForm()

    return render(request, 'core/ver_reservas.html', {'citas': citas, 'form': form})

@login_required
def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    
    if request.method == 'POST':
        form = EditarCitaForm(request.POST, instance=cita)
        
        if form.is_valid():
            form.save()  # Guardar los cambios en la cita
            return redirect('reservas')  # Redirigir a la página de citas reservadas

    form = EditarCitaForm(instance=cita)
    return render(request, 'core/editar_cita.html', {'form': form, 'cita': cita})

# Eliminar una cita
@login_required
def anular_cita(request, cita_id):
    # Obtener la cita o devolver un error 404 si no existe
    cita = get_object_or_404(Cita, id=cita_id)

    # Verificar que el usuario es el propietario o un superusuario
    if request.user != cita.usuario and not request.user.is_superuser:
        return JsonResponse({'error': 'No tienes permiso para anular esta cita'}, status=403)

    # Eliminar la cita
    cita.delete()
    return JsonResponse({'message': 'Cita eliminada correctamente'}, status=200)

# Actualizar el estado de una cita
def actualizar_estado_cita(request, cita_id):
    if request.method == 'POST':
        cita = Cita.objects.get(id=cita_id)
        data = json.loads(request.body)  # Obtener el nuevo estado desde la solicitud
        cita.estado = data.get('estado')
        cita.save()
        return JsonResponse({'message': f'Estado actualizado a {cita.estado}'}, status=200)


@login_required
def generar_informe(request):
    if request.method == 'POST':
        form = ReporteForm(request.POST)
        if form.is_valid():
            medico = form.cleaned_data['medico']
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_fin = form.cleaned_data['fecha_fin']
            citas = Cita.objects.filter(fecha__range=[fecha_inicio, fecha_fin])
            if medico:
                citas = citas.filter(medico=medico)

            # Generar CSV
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="reporte_citas.csv"'
            writer = csv.writer(response)
            writer.writerow(['Usuario', 'Medico', 'Fecha', 'Hora', 'Estado'])
            for cita in citas:
                writer.writerow([cita.usuario.username, cita.medico.nombre, cita.fecha, cita.hora, cita.estado])

            return response
    else:
        form = ReporteForm()
    return render(request, 'generar_informe.html', {'form': form})


# Se usará el decorador "@user_passes_test" para realizar la autorización básica a las páginas.
# De este modo sólo entrarán a las páginas las personas que sean del tipo_usuario permitido.
# Si un usuario no autorizado intenta entrar a la página, será redirigido al inicio o a ingreso

# Revisar si el usuario es personal de la empresa (staff administrador o superusuario) autenticado y con cuenta activa
def es_personal_autenticado_y_activo(user):
    return (user.is_staff or user.is_superuser) and user.is_authenticated and user.is_active

# Revisar si el usuario no está autenticado, es decir, si aún está navegando como usuario anónimo
def es_usuario_anonimo(user):
    return user.is_anonymous

# Revisar si el usuario es un cliente (no es personal de la empresa) autenticado y con cuenta activa
def es_cliente_autenticado_y_activo(user):
    return (not user.is_staff and not user.is_superuser) and user.is_authenticated and user.is_active

def inicio(request):
    return render(request, 'core/inicio.html')

def nosotros(request):
    return render(request, 'core/nosotros.html')

def premio(request):
    return render(request, 'core/api.html')

@user_passes_test(es_usuario_anonimo, login_url='inicio')
def ingresar(request):
    if request.method == "POST":
        form = IngresarForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if request.POST.get('recordar_cuenta'):
                        # Si el checkbox está marcado, establecer la cookie para recordar la sesión
                        request.session.set_expiry(1209600)  # 2 semanas en segundos
                    messages.success(request, f'¡Bienvenido(a) {user.first_name} {user.last_name}!')
                    return redirect(inicio)
                else:
                    messages.error(request, 'La cuenta está desactivada.')
            else:
                messages.error(request, 'La cuenta o la contraseña no son correctos.')
        else:
            messages.error(request, 'No se pudo ingresar al sistema.')
            show_form_errors(request, [form])

    else:  # Método GET
        form = IngresarForm()

    context = {
        'form': form,
        'perfiles': Perfil.objects.all().order_by('tipo_usuario', 'subscrito'),
    }

    return render(request, "core/ingresar.html", context)

@login_required
def salir(request):
    nombre = request.user.first_name
    apellido = request.user.last_name
    messages.success(request, f'¡Hasta pronto {nombre} {apellido}!')
    logout(request)
    return redirect(inicio)

@user_passes_test(es_usuario_anonimo, login_url='inicio')
def registrarme(request):
    
    if request.method == 'POST':
        
        form_usuario = RegistroUsuarioForm(request.POST)
        form_perfil = RegistroPerfilForm(request.POST, request.FILES)
        
        if form_usuario.is_valid() and form_perfil.is_valid():
            usuario = form_usuario.save()
            usuario.is_staff = False
            perfil = form_perfil.save(commit=False)
            usuario.save()
            perfil.usuario_id = usuario.id
            perfil.tipo_usuario = 'Cliente'
            perfil.save()
            # premium = ' y aprovechar tus descuentos especiales como cliente PREMIUM' if perfil.su
            mensaje = f'Tu cuenta de usuario: "{usuario.username}" ha sido creada con éxito. ¡Ya puedes ingresar al Centro Médico Galenos'
            messages.success(request, mensaje)
            return redirect(ingresar)
        else:
            messages.error(request, f'No fue posible crear tu cuenta de cliente.')
            show_form_errors(request, [form_usuario, form_perfil])
    
    if request.method == 'GET':
        form_usuario = RegistroUsuarioForm()
        form_perfil = RegistroPerfilForm()

    context = {
        'form_usuario': form_usuario,
        'form_perfil': form_perfil,
    }

    return render(request, 'core/registrarme.html', context)

@login_required
def misdatos(request):

    if request.method == 'POST':
        form_usuario = UsuarioForm(request.POST, instance=request.user)
        form_perfil = RegistroPerfilForm(request.POST, request.FILES, instance=request.user.perfil)
        
        if form_usuario.is_valid() and form_perfil.is_valid():
            usuario = form_usuario.save(commit=False)
            perfil = form_perfil.save(commit=False)
            usuario.save()
            perfil.usuario_id = usuario.id
            perfil.save()
            if perfil.tipo_usuario in ['Administrador', 'Superusuario']:
                tipo_cuenta = perfil.tipo_usuario
            else:
                tipo_cuenta = 'CLIENTE PREMIUM' if perfil.subscrito else 'cliente'
            messages.success(request, f'Tu cuenta de {tipo_cuenta} ha sido actualizada con éxito.')
            return redirect(misdatos)
        else:
            show_form_errors(request, [form_usuario, form_perfil])

    if request.method == 'GET':
        form_usuario = UsuarioForm(instance=request.user)
        form_perfil = RegistroPerfilForm(instance=request.user.perfil)

    context = {
        'form_usuario': form_usuario,
        'form_perfil': form_perfil
    }

    return render(request, 'core/misdatos.html', context)

@user_passes_test(es_personal_autenticado_y_activo)
def usuarios(request, accion, id):

    usuario = User.objects.get(id=id) if int(id) > 0 else None
    perfil = usuario.perfil if usuario else None

    if request.method == 'POST':

        form_usuario = UsuarioForm(request.POST, instance=usuario)

        form_perfil = PerfilForm(request.POST, request.FILES, instance=perfil)

        if form_usuario.is_valid() and form_perfil.is_valid():
            usuario = form_usuario.save(commit=False)
            tipo_usuario = form_perfil.cleaned_data['tipo_usuario']
            usuario.is_staff = tipo_usuario in ['Administrador', 'Superusuario']
            perfil = form_perfil.save(commit=False)
            usuario.save()
            perfil.usuario_id = usuario.id
            perfil.save()
            messages.success(request, f'El usuario {usuario.first_name} {usuario.last_name} fue guardado exitosamente.')
            return redirect(usuarios, 'actualizar', usuario.id)
        else:
            messages.error(request, f'No fue posible guardar el nuevo usuario.')
            show_form_errors(request, [form_usuario, form_perfil])

    if request.method == 'GET':

        if accion == 'eliminar':
            eliminado, mensaje = eliminar_registro(User, id)
            messages.success(request, mensaje)
            return redirect(usuarios, 'crear', '0')
        else:
            form_usuario = UsuarioForm(instance=usuario)
            form_perfil = PerfilForm(instance=perfil)

    context = {
        'form_usuario': form_usuario,
        'form_perfil': form_perfil,
        'usuarios': User.objects.all(),
    }

    return render(request, 'core/usuarios.html', context)

# CAMBIO DE PASSWORD Y ENVIO DE PASSWORD PROVISORIA POR CORREO

@login_required
def mipassword(request):

    if request.method == 'POST':

        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu contraseña ha sido actualizada con éxito, ingresa de nuevo con tu nueva contraseña.')
            return redirect(ingresar)
        else:
            messages.error(request, 'Tu contraseña no pudo ser actualizada.')
            show_form_errors(request, [form])
    
    if request.method == 'GET':

        form = PasswordChangeForm(user=request.user)

    context = {
        'form': form
    }

    return render(request, 'core/mipassword.html', context)

@user_passes_test(es_personal_autenticado_y_activo)
def cambiar_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        existe = User.objects.filter(username=username).exists()
        if existe:
            user = User.objects.get(username=username)
            if user is not None:
                if user.is_active:
                    password = User.objects.make_random_password()
                    user.set_password(password)
                    user.save()
                    enviado = enviar_correo_cambio_password(request, user, password)
                    if enviado:
                        messages.success(request, f'Una nueva contraseña fue enviada al usuario {user.first_name} {user.last_name}')
                    else:
                        messages.error(request, f'No fue posible enviar la contraseña al usuario {user.first_name} {user.last_name}, intente nuevamente más tarde')
                else:
                    messages.error(request, 'La cuenta está desactivada.')
            else:
                messages.error(request, 'La cuenta o la password no son correctos')
        else:
            messages.error(request, 'El usuario al que quiere generar una nueva contraseña ya no existe en el sistema')
    return redirect(usuarios, 'crear', '0')

def enviar_correo_cambio_password(request, user, password):
    try:
        # Revisar "CONFIGURACIÓN PARA ENVIAR CORREOS ELECTRÓNICOS A TRAVÉS DEL SERVIDOR DE GMAIL" en settings.py 
        subject = 'Cambio de contraseña Sword Games Shop'
        url_ingresar = request.build_absolute_uri(reverse(ingresar))
        message = render(request, 'common/formato_correo.html', {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_password': password,
            'link_to_login': url_ingresar,
        })
        from_email = 'info@faithfulpet.com'  # La dirección de correo que aparecerá como remitente
        recipient_list = []
        recipient_list.append(user.email)
        # Enviar el correo
        send_mail(subject=subject, message='', from_email=from_email, recipient_list=recipient_list
            , html_message=message.content.decode('utf-8'))
        return True
    except:
        return False

# POBLAR BASE DE DATOS CON REGISTROS DE PRUEBA

def poblar(request):
    # Permite poblar la base de datos con valores de prueba en todas sus tablas.
    # Opcionalmente se le puede enviar un correo único, para que los Administradores
    # del sistema puedan probar el cambio de password de los usuarios, en la página
    # de "Adminstración de usuarios".
    poblar_bd('zi.yuan@duocuc.cl')
    return redirect(inicio)