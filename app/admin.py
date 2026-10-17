from django.contrib import admin
from .models import Persona


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombres_completos', 'fecha_nacimiento', 'creado_en')
    search_fields = ('nombres_completos',)
    list_filter = ('fecha_nacimiento', 'creado_en')
    ordering = ('-id',)
