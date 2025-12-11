from django.contrib import admin
from .models import Equipo, HistorialEquipo, MantenimientoEquipo, TareaReordenamiento, EquipoTarea, LogReordenamiento

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
                'guia_laboratorio', 'practica'
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


class EquipoTareaInline(admin.TabularInline):
    model = EquipoTarea
    extra = 0
    readonly_fields = ('procesado', 'fecha_procesado')


class LogReordenamientoInline(admin.TabularInline):
    model = LogReordenamiento
    extra = 0
    readonly_fields = ('fecha',)


@admin.register(TareaReordenamiento)
class TareaReordenamientoAdmin(admin.ModelAdmin):
    list_display = (
        'titulo', 'tipo', 'estado', 'prioridad', 'usuario_creador', 
        'usuario_asignado', 'porcentaje_completado', 'fecha_creacion'
    )
    list_filter = (
        'tipo', 'estado', 'prioridad', 'usuario_creador', 'usuario_asignado', 
        'fecha_creacion', 'fecha_fin_estimada'
    )
    search_fields = ('titulo', 'descripcion', 'observaciones')
    readonly_fields = ('fecha_creacion',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'titulo', 'descripcion', 'tipo', 'estado', 'prioridad'
            )
        }),
        ('Responsables', {
            'fields': ('usuario_creador', 'usuario_asignado')
        }),
        ('Fechas', {
            'fields': (
                'fecha_creacion', 'fecha_inicio', 'fecha_fin_estimada', 'fecha_fin_real'
            )
        }),
        ('Progreso', {
            'fields': ('porcentaje_completado', 'observaciones')
        }),
    )
    
    inlines = [EquipoTareaInline, LogReordenamientoInline]
    list_per_page = 20


@admin.register(EquipoTarea)
class EquipoTareaAdmin(admin.ModelAdmin):
    list_display = (
        'tarea', 'equipo', 'unidad_academica_origen', 'laboratorio_origen',
        'unidad_academica_destino', 'laboratorio_destino', 'procesado'
    )
    list_filter = (
        'procesado', 'tarea__tipo', 'unidad_academica_origen', 
        'unidad_academica_destino', 'fecha_procesado'
    )
    search_fields = (
        'tarea__titulo', 'equipo__equipo_existente', 'equipo__codigo_inventario'
    )
    readonly_fields = ('fecha_procesado',)
    
    fieldsets = (
        ('Asignación', {
            'fields': ('tarea', 'equipo')
        }),
        ('Origen', {
            'fields': ('unidad_academica_origen', 'laboratorio_origen')
        }),
        ('Destino', {
            'fields': ('unidad_academica_destino', 'laboratorio_destino')
        }),
        ('Estado', {
            'fields': ('procesado', 'fecha_procesado', 'observaciones_equipo')
        }),
    )
    
    list_per_page = 20


@admin.register(LogReordenamiento)
class LogReordenamientoAdmin(admin.ModelAdmin):
    list_display = ('tarea', 'usuario', 'accion', 'fecha')
    list_filter = ('accion', 'fecha', 'usuario')
    search_fields = ('tarea__titulo', 'usuario__username', 'accion', 'descripcion')
    readonly_fields = ('fecha',)
    list_per_page = 20
