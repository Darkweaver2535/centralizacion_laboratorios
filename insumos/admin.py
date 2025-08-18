from django.contrib import admin
from .models import TipoInsumo, Insumo, MovimientoInsumo, SolicitudInsumo

@admin.register(TipoInsumo)
class TipoInsumoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'get_nombre_display', 'created_at')
    list_filter = ('nombre', 'created_at')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = (
        'codigo_inventario', 'nombre', 'tipo_insumo', 'cantidad_actual', 
        'unidad_medida', 'estado', 'unidad_academica', 'carrera'
    )
    list_filter = (
        'unidad_academica', 'carrera', 'semestre', 'tipo_insumo', 'estado',
        'es_peligroso', 'created_at'
    )
    search_fields = (
        'codigo_inventario', 'nombre', 'descripcion', 'marca', 'modelo',
        'unidad_academica__nombre', 'carrera__nombre'
    )
    readonly_fields = ('codigo_inventario', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Información Académica', {
            'fields': (
                'unidad_academica', 'carrera', 'semestre', 'asignatura',
                'unidad_tematica', 'guia_laboratorio', 'practica'
            )
        }),
        ('Información del Insumo', {
            'fields': (
                'tipo_insumo', 'nombre', 'descripcion', 'marca', 'modelo'
            )
        }),
        ('Inventario', {
            'fields': (
                'cantidad_actual', 'cantidad_minima', 'cantidad_requerida', 
                'unidad_medida', 'estado'
            )
        }),
        ('Ubicación', {
            'fields': ('laboratorio', 'ubicacion_especifica')
        }),
        ('Información Adicional', {
            'fields': (
                'fecha_vencimiento', 'numero_lote', 'proveedor', 'precio_unitario'
            ),
            'classes': ('collapse',)
        }),
        ('Seguridad', {
            'fields': ('es_peligroso', 'notas_seguridad'),
            'classes': ('collapse',)
        }),
        ('Fotografía', {
            'fields': ('fotografia',),
            'classes': ('collapse',)
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
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Mostrar alertas de stock bajo
        return queryset.extra(
            select={
                'alerta_stock': 'cantidad_actual <= cantidad_minima'
            }
        )

@admin.register(MovimientoInsumo)
class MovimientoInsumoAdmin(admin.ModelAdmin):
    list_display = (
        'insumo', 'tipo', 'cantidad', 'cantidad_anterior', 
        'cantidad_nueva', 'usuario', 'fecha_movimiento'
    )
    list_filter = ('tipo', 'fecha_movimiento')
    search_fields = ('insumo__nombre', 'insumo__codigo_inventario', 'motivo', 'usuario__username')
    readonly_fields = ('fecha_movimiento',)
    list_per_page = 20

@admin.register(SolicitudInsumo)
class SolicitudInsumoAdmin(admin.ModelAdmin):
    list_display = (
        'insumo', 'cantidad_solicitada', 'solicitante', 'estado', 
        'fecha_solicitud', 'fecha_necesaria'
    )
    list_filter = ('estado', 'fecha_solicitud', 'fecha_necesaria')
    search_fields = (
        'insumo__nombre', 'insumo__codigo_inventario', 
        'solicitante__username', 'justificacion'
    )
    readonly_fields = ('fecha_solicitud', 'fecha_revision', 'fecha_entrega')
    
    fieldsets = (
        ('Información de la Solicitud', {
            'fields': (
                'insumo', 'cantidad_solicitada', 'fecha_necesaria',
                'solicitante', 'justificacion'
            )
        }),
        ('Estado de la Solicitud', {
            'fields': ('estado', 'observaciones')
        }),
        ('Revisión', {
            'fields': (
                'revisado_por', 'fecha_revision', 'motivo_rechazo'
            ),
            'classes': ('collapse',)
        }),
        ('Entrega', {
            'fields': (
                'entregado_por', 'fecha_entrega', 'cantidad_entregada'
            ),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 20
