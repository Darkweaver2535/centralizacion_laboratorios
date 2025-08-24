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
        verbose_name="Unidad Académica"
    )
    
    # 2. LABORATORIO
    laboratorio = models.ForeignKey(
        Laboratorio, 
        on_delete=models.CASCADE,
        verbose_name="Laboratorio"
    )
    
    # 3. CATEGORÍA
    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIAS,
        default='consumible',
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
        verbose_name="Cantidad"
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
    
    # 17. CONDICIONES DE ALMACENAMIENTO
    condiciones_almacenamiento = models.CharField(
        max_length=30,
        choices=CONDICIONES_ALMACENAMIENTO,
        blank=True,
        null=True,
        verbose_name="Condiciones de Almacenamiento"
    )
    
    # 18. OBSERVACIONES
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )
    
    # 19. INGRESE EL LINK DE LA FOTOGRAFÍA DEL ELEMENTO
    link_fotografia = models.URLField(
        blank=True,
        verbose_name="Link de la Fotografía del Elemento",
        help_text="URL de la imagen del elemento"
    )
    
    # Auditoría
    usuario_creador = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Usuario Creador"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"
        ordering = ['unidad_academica', 'carrera', 'categoria', 'nombre_elemento']
    
    def __str__(self):
        return f"{self.nombre_elemento} - {self.categoria} - {self.laboratorio}"
    
    def save(self, *args, **kwargs):
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
        # Formato: INS-UA-LAB-NUM
        ua_code = self.unidad_academica.nombre[:3].upper()
        lab_code = self.laboratorio.nombre[:3].upper()
        
        # Obtener el siguiente número secuencial
        ultimo_insumo = Insumo.objects.filter(
            unidad_academica=self.unidad_academica,
            laboratorio=self.laboratorio
        ).order_by('-id').first()
        
        if ultimo_insumo and ultimo_insumo.codigo_inventario:
            try:
                ultimo_num = int(ultimo_insumo.codigo_inventario.split('-')[-1])
                nuevo_num = ultimo_num + 1
            except (ValueError, IndexError):
                nuevo_num = 1
        else:
            nuevo_num = 1
        
        return f"INS-{ua_code}-{lab_code}-{nuevo_num:04d}"
    
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
