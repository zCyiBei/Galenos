
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from core.templatetags.custom_filters import formatear_dinero
from django.db import models
from django.db.models import Min
from django.db import connection

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Medico(models.Model):
    nombre = models.CharField(max_length=100)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} - {self.especialidad.nombre}"


class Cita(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('DNI', 'DNI'),
        ('PASAPORTE', 'Pasaporte'),
        ('CEDULA', 'Cédula de Identidad'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    medico = models.CharField(max_length=100)
    fecha = models.DateField()
    hora = models.TimeField()
    tipo_documento = models.CharField(
        max_length=20,
        choices=TIPO_DOCUMENTO_CHOICES,
        verbose_name='Tipo de documento de identidad',
        default='DNI',
    )
    numero_documento = models.CharField(
        max_length=20, 
        verbose_name='Número de documento', 
        default='123456789'  # Valor predeterminado para numero_documento
    )
    estado = models.CharField(
        max_length=20, 
        choices=[('pendiente', 'Pendiente'), ('confirmada', 'Confirmada')]
    )

    def __str__(self):
        return f"Cita de {self.usuario} con {self.medico} en {self.fecha}"


    
class Perfil(models.Model):
    USUARIO_CHOICES = [
        ('Cliente', 'Cliente'),
        ('Medico', 'Medico'),
        ('Administrador', 'Administrador'),
        ('Superusuario', 'Superusuario'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(
        choices=USUARIO_CHOICES,
        max_length=50,
        blank=False,
        null=False,
        verbose_name='Tipo de usuario'
    )
    rut = models.CharField(max_length=15, blank=False, null=False, verbose_name='RUT')
    direccion = models.CharField(max_length=800, blank=False, null=False, verbose_name='Dirección')
    subscrito = models.BooleanField(default=False)
    imagen = models.ImageField(upload_to='perfiles/', blank=False, null=False, verbose_name='Imagen')
    
    class Meta:
        db_table = 'Perfil'
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuarios"
        ordering = ['tipo_usuario']

    def __str__(self):
        subscrito = ''
        if self.tipo_usuario == 'Cliente':
            subscrito = ' subscrito' if self.subscrito else ' no subscrito'
        return f'{self.usuario.first_name} {self.usuario.last_name} (ID {self.id} - {self.tipo_usuario}{subscrito})'
    
    def acciones():
        return {
            'accion_eliminar': 'eliminar el Perfil',
            'accion_actualizar': 'actualizar el Perfil'
        }