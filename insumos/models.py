from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from core.models import UnidadAcademica, Carrera, Asignatura, UnidadTematica, GuiaLaboratorio, Practica, Laboratorio

class TipoInsumo(models.Model):
    """Tipos de insumos disponibles"""
    TIPOS = [
        ('reactivos', 'Reactivos Químicos'),
        ('materiales_laboratorio', 'Materiales de Laboratorio'),
        ('herramientas', 'Herramientas'),
        ('consumibles', 'Consumibles'),
        ('material_vidrio', 'Material de Vidrio'),
        ('equipos_proteccion', 'Equipos de Protección'),
        ('material_electronico', 'Material Electrónico'),
        ('software', 'Software'),
        ('licencias', 'Licencias'),
        ('otros', 'Otros'),
    ]
    
    nombre = models.CharField(max_length=50, choices=TIPOS, unique=True)
    descripcion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tipo de Insumo"
        verbose_name_plural = "Tipos de Insumos"
        ordering = ['nombre']
    
    def __str__(self):
        return self.get_nombre_display()

class Insumo(models.Model):
    """
    Modelo para insumos de laboratorio con 19 columnas según especificación oficial
    """
    
    # Categorías de insumos (simplificadas a 3 opciones principales)
    CATEGORIAS = [
        ('reactivos', 'Reactivos'),
        ('materiales', 'Materiales'),
        ('herramientas', 'Herramientas'),
    ]
    
    ESTADOS = [
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('malo', 'Malo'),
        ('vencido', 'Vencido'),
        ('agotado', 'Agotado'),
        ('descartado', 'Descartado'),
    ]
    
    UNIDADES_MEDIDA = [
        ('unidades', 'Unidades'),
        ('ml', 'Mililitros'),
        ('l', 'Litros'),
        ('mg', 'Miligramos'),
        ('g', 'Gramos'),
        ('kg', 'Kilogramos'),
        ('m', 'Metros'),
        ('cm', 'Centímetros'),
        ('mm', 'Milímetros'),
        ('piezas', 'Piezas'),
        ('cajas', 'Cajas'),
        ('paquetes', 'Paquetes'),
        ('frascos', 'Frascos'),
        ('sobres', 'Sobres'),
    ]
    
    USO_PRINCIPAL = [
        ('ensayos', 'Ensayos de Laboratorio'),
        ('practicas', 'Prácticas Académicas'),
        ('investigacion', 'Investigación'),
        ('mantenimiento', 'Mantenimiento'),
        ('limpieza', 'Limpieza'),
        ('seguridad', 'Seguridad'),
        ('calibracion', 'Calibración'),
        ('otros', 'Otros'),
    ]
    
    CONDICIONES_ALMACENAMIENTO = [
        ('temperatura_ambiente', 'Temperatura Ambiente'),
        ('refrigeracion', 'Refrigeración (2-8°C)'),
        ('congelacion', 'Congelación (-18°C)'),
        ('lugar_seco', 'Lugar Seco'),
        ('lugar_oscuro', 'Lugar Oscuro'),
        ('ventilado', 'Lugar Ventilado'),
        ('controlado', 'Ambiente Controlado'),
        ('especial', 'Condiciones Especiales'),
    ]
    
    # 1. UNIDAD ACADÉMICA
    unidad_academica = models.ForeignKey(
        UnidadAcademica, 
        on_delete=models.CASCADE,
        verbose_name="Unidad Académica",
        db_index=True  # Índice para consultas frecuentes
    )
    
    # 2. LABORATORIO
    laboratorio = models.ForeignKey(
        Laboratorio, 
        on_delete=models.CASCADE,
        verbose_name="Laboratorio",
        db_index=True  # Índice para consultas frecuentes
    )
    
    # 3. CATEGORÍA
    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIAS,
        default='reactivos',
        verbose_name="Categoría"
    )
    
    # 4. NOMBRE DEL ELEMENTO
    nombre_elemento = models.CharField(
        max_length=200,
        default='Sin nombre',
        verbose_name="Nombre del Elemento"
    )
    
    # 5. DESCRIPCIÓN/CARACTERÍSTICAS
    descripcion_caracteristicas = models.TextField(
        blank=True,
        verbose_name="Descripción/Características"
    )
    
    # 6. MARCA / MODELO
    marca_modelo = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Marca / Modelo"
    )
    
    # 7. CÓDIGO DE INVENTARIO (INTERNO)
    codigo_inventario = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Código de Inventario (Interno)"
    )
    
    # 8. ESTADO
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='bueno',
        verbose_name="Estado"
    )
    
    # 9. UBICACIÓN FÍSICA
    ubicacion_fisica = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ubicación Física",
        help_text="Estante, cajón, armario, etc."
    )
    
    # 10. CANTIDAD
    cantidad = models.FloatField(
        default=0,
        verbose_name="Cantidad",
        validators=[MinValueValidator(0)]
    )
    
    # 11. UNIDAD DE MEDIDA
    unidad_medida = models.CharField(
        max_length=20,
        choices=UNIDADES_MEDIDA,
        default='unidades',
        verbose_name="Unidad de Medida"
    )
    
    # 12. FECHA DE INGRESO/COMPRA
    fecha_ingreso_compra = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha de Ingreso/Compra"
    )
    
    # 13. USO PRINCIPAL
    uso_principal = models.CharField(
        max_length=30,
        choices=USO_PRINCIPAL,
        blank=True,
        null=True,
        verbose_name="Uso Principal"
    )
    
    # 14. CARRERA
    carrera = models.ForeignKey(
        Carrera, 
        on_delete=models.CASCADE,
        verbose_name="Carrera"
    )
    
    # 15. ASIGNATURA
    asignatura = models.ForeignKey(
        Asignatura, 
        on_delete=models.CASCADE,
        verbose_name="Asignatura"
    )
    
    # 16. UNIDAD TEMÁTICA
    unidad_tematica = models.ForeignKey(
        UnidadTematica, 
        on_delete=models.CASCADE,
        verbose_name="Unidad Temática"
    )
    
    # 17. GUÍA DE LABORATORIO
    guia_laboratorio = models.ForeignKey(
        GuiaLaboratorio, 
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Guía de Laboratorio"
    )
    
    # 18. PRÁCTICA
    practica = models.ForeignKey(
        Practica, 
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Práctica"
    )
    
    # 19. CONDICIONES DE ALMACENAMIENTO
    condiciones_almacenamiento = models.CharField(
        max_length=30,
        choices=CONDICIONES_ALMACENAMIENTO,
        blank=True,
        null=True,
        verbose_name="Condiciones de Almacenamiento"
    )
    
    # 20. OBSERVACIONES
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )
    
    # 21. INGRESE EL LINK DE LA FOTOGRAFÍA DEL ELEMENTO
    link_fotografia = models.URLField(
        blank=True,
        verbose_name="Link de la Fotografía del Elemento",
        help_text="URL de la imagen del elemento"
    )
    
    # Auditoría
    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Usuario Creador"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"
        ordering = ['unidad_academica', 'laboratorio', 'categoria', 'nombre_elemento']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['categoria']),
            models.Index(fields=['created_at']),
            models.Index(fields=['unidad_academica', 'laboratorio']),
        ]
    
    def __str__(self):
        return f"{self.nombre_elemento} - {self.categoria} - {self.laboratorio}"
    
    def save(self, *args, **kwargs):
        # Convertir string vacío a None para evitar problemas de unique constraint
        if self.codigo_inventario == '':
            self.codigo_inventario = None
            
        # Generar código de inventario automáticamente si no existe
        if not self.codigo_inventario and self.unidad_academica and self.laboratorio:
            self.codigo_inventario = self.generar_codigo_inventario()
        elif not self.codigo_inventario:
            # Código simple si no hay unidad académica o laboratorio
            ultimo_numero = Insumo.objects.count()
            self.codigo_inventario = f'INS-{ultimo_numero + 1:06d}'
        super().save(*args, **kwargs)
    
    def generar_codigo_inventario(self):
        """Generar código de inventario único para insumos"""
        # Formato: INS-UA-LAB-NUM (usando IDs para evitar conflictos de nombres)
        ua_id = self.unidad_academica.id
        lab_id = self.laboratorio.id
        
        # Obtener todos los códigos existentes para esta combinación
        existing_codes = Insumo.objects.filter(
            unidad_academica=self.unidad_academica,
            laboratorio=self.laboratorio,
            codigo_inventario__isnull=False
        ).values_list('codigo_inventario', flat=True)
        
        # Extraer números de los códigos existentes
        prefix = f"INS-UA{ua_id}-LAB{lab_id}-"
        existing_nums = []
        for code in existing_codes:
            if code and code.startswith(prefix):
                try:
                    num_part = code.replace(prefix, '')
                    existing_nums.append(int(num_part))
                except ValueError:
                    continue
        
        # Encontrar el siguiente número disponible
        nuevo_num = 1
        while nuevo_num in existing_nums:
            nuevo_num += 1
        
        return f"INS-UA{ua_id}-LAB{lab_id}-{nuevo_num:04d}"
    
    def get_estado_badge_class(self):
        """Devuelve la clase CSS para el badge del estado"""
        badge_classes = {
            'bueno': 'badge-success',
            'regular': 'badge-warning',
            'malo': 'badge-danger',
            'vencido': 'badge-dark',
            'agotado': 'badge-secondary',
            'descartado': 'badge-danger',
        }
        return badge_classes.get(self.estado, 'badge-secondary')


class MovimientoInsumo(models.Model):
    """Historial de movimientos de insumos (entradas, salidas, ajustes)"""
    TIPOS_MOVIMIENTO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste de Inventario'),
        ('descarte', 'Descarte'),
        ('devolucion', 'Devolución'),
    ]
    
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=20, choices=TIPOS_MOVIMIENTO)
    cantidad = models.FloatField()
    cantidad_anterior = models.FloatField()
    cantidad_nueva = models.FloatField()
    motivo = models.CharField(max_length=200)
    observaciones = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Movimiento de Insumo"
        verbose_name_plural = "Movimientos de Insumos"
        ordering = ['-fecha_movimiento']
    
    def __str__(self):
        return f"{self.insumo} - {self.get_tipo_display()} - {self.cantidad} {self.insumo.get_unidad_medida_display()}"

class SolicitudInsumo(models.Model):
    """Solicitudes de insumos por parte de docentes o laboratoristas"""
    ESTADOS_SOLICITUD = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
    ]
    
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='solicitudes')
    cantidad_solicitada = models.FloatField()
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_necesaria = models.DateField()
    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solicitudes_insumos')
    estado = models.CharField(max_length=20, choices=ESTADOS_SOLICITUD, default='pendiente')
    justificacion = models.TextField()
    observaciones = models.TextField(blank=True)
    
    # Campos para aprobación/rechazo
    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='solicitudes_revisadas'
    )
    fecha_revision = models.DateTimeField(null=True, blank=True)
    motivo_rechazo = models.TextField(blank=True)
    
    # Campo para entrega
    entregado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='entregas_insumos'
    )
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    cantidad_entregada = models.FloatField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Solicitud de Insumo"
        verbose_name_plural = "Solicitudes de Insumos"
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"Solicitud de {self.insumo.nombre} - {self.solicitante.username} - {self.get_estado_display()}"


# ================================
# MODELOS PARA REORDENAMIENTO DE INSUMOS
# ================================

class TareaReordenamientoInsumo(models.Model):
    """Modelo para gestionar tareas de reordenamiento de insumos"""
    TIPOS_TAREA = [
        ('reasignacion', 'Reasignación de Insumos'),
        ('reubicacion', 'Reubicación de Insumos'),
        ('cambio_categoria', 'Cambio de Categoría'),
        ('modificacion_datos', 'Modificación de Datos'),
        ('transferencia_unidad', 'Transferencia entre Unidades'),
        ('actualizacion_inventario', 'Actualización de Inventario'),
        ('control_stock', 'Control de Stock'),
        ('verificacion_vencimientos', 'Verificación de Vencimientos'),
    ]
    
    ESTADOS_TAREA = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('pausada', 'Pausada'),
    ]
    
    PRIORIDADES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    # Información básica de la tarea
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título de la Tarea"
    )
    descripcion = models.TextField(
        verbose_name="Descripción",
        help_text="Descripción detallada de la tarea a realizar"
    )
    tipo = models.CharField(
        max_length=30,
        choices=TIPOS_TAREA,
        verbose_name="Tipo de Tarea"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_TAREA,
        default='pendiente',
        verbose_name="Estado"
    )
    prioridad = models.CharField(
        max_length=10,
        choices=PRIORIDADES,
        default='media',
        verbose_name="Prioridad"
    )
    
    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Inicio"
    )
    fecha_fin_estimada = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha Fin Estimada"
    )
    fecha_fin_real = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha Fin Real"
    )
    
    # Usuarios responsables
    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tareas_insumos_creadas',
        verbose_name="Usuario Creador"
    )
    usuario_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tareas_insumos_asignadas',
        null=True,
        blank=True,
        verbose_name="Usuario Asignado"
    )
    
    # Datos adicionales
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )
    porcentaje_completado = models.IntegerField(
        default=0,
        verbose_name="Porcentaje Completado (%)"
    )
    
    class Meta:
        verbose_name = "Tarea de Reordenamiento de Insumo"
        verbose_name_plural = "Tareas de Reordenamiento de Insumos"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.titulo} - {self.get_estado_display()}"
    
    def get_color_prioridad(self):
        """Retorna el color CSS según la prioridad"""
        colores = {
            'baja': '#22c55e',    # Verde
            'media': '#f59e0b',   # Amarillo
            'alta': '#ef4444',    # Rojo
            'urgente': '#dc2626'  # Rojo oscuro
        }
        return colores.get(self.prioridad, '#6b7280')
    
    def get_color_estado(self):
        """Retorna el color CSS según el estado"""
        colores = {
            'pendiente': '#6b7280',   # Gris
            'en_proceso': '#3b82f6', # Azul
            'completada': '#22c55e', # Verde
            'cancelada': '#ef4444',  # Rojo
            'pausada': '#f59e0b'     # Amarillo
        }
        return colores.get(self.estado, '#6b7280')


class InsumoTarea(models.Model):
    """Relación entre insumos y tareas de reordenamiento"""
    tarea = models.ForeignKey(
        TareaReordenamientoInsumo,
        on_delete=models.CASCADE,
        related_name='insumos'
    )
    insumo = models.ForeignKey(
        Insumo,
        on_delete=models.CASCADE,
        related_name='tareas_reordenamiento'
    )
    
    # Datos originales (antes del reordenamiento)
    unidad_academica_original = models.ForeignKey(
        'core.UnidadAcademica',
        on_delete=models.CASCADE,
        related_name='insumos_tareas_origen',
        null=True,
        blank=True,
        verbose_name="Unidad Académica Original"
    )
    carrera_original = models.ForeignKey(
        'core.Carrera',
        on_delete=models.CASCADE,
        related_name='insumos_tareas_origen',
        null=True,
        blank=True,
        verbose_name="Carrera Original"
    )
    laboratorio_original = models.ForeignKey(
        'core.Laboratorio',
        on_delete=models.CASCADE,
        related_name='insumos_tareas_origen',
        null=True,
        blank=True,
        verbose_name="Laboratorio Original"
    )
    categoria_original = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Categoría Original"
    )
    
    # Datos objetivo (después del reordenamiento)
    unidad_academica_objetivo = models.ForeignKey(
        'core.UnidadAcademica',
        on_delete=models.CASCADE,
        related_name='insumos_tareas_destino',
        null=True,
        blank=True,
        verbose_name="Unidad Académica Objetivo"
    )
    carrera_objetivo = models.ForeignKey(
        'core.Carrera',
        on_delete=models.CASCADE,
        related_name='insumos_tareas_destino',
        null=True,
        blank=True,
        verbose_name="Carrera Objetivo"
    )
    laboratorio_objetivo = models.ForeignKey(
        'core.Laboratorio',
        on_delete=models.CASCADE,
        related_name='insumos_tareas_destino',
        null=True,
        blank=True,
        verbose_name="Laboratorio Objetivo"
    )
    categoria_objetivo = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Categoría Objetivo"
    )
    
    # Estado de procesamiento
    procesado = models.BooleanField(
        default=False,
        verbose_name="Procesado"
    )
    fecha_procesamiento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Procesamiento"
    )
    observaciones_procesamiento = models.TextField(
        blank=True,
        verbose_name="Observaciones del Procesamiento"
    )
    
    class Meta:
        verbose_name = "Insumo en Tarea"
        verbose_name_plural = "Insumos en Tareas"
        unique_together = ['tarea', 'insumo']
    
    def __str__(self):
        return f"{self.insumo.nombre_elemento} - {self.tarea.titulo}"


class LogReordenamientoInsumo(models.Model):
    """Log de acciones realizadas en las tareas de reordenamiento de insumos"""
    tarea = models.ForeignKey(
        TareaReordenamientoInsumo,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuario"
    )
    accion = models.CharField(
        max_length=200,
        verbose_name="Acción Realizada"
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción Detallada"
    )
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Log de Reordenamiento de Insumo"
        verbose_name_plural = "Logs de Reordenamiento de Insumos"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.tarea.titulo} - {self.accion} - {self.usuario.username}"
