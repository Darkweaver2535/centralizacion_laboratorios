from django.db import models
from django.conf import settings
from core.models import UnidadAcademica, Carrera, Asignatura, UnidadTematica, GuiaLaboratorio, Practica, Laboratorio

class Equipo(models.Model):
    """
    Modelo principal para equipos con las 22 columnas especificadas:
    1. UNIDAD ACADÉMICA
    2. CARRERA
    3. SEMESTRE
    4. ASIGNATURA
    5. CARGA HORARIA SEMANAL
    6. CARGA HORARIA SEMESTRAL
    7. UNIDAD TEMÁTICA
    8. GUÍA DE LABORATORIO
    9. PRÁCTICA
    10. EQUIPO EXISTENTE
    11. MARCA
    12. MODELO
    13. ESTADO
    14. NÚMERO DE UNIDADES DEL EQUIPO
    15. ES UN ACTIVO FIJO DE ACUERDO A SU ACTA DE ENTREGA?
    16. FOTOGRAFÍA FRONTAL DEL EQUIPO
    17. FOTOGRAFÍA DE LA PLACA DE CARACTERÍSTICAS
    18. UBICACIÓN DEL EQUIPO (LABORATORIO)
    19. SECCIÓN/ÁREA
    20. IDENTIFICADOR/Nº DE AULA
    21. EQUIPO REQUERIDO
    22. NÚMERO DE EQUIPOS REQUERIDOS
    """
    
    ESTADOS = [
        ('operativo', 'Operativo'),
        ('mantenimiento', 'En Mantenimiento'),
        ('reparacion', 'En Reparación'),
        ('inoperativo', 'Inoperativo'),
        ('nuevo', 'Nuevo'),
        ('usado', 'Usado'),
        ('descartado', 'Descartado'),
    ]
    
    # 1. UNIDAD ACADÉMICA
    unidad_academica = models.ForeignKey(
        UnidadAcademica, 
        on_delete=models.CASCADE,
        verbose_name="Unidad Académica"
    )
    
    # 2. CARRERA
    carrera = models.ForeignKey(
        Carrera, 
        on_delete=models.CASCADE,
        verbose_name="Carrera"
    )
    
    # 3. SEMESTRE
    semestre = models.IntegerField(
        choices=[(i, f"{i}° Semestre") for i in range(1, 11)],
        verbose_name="Semestre"
    )
    
    # 4. ASIGNATURA
    asignatura = models.ForeignKey(
        Asignatura, 
        on_delete=models.CASCADE,
        verbose_name="Asignatura"
    )
    
    # 5. CARGA HORARIA SEMANAL
    carga_horaria_semanal = models.IntegerField(
        verbose_name="Carga Horaria Semanal",
        help_text="Horas por semana"
    )
    
    # 6. CARGA HORARIA SEMESTRAL
    carga_horaria_semestral = models.IntegerField(
        verbose_name="Carga Horaria Semestral",
        help_text="Total de horas en el semestre"
    )
    
    # 7. UNIDAD TEMÁTICA
    unidad_tematica = models.ForeignKey(
        UnidadTematica, 
        on_delete=models.CASCADE,
        verbose_name="Unidad Temática"
    )
    
    # 8. GUÍA DE LABORATORIO
    guia_laboratorio = models.ForeignKey(
        GuiaLaboratorio, 
        on_delete=models.CASCADE,
        verbose_name="Guía de Laboratorio"
    )
    
    # 9. PRÁCTICA
    practica = models.ForeignKey(
        Practica, 
        on_delete=models.CASCADE,
        verbose_name="Práctica"
    )
    
    # 10. EQUIPO EXISTENTE
    equipo_existente = models.CharField(
        max_length=200,
        verbose_name="Equipo Existente",
        help_text="Nombre del equipo existente"
    )
    
    # 11. MARCA
    marca = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Marca"
    )
    
    # 12. MODELO
    modelo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Modelo"
    )
    
    # 13. ESTADO
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='operativo',
        verbose_name="Estado"
    )
    
    # 14. NÚMERO DE UNIDADES DEL EQUIPO
    numero_unidades = models.IntegerField(
        default=1,
        verbose_name="Número de Unidades del Equipo"
    )
    
    # 15. ES UN ACTIVO FIJO DE ACUERDO A SU ACTA DE ENTREGA?
    es_activo_fijo = models.BooleanField(
        default=False,
        verbose_name="Es un Activo Fijo de acuerdo a su Acta de Entrega?"
    )
    
    # 16. FOTOGRAFÍA FRONTAL DEL EQUIPO
    fotografia_frontal = models.ImageField(
        upload_to='equipos/fotos_frontales/',
        blank=True,
        null=True,
        verbose_name="Fotografía Frontal del Equipo"
    )
    
    # 17. FOTOGRAFÍA DE LA PLACA DE CARACTERÍSTICAS
    fotografia_placa = models.ImageField(
        upload_to='equipos/fotos_placas/',
        blank=True,
        null=True,
        verbose_name="Fotografía de la Placa de Características"
    )
    
    # 18. UBICACIÓN DEL EQUIPO (LABORATORIO)
    laboratorio = models.ForeignKey(
        Laboratorio, 
        on_delete=models.CASCADE,
        verbose_name="Ubicación del Equipo (Laboratorio)"
    )
    
    # 19. SECCIÓN/ÁREA
    seccion_area = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Sección/Área"
    )
    
    # 20. IDENTIFICADOR/Nº DE AULA
    identificador_aula = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Identificador/Nº de Aula"
    )
    
    # 21. EQUIPO REQUERIDO
    equipo_requerido = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Equipo Requerido",
        help_text="Equipo que se requiere para completar el laboratorio"
    )
    
    # 22. NÚMERO DE EQUIPOS REQUERIDOS
    numero_equipos_requeridos = models.IntegerField(
        default=0,
        verbose_name="Número de Equipos Requeridos"
    )
    
    # Campos adicionales para auditoría
    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name="Usuario Creador"
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )
    codigo_inventario = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        verbose_name="Código de Inventario"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ['unidad_academica', 'carrera', 'semestre', 'asignatura']
    
    def __str__(self):
        return f"{self.equipo_existente} - {self.unidad_academica} - {self.carrera}"
    
    def save(self, *args, **kwargs):
        # Generar código de inventario automáticamente si no existe
        if not self.codigo_inventario:
            self.codigo_inventario = self.generar_codigo_inventario()
        super().save(*args, **kwargs)
    
    def generar_codigo_inventario(self):
        """Generar código de inventario único"""
        # Formato: UA-CAR-SEM-ASIG-NUM
        ua_code = self.unidad_academica.nombre[:3].upper()
        car_code = self.carrera.nombre[:3].upper()
        sem_code = f"S{self.semestre:02d}"
        
        # Obtener el siguiente número secuencial
        ultimo_equipo = Equipo.objects.filter(
            unidad_academica=self.unidad_academica,
            carrera=self.carrera,
            semestre=self.semestre
        ).order_by('-id').first()
        
        num = 1 if not ultimo_equipo else ultimo_equipo.id + 1
        
        return f"{ua_code}-{car_code}-{sem_code}-{num:04d}"

class HistorialEquipo(models.Model):
    """Historial de cambios de estado de equipos"""
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=20, choices=Equipo.ESTADOS)
    estado_nuevo = models.CharField(max_length=20, choices=Equipo.ESTADOS)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Historial de Equipo"
        verbose_name_plural = "Historiales de Equipos"
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"{self.equipo} - {self.estado_anterior} → {self.estado_nuevo}"

class MantenimientoEquipo(models.Model):
    """Registro de mantenimientos de equipos"""
    TIPOS_MANTENIMIENTO = [
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
        ('calibracion', 'Calibración'),
        ('reparacion', 'Reparación'),
    ]
    
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='mantenimientos')
    tipo = models.CharField(max_length=20, choices=TIPOS_MANTENIMIENTO)
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    proveedor = models.CharField(max_length=200, blank=True)
    usuario_responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Mantenimiento de Equipo"
        verbose_name_plural = "Mantenimientos de Equipos"
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.equipo} - {self.get_tipo_display()} - {self.fecha_inicio.strftime('%d/%m/%Y')}"


class TareaReordenamiento(models.Model):
    """Modelo para gestionar tareas de reordenamiento de equipos"""
    TIPOS_TAREA = [
        ('reasignacion', 'Reasignación de Equipos'),
        ('reubicacion', 'Reubicación de Equipos'),
        ('cambio_caracteristicas', 'Cambio de Características'),
        ('modificacion_datos', 'Modificación de Datos'),
        ('transferencia_unidad', 'Transferencia entre Unidades'),
        ('actualizacion_inventario', 'Actualización de Inventario'),
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
        related_name='tareas_creadas',
        verbose_name="Usuario Creador"
    )
    usuario_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tareas_asignadas',
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
        verbose_name = "Tarea de Reordenamiento"
        verbose_name_plural = "Tareas de Reordenamiento"
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


class EquipoTarea(models.Model):
    """Relación entre equipos y tareas de reordenamiento"""
    tarea = models.ForeignKey(
        TareaReordenamiento,
        on_delete=models.CASCADE,
        related_name='equipos_involucrados'
    )
    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        related_name='tareas_reordenamiento'
    )
    
    # Datos originales (antes del cambio)
    unidad_academica_origen = models.ForeignKey(
        UnidadAcademica,
        on_delete=models.CASCADE,
        related_name='equipos_origen',
        null=True,
        blank=True,
        verbose_name="Unidad Académica Origen"
    )
    laboratorio_origen = models.ForeignKey(
        Laboratorio,
        on_delete=models.CASCADE,
        related_name='equipos_origen',
        null=True,
        blank=True,
        verbose_name="Laboratorio Origen"
    )
    
    # Datos destino (después del cambio)
    unidad_academica_destino = models.ForeignKey(
        UnidadAcademica,
        on_delete=models.CASCADE,
        related_name='equipos_destino',
        null=True,
        blank=True,
        verbose_name="Unidad Académica Destino"
    )
    laboratorio_destino = models.ForeignKey(
        Laboratorio,
        on_delete=models.CASCADE,
        related_name='equipos_destino',
        null=True,
        blank=True,
        verbose_name="Laboratorio Destino"
    )
    
    # Estado del procesamiento de este equipo específico
    procesado = models.BooleanField(
        default=False,
        verbose_name="Procesado"
    )
    fecha_procesado = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Procesado"
    )
    observaciones_equipo = models.TextField(
        blank=True,
        verbose_name="Observaciones del Equipo"
    )
    
    class Meta:
        verbose_name = "Equipo en Tarea"
        verbose_name_plural = "Equipos en Tareas"
        unique_together = ['tarea', 'equipo']
    
    def __str__(self):
        return f"{self.tarea.titulo} - {self.equipo.equipo_existente}"


class LogReordenamiento(models.Model):
    """Log de acciones realizadas en las tareas de reordenamiento"""
    tarea = models.ForeignKey(
        TareaReordenamiento,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    accion = models.CharField(
        max_length=100,
        verbose_name="Acción Realizada"
    )
    descripcion = models.TextField(
        verbose_name="Descripción de la Acción"
    )
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Log de Reordenamiento"
        verbose_name_plural = "Logs de Reordenamiento"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.tarea.titulo} - {self.accion} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"
