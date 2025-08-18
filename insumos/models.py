from django.db import models
from django.contrib.auth.models import User
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
    Modelo para insumos de laboratorio
    Similar estructura a equipos pero adaptada para insumos
    """
    
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('agotado', 'Agotado'),
        ('vencido', 'Vencido'),
        ('en_proceso', 'En Proceso de Compra'),
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
    ]
    
    # Información académica
    unidad_academica = models.ForeignKey(
        UnidadAcademica, 
        on_delete=models.CASCADE,
        verbose_name="Unidad Académica"
    )
    
    carrera = models.ForeignKey(
        Carrera, 
        on_delete=models.CASCADE,
        verbose_name="Carrera"
    )
    
    semestre = models.IntegerField(
        choices=[(i, f"{i}° Semestre") for i in range(1, 11)],
        verbose_name="Semestre"
    )
    
    asignatura = models.ForeignKey(
        Asignatura, 
        on_delete=models.CASCADE,
        verbose_name="Asignatura"
    )
    
    unidad_tematica = models.ForeignKey(
        UnidadTematica, 
        on_delete=models.CASCADE,
        verbose_name="Unidad Temática"
    )
    
    guia_laboratorio = models.ForeignKey(
        GuiaLaboratorio, 
        on_delete=models.CASCADE,
        verbose_name="Guía de Laboratorio"
    )
    
    practica = models.ForeignKey(
        Practica, 
        on_delete=models.CASCADE,
        verbose_name="Práctica"
    )
    
    # Información del insumo
    tipo_insumo = models.ForeignKey(
        TipoInsumo, 
        on_delete=models.CASCADE,
        verbose_name="Tipo de Insumo"
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del Insumo"
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    
    marca = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Marca"
    )
    
    modelo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Modelo"
    )
    
    # Inventario
    cantidad_actual = models.FloatField(
        default=0,
        verbose_name="Cantidad Actual"
    )
    
    cantidad_minima = models.FloatField(
        default=0,
        verbose_name="Cantidad Mínima",
        help_text="Cantidad mínima para alertas de stock"
    )
    
    cantidad_requerida = models.FloatField(
        default=0,
        verbose_name="Cantidad Requerida"
    )
    
    unidad_medida = models.CharField(
        max_length=20,
        choices=UNIDADES_MEDIDA,
        default='unidades',
        verbose_name="Unidad de Medida"
    )
    
    # Estado y ubicación
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='disponible',
        verbose_name="Estado"
    )
    
    laboratorio = models.ForeignKey(
        Laboratorio, 
        on_delete=models.CASCADE,
        verbose_name="Ubicación (Laboratorio)"
    )
    
    ubicacion_especifica = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ubicación Específica",
        help_text="Estante, cajón, etc."
    )
    
    # Información adicional
    fecha_vencimiento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Vencimiento"
    )
    
    numero_lote = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Número de Lote"
    )
    
    proveedor = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Proveedor"
    )
    
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Precio Unitario"
    )
    
    # Seguridad
    es_peligroso = models.BooleanField(
        default=False,
        verbose_name="Es Peligroso",
        help_text="Requiere manejo especial o EPP"
    )
    
    notas_seguridad = models.TextField(
        blank=True,
        verbose_name="Notas de Seguridad"
    )
    
    # Fotografías
    fotografia = models.ImageField(
        upload_to='insumos/fotos/',
        blank=True,
        null=True,
        verbose_name="Fotografía del Insumo"
    )
    
    # Auditoría
    usuario_creador = models.ForeignKey(
        User, 
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
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"
        ordering = ['unidad_academica', 'carrera', 'semestre', 'tipo_insumo', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.unidad_academica} - {self.carrera}"
    
    def save(self, *args, **kwargs):
        # Generar código de inventario automáticamente si no existe
        if not self.codigo_inventario:
            self.codigo_inventario = self.generar_codigo_inventario()
        super().save(*args, **kwargs)
    
    def generar_codigo_inventario(self):
        """Generar código de inventario único para insumos"""
        # Formato: INS-UA-CAR-SEM-NUM
        ua_code = self.unidad_academica.nombre[:3].upper()
        car_code = self.carrera.nombre[:3].upper()
        sem_code = f"S{self.semestre:02d}"
        
        # Obtener el siguiente número secuencial
        ultimo_insumo = Insumo.objects.filter(
            unidad_academica=self.unidad_academica,
            carrera=self.carrera,
            semestre=self.semestre
        ).order_by('-id').first()
        
        num = 1 if not ultimo_insumo else ultimo_insumo.id + 1
        
        return f"INS-{ua_code}-{car_code}-{sem_code}-{num:04d}"
    
    @property
    def esta_por_agotarse(self):
        """Verificar si el insumo está por agotarse"""
        return self.cantidad_actual <= self.cantidad_minima
    
    @property
    def esta_vencido(self):
        """Verificar si el insumo está vencido"""
        if not self.fecha_vencimiento:
            return False
        from django.utils import timezone
        return self.fecha_vencimiento < timezone.now().date()

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
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
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
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes_insumos')
    estado = models.CharField(max_length=20, choices=ESTADOS_SOLICITUD, default='pendiente')
    justificacion = models.TextField()
    observaciones = models.TextField(blank=True)
    
    # Campos para aprobación/rechazo
    revisado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='solicitudes_revisadas'
    )
    fecha_revision = models.DateTimeField(null=True, blank=True)
    motivo_rechazo = models.TextField(blank=True)
    
    # Campo para entrega
    entregado_por = models.ForeignKey(
        User, 
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
