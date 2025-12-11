from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.models import UnidadAcademica, Carrera, Asignatura, Laboratorio

class ActivoFijo(models.Model):
    """
    Modelo para activos fijos institucionales con información completa
    """
    
    # Categorías de activos fijos
    CATEGORIAS = [
        ('equipos_computo', 'Equipos de Cómputo'),
        ('mobiliario', 'Mobiliario y Enseres'),
        ('vehiculos', 'Vehículos'),
        ('maquinaria', 'Maquinaria y Equipos'),
        ('equipos_laboratorio', 'Equipos de Laboratorio'),
        ('equipos_audiovisuales', 'Equipos Audiovisuales'),
        ('instrumentos', 'Instrumentos y Herramientas'),
        ('infraestructura', 'Infraestructura'),
        ('bibliotecas', 'Material Bibliográfico'),
        ('otros', 'Otros Activos'),
    ]
    
    ESTADOS_FISICOS = [
        ('excelente', 'Excelente'),
        ('muy_bueno', 'Muy Bueno'),
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('malo', 'Malo'),
        ('inservible', 'Inservible'),
        ('en_reparacion', 'En Reparación'),
        ('dado_de_baja', 'Dado de Baja'),
    ]
    
    ESTADOS_OPERATIVOS = [
        ('operativo', 'Operativo'),
        ('no_operativo', 'No Operativo'),
        ('en_mantenimiento', 'En Mantenimiento'),
        ('fuera_de_servicio', 'Fuera de Servicio'),
        ('pendiente_revision', 'Pendiente de Revisión'),
        ('en_prestamo', 'En Préstamo'),
        ('almacenado', 'Almacenado'),
        ('transferido', 'Transferido'),
    ]
    
    METODOS_ADQUISICION = [
        ('compra', 'Compra Directa'),
        ('licitacion', 'Licitación Pública'),
        ('donacion', 'Donación'),
        ('transferencia', 'Transferencia'),
        ('intercambio', 'Intercambio'),
        ('fabricacion_propia', 'Fabricación Propia'),
        ('arrendamiento', 'Arrendamiento Financiero'),
        ('otros', 'Otros Métodos'),
    ]
    
    # === INFORMACIÓN BÁSICA ===
    
    # Código patrimonial único
    codigo_patrimonial = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name="Código Patrimonial",
        help_text="Código único del activo fijo"
    )
    
    # Nombre del activo
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del Activo",
        help_text="Nombre descriptivo del activo fijo"
    )
    
    # Descripción detallada
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción detallada del activo, características, especificaciones"
    )
    
    # Categoría
    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIAS,
        verbose_name="Categoría",
        help_text="Tipo/categoría del activo fijo"
    )
    
    # === INFORMACIÓN PATRIMONIAL ===
    
    # Valor de adquisición
    valor_adquisicion = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor de Adquisición (Bs.)",
        help_text="Valor original de compra en bolivianos"
    )
    
    # Valor actual/depreciado
    valor_actual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        blank=True,
        null=True,
        verbose_name="Valor Actual (Bs.)",
        help_text="Valor actual considerando depreciación"
    )
    
    # Fecha de adquisición
    fecha_adquisicion = models.DateField(
        verbose_name="Fecha de Adquisición",
        help_text="Fecha en que se adquirió el activo"
    )
    
    # Método de adquisición
    metodo_adquisicion = models.CharField(
        max_length=50,
        choices=METODOS_ADQUISICION,
        verbose_name="Método de Adquisición"
    )
    
    # Proveedor
    proveedor = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Proveedor",
        help_text="Empresa o entidad proveedora"
    )
    
    # === INFORMACIÓN TÉCNICA ===
    
    # Marca
    marca = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Marca"
    )
    
    # Modelo
    modelo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Modelo"
    )
    
    # Número de serie
    numero_serie = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Número de Serie"
    )
    
    # Año de fabricación
    año_fabricacion = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Año de Fabricación"
    )
    
    # === UBICACIÓN Y ASIGNACIÓN ===
    
    # Unidad académica
    unidad_academica = models.ForeignKey(
        UnidadAcademica,
        on_delete=models.CASCADE,
        verbose_name="Unidad Académica"
    )
    
    # Laboratorio (opcional)
    laboratorio = models.ForeignKey(
        Laboratorio,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Laboratorio"
    )
    
    # Carrera (opcional)
    carrera = models.ForeignKey(
        Carrera,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Carrera"
    )
    
    # Ubicación física específica
    ubicacion_fisica = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ubicación Física",
        help_text="Edificio, aula, oficina, etc."
    )
    
    # === ESTADOS Y CONDICIÓN ===
    
    # Estado físico
    estado_fisico = models.CharField(
        max_length=50,
        choices=ESTADOS_FISICOS,
        default='bueno',
        verbose_name="Estado Físico"
    )
    
    # Estado operativo
    estado_operativo = models.CharField(
        max_length=50,
        choices=ESTADOS_OPERATIVOS,
        default='operativo',
        verbose_name="Estado Operativo"
    )
    
    # === RESPONSABILIDAD ===
    
    # Responsable actual
    responsable = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Responsable Actual",
        help_text="Nombre de la persona responsable"
    )
    
    # === OBSERVACIONES Y NOTAS ===
    
    # Observaciones generales
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones Generales"
    )
    
    # === METADATOS ===
    
    # Usuario que creó el registro
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activos_creados',
        verbose_name="Creado por"
    )
    
    # Fechas de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # === META CONFIGURACIÓN ===
    
    class Meta:
        verbose_name = "Activo Fijo"
        verbose_name_plural = "Activos Fijos"
        ordering = ['codigo_patrimonial']
    
    def __str__(self):
        return f"{self.codigo_patrimonial} - {self.nombre}"
    
    def get_nombre_display(self):
        """Retorna nombre completo del activo"""
        if self.marca and self.modelo:
            return f"{self.nombre} {self.marca} {self.modelo}"
        elif self.marca:
            return f"{self.nombre} {self.marca}"
        else:
            return self.nombre
    
    def get_valor_display(self):
        """Retorna valor formateado"""
        return f"Bs. {self.valor_adquisicion:,.2f}"
    
    def get_estado_display(self):
        """Retorna estado combinado físico-operativo"""
        fisico = self.get_estado_fisico_display()
        operativo = self.get_estado_operativo_display()
        return f"{fisico} / {operativo}"
