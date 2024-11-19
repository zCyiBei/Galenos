import sqlite3
from django.contrib.auth.models import User, Permission
from django.db import connection
from datetime import date, timedelta
from random import randint
from core.models import Perfil
from core.models import Medico, Cita
from datetime import date, timedelta
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Poblar la base de datos con datos de ejemplo'

    def handle(self, *args, **kwargs):
        # Crear usuarios de ejemplo
        user1 = User.objects.create_user('juan', 'juan@ejemplo.com', 'contraseña123')
        user2 = User.objects.create_user('ana', 'ana@ejemplo.com', 'contraseña123')

        # Crear médicos de ejemplo
        medico1 = Medico.objects.create(nombre='Dr. Pérez', especialidad='Cardiología')
        medico2 = Medico.objects.create(nombre='Dr. Gómez', especialidad='Pediatría')

        # Crear citas de ejemplo
        Cita.objects.create(usuario=user1, medico=medico1, fecha=date.today(), hora='10:00:00', estado='pendiente')
        Cita.objects.create(usuario=user2, medico=medico2, fecha=date.today() + timedelta(days=1), hora='11:00:00', estado='confirmada')

        self.stdout.write(self.style.SUCCESS('Base de datos poblada con datos de ejemplo'))

def eliminar_tabla(nombre_tabla):
    conexion = sqlite3.connect('db.sqlite3')
    cursor = conexion.cursor()
    cursor.execute(f"DELETE FROM {nombre_tabla}")
    conexion.commit()
    conexion.close()

def exec_sql(query):
    with connection.cursor() as cursor:
        cursor.execute(query)

def crear_usuario(username, tipo, nombre, apellido, correo, es_superusuario, 
    es_staff, rut, direccion, subscrito, imagen):

    try:
        print(f'Verificar si existe usuario {username}.')

        if User.objects.filter(username=username).exists():
            print(f'   Eliminar {username}')
            User.objects.get(username=username).delete()
            print(f'   Eliminado {username}')
        
        print(f'Iniciando creación de usuario {username}.')

        usuario = None
        if tipo == 'Superusuario':
            print('    Crear Superuser')
            usuario = User.objects.create_superuser(username=username, password='123')
        else:
            print('    Crear User')
            usuario = User.objects.create_user(username=username, password='123')

        if tipo == 'Administrador':
            print('    Es administrador')
            usuario.is_staff = es_staff
            
        usuario.first_name = nombre
        usuario.last_name = apellido
        usuario.email = correo
        usuario.save()

        if tipo == 'Administrador':
            print(f'    Dar permisos a core y apirest')
            permisos = Permission.objects.filter(content_type__app_label__in=['core', 'apirest'])
            usuario.user_permissions.set(permisos)
            usuario.save()
 
        print(f'    Crear perfil: RUT {rut}, Subscrito {subscrito}, Imagen {imagen}')
        Perfil.objects.create(
            usuario=usuario, 
            tipo_usuario=tipo,
            rut=rut,
            direccion=direccion,
            subscrito=subscrito,
            imagen=imagen)
        print("    Creado correctamente")
    except Exception as err:
        print(f"    Error: {err}")

def eliminar_tablas():
    eliminar_tabla('auth_user_groups')
    eliminar_tabla('auth_user_user_permissions')
    eliminar_tabla('auth_group_permissions')
    eliminar_tabla('auth_group')
    eliminar_tabla('auth_permission')
    eliminar_tabla('django_admin_log')
    eliminar_tabla('django_content_type')
    #eliminar_tabla('django_migrations')
    eliminar_tabla('django_session')
    eliminar_tabla('Perfil')
    #eliminar_tabla('authtoken_token')
    eliminar_tabla('auth_user')

def poblar_bd(test_user_email=''):
    eliminar_tablas()

    crear_usuario(
        username='jperez',
        tipo='Cliente', 
        nombre='Juan', 
        apellido='Perez', 
        correo=test_user_email if test_user_email else 'jperez@jotmail.com', 
        es_superusuario=False, 
        es_staff=False, 
        rut='25.747.200-0',	
        direccion='Tenderini 82 P. 7, Región Metropolitana de Santiago', 
        subscrito=True, 
        imagen='perfiles/jperez.jpg')

    crear_usuario(
        username='jgonzalez',
        tipo='Cliente', 
        nombre='Juana', 
        apellido='Gonzalez', 
        correo=test_user_email if test_user_email else 'jgonzalez@jotmail.com', 
        es_superusuario=False, 
        es_staff=False, 
        rut='12.202.357-5', 
        direccion='Calle Isabel Riquelme, 895', 
        subscrito=True, 
        imagen='perfiles/jgonzalez.jpg')

    crear_usuario(
        username='mpinto',
        tipo='Cliente', 
        nombre='Manuel', 
        apellido='Pinto', 
        correo=test_user_email if test_user_email else 'mpinto@jotmail.com', 
        es_superusuario=False, 
        es_staff=False, 
        rut='11.991.600-3', 
        direccion='Avenida 21 De Mayo, 1465', 
        subscrito=False, 
        imagen='perfiles/mpinto.jpg')

    crear_usuario(
        username='nriffo',
        tipo='Cliente', 
        nombre='Natalia', 
        apellido='Riffo', 
        correo=test_user_email if test_user_email else 'nriffo@jotmail.com', 
        es_superusuario=False, 
        es_staff=False, 
        rut='16.469.725-8', 
        direccion='Avenida Valle Del Maipo 4134 barrio Las Rosas, Maipú', 
        subscrito=False, 
        imagen='perfiles/nriffo.jpg')

    crear_usuario(
        username='mgranifo',
        tipo='Administrador', 
        nombre='Marion', 
        apellido='Granifo', 
        correo=test_user_email if test_user_email else 'mari.granifo@duocuc.cl', 
        es_superusuario=False, 
        es_staff=True, 
        rut='19.441.980-5', 
        direccion='García Sierpes 05.', 
        subscrito=False, 
        imagen='perfiles/mgranifo.jpg')
    
    crear_usuario(
        username='triveros',
        tipo='Administrador', 
        nombre='Tomas', 
        apellido='Riveros', 
        correo=test_user_email if test_user_email else 't.riveros@duocuc.cl', 
        es_superusuario=False, 
        es_staff=True, 
        rut='21.708.052-5', 
        direccion='Avenida Los Dominicos, 8176 - Of. 8', 
        subscrito=False, 
        imagen='perfiles/triveros.jpg')
    
    crear_usuario(
        username='zyuan',
        tipo='Administrador', 
        nombre='Zichao', 
        apellido='Yuan', 
        correo=test_user_email if test_user_email else 'zi.yuan@duocuc.cl', 
        es_superusuario=False, 
        es_staff=True, 
        rut='21.966.370-6', 
        direccion='Calle Tabare 681 , Recoleta', 
        subscrito=False, 
        imagen='perfiles/ziyuan.jpg')

    crear_usuario(
        username='Spacestation',
        tipo='Superusuario',
        nombre='Space',
        apellido='Station',
        correo=test_user_email if test_user_email else 'SpaceStation@spstt.com',
        es_superusuario=True,
        es_staff=True,
        rut='13.029.317-4',
        direccion='12777 Jefferson Blvd, Los Angeles, CA 90066',
        subscrito=False,
        imagen='perfiles/spst.jpg')
    