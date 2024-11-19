from django.contrib import admin
from .models import Perfil, Cita, Medico, Especialidad

class CitaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'medico', 'fecha', 'hora', 'estado']
    list_filter = ['estado']
    

class MedicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especialidad')
    search_fields = ('nombre', 'especialidad')

admin.site.register(Cita, CitaAdmin)
admin.site.register(Medico, MedicoAdmin)
admin.site.register(Especialidad)