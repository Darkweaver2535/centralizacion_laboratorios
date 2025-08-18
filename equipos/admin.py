from django.contrib import admin
from .models import Equipo, HistorialEquipo, MantenimientoEquipo

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = (
        'codigo_inventario', 'equipo_existente', 'marca', 'modelo', 'estado', 
        'unidad_academica', 'carrera', 'semestre', 'numero_unidades'
    )
    list_filter = (
        'unidad_academica', 'carrera', 'semestre', 'estado', 'es_activo_fijo',
        'asignatura', 'laboratorio', 'created_at'
    )
    search_fields = (
        'codigo_inventario', 'equipo_existente', 'marca', 'modelo', 
        'unidad_academica__nombre', 'carrera__nombre', 'asignatura__nombre'
    )
    readonly_fields = ('codigo_inventario', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Información Académica', {
            'fields': (
                'unidad_academica', 'carrera', 'semestre', 'asignatura',
                'carga_horaria_semanal', 'carga_horaria_semestral'
            )
        }),
        ('Estructura Curricular', {
            'fields': (
                'unidad_tematica', 'guia_laboratorio', 'practica'
            )
        }),
        ('Información del Equipo', {
            'fields': (
                'equipo_existente', 'marca', 'modelo', 'estado', 
                'numero_unidades', 'es_activo_fijo'
            )
        }),
        ('Fotografías', {
            'fields': ('fotografia_frontal', 'fotografia_placa'),
            'classes': ('collapse',)
        }),
        ('Ubicación', {
            'fields': (
                'laboratorio', 'seccion_area', 'identificador_aula'
            )
        }),
        ('Requerimientos', {
            'fields': (
                'equipo_requerido', 'numero_equipos_requeridos'
            )
        }),
        ('Auditoría', {
            'fields': (
                'usuario_creador', 'observaciones', 'codigo_inventario',
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 20

@admin.register(HistorialEquipo)
class HistorialEquipoAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'estado_anterior', 'estado_nuevo', 'usuario', 'fecha_cambio')
    list_filter = ('estado_anterior', 'estado_nuevo', 'fecha_cambio')
    search_fields = ('equipo__equipo_existente', 'equipo__codigo_inventario', 'usuario__username')
    readonly_fields = ('fecha_cambio',)
    list_per_page = 20

@admin.register(MantenimientoEquipo)
class MantenimientoEquipoAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'tipo', 'fecha_inicio', 'fecha_fin', 'usuario_responsable', 'costo')
    list_filter = ('tipo', 'fecha_inicio', 'fecha_fin')
    search_fields = ('equipo__equipo_existente', 'equipo__codigo_inventario', 'descripcion', 'proveedor')
    readonly_fields = ('created_at',)
    list_per_page = 20
