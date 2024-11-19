from django.urls import path
from .views import inicio, registrarme, nosotros
from .views import usuarios,ingresar, usuarios
from .views import misdatos,salir
from .views import poblar
from .views import premio
from .views import mipassword, cambiar_password
from . import views


urlpatterns = [
    path('', inicio, name='inicio'),
    path('inicio', inicio, name='inicio'),
    path('registrarme', registrarme, name='registrarme'),
    path('nosotros', nosotros, name='nosotros'),
    path('usuarios/<accion>/<id>', usuarios, name='usuarios'),
    path('cambiar_password', cambiar_password, name='cambiar_password'),
    path('ingresar', ingresar, name='ingresar'),
    path('misdatos', misdatos, name='misdatos'),
    path('mipassword', mipassword, name='mipassword'),
    path('salir', salir, name='salir'),
    path('premio', premio, name='premio'),
    path('poblar', poblar, name='poblar'),
    path('reservar/', views.reserva_cita, name='reservar_cita'),
    path('reservas/', views.ver_reservas, name='reservas'),
    path('anular-cita/<int:cita_id>/', views.anular_cita, name='anular_cita'),
]