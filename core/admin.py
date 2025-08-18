from django.contrib import admin
from .models import UnidadAcademica, Carrera, Asignatura, UnidadTematica, GuiaLaboratorio, Practica, Laboratorio

@admin.register(UnidadAcademica)
class UnidadAcademicaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'get_nombre_display', 'created_at')
    list_filter = ('nombre', 'created_at')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'get_nombre_display', 'unidad_academica', 'created_at')
    list_filter = ('unidad_academica', 'nombre', 'created_at')
    search_fields = ('nombre', 'descripcion', 'unidad_academica__nombre')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'get_nombre_display', 'carrera', 'semestre', 'carga_horaria_semanal', 'carga_horaria_semestral')
    list_filter = ('carrera', 'semestre', 'created_at')
    search_fields = ('nombre', 'carrera__nombre')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20

@admin.register(UnidadTematica)
class UnidadTematicaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nombre', 'asignatura', 'created_at')
    list_filter = ('asignatura__carrera', 'asignatura__semestre', 'created_at')
    search_fields = ('nombre', 'asignatura__nombre', 'descripcion')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20

@admin.register(GuiaLaboratorio)
class GuiaLaboratorioAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nombre', 'unidad_tematica', 'created_at')
    list_filter = ('unidad_tematica__asignatura__carrera', 'unidad_tematica__asignatura__semestre', 'created_at')
    search_fields = ('nombre', 'unidad_tematica__nombre', 'descripcion')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20

@admin.register(Practica)
class PracticaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'nombre', 'guia_laboratorio', 'created_at')
    list_filter = ('guia_laboratorio__unidad_tematica__asignatura__carrera', 'created_at')
    search_fields = ('nombre', 'guia_laboratorio__nombre', 'descripcion')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20

@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'get_nombre_display', 'responsable', 'capacidad', 'seccion_area', 'identificador_aula')
    list_filter = ('nombre', 'created_at')
    search_fields = ('nombre', 'responsable', 'seccion_area', 'identificador_aula', 'descripcion')
    readonly_fields = ('created_at', 'updated_at')
