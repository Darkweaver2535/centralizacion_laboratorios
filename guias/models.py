from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import UnidadAcademica, Carrera, Asignatura, UnidadTematica, GuiaLaboratorio, Practica, Laboratorio


class GuiaGenerada(models.Model):
    """Modelo completo para almacenar las guías de laboratorio con todos los campos requeridos"""
    
    SEMESTRES = [
        ('1', 'Primer Semestre'),
        ('2', 'Segundo Semestre'),
        ('3', 'Tercer Semestre'),
        ('4', 'Cuarto Semestre'),
        ('5', 'Quinto Semestre'),
        ('6', 'Sexto Semestre'),
        ('7', 'Séptimo Semestre'),
        ('8', 'Octavo Semestre'),
        ('9', 'Noveno Semestre'),
        ('10', 'Décimo Semestre'),
    ]
    
    ESTADOS_GUIA = [
        ('borrador', 'Borrador'),
        ('revision', 'En Revisión'),
        ('aprobada', 'Aprobada'),
        ('publicada', 'Publicada'),
    ]
    
    TIPOS_PRACTICA = [
        ('laboratorio', 'Práctica de Laboratorio'),
        ('campo', 'Práctica de Campo'),
        ('simulacion', 'Simulación'),
        ('proyecto', 'Proyecto'),
        ('investigacion', 'Investigación'),
    ]
    
    # === INFORMACIÓN CURRICULAR ===
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, verbose_name="Carrera", db_index=True)
    semestre = models.CharField(max_length=2, choices=SEMESTRES, verbose_name="Semestre")
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, verbose_name="Asignatura", db_index=True)
    contenido_analitico = models.TextField(verbose_name="Contenido Analítico")
    unidad_didactica = models.CharField(max_length=200, verbose_name="Unidad Didáctica")
    
    # === INFORMACIÓN BÁSICA DE LA GUÍA ===
    titulo = models.CharField(max_length=200, verbose_name="Título de la Guía")
    codigo_guia = models.CharField(max_length=50, blank=True, verbose_name="Código de la Guía")
    tipo_practica = models.CharField(max_length=50, choices=TIPOS_PRACTICA, default='laboratorio', verbose_name="Tipo de Práctica")
    duracion_horas = models.PositiveIntegerField(
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(8)],
        verbose_name="Duración en Horas",
        help_text="Debe ser entre 1 y 8 horas"
    )
    numero_practica = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Número de Práctica",
        help_text="Debe ser mayor a 0"
    )
    
    # === CAMPOS CRÍTICOS FALTANTES ===
    # 1. Referencia Bibliográfica
    referencia_bibliografica = models.TextField(
        blank=True,
        verbose_name="Referencia Bibliográfica",
        help_text="Referencias bibliográficas y fuentes consultadas"
    )
    
    # 2. Competencias
    competencias = models.TextField(
        verbose_name="Competencias",
        help_text="Competencias específicas que desarrolla esta práctica"
    )
    
    # 3. Objetivo
    objetivo_general = models.TextField(
        verbose_name="Objetivo General",
        help_text="Objetivo general de la práctica de laboratorio"
    )
    objetivos_especificos = models.TextField(
        blank=True,
        verbose_name="Objetivos Específicos",
        help_text="Objetivos específicos detallados"
    )
    
    # 4. Procedimientos
    procedimientos = models.TextField(
        verbose_name="Procedimientos",
        help_text="Pasos detallados para realizar la práctica"
    )
    
    preparacion_previa = models.TextField(
        blank=True,
        verbose_name="Preparación Previa",
        help_text="Actividades que el estudiante debe realizar antes de la práctica"
    )
    
    # 5. Cuestionario
    cuestionario = models.TextField(
        verbose_name="Cuestionario",
        help_text="Preguntas de evaluación y análisis de resultados"
    )
    
    # === RELACIONES MANY-TO-MANY CRÍTICAS ===
    # Relación con Equipos
    equipos_requeridos = models.ManyToManyField(
        'equipos.Equipo',
        blank=True,
        verbose_name="Equipos Requeridos",
        help_text="Equipos necesarios para esta práctica"
    )
    
    # Relación con Insumos
    insumos_requeridos = models.ManyToManyField(
        'insumos.Insumo',
        blank=True,
        verbose_name="Insumos Requeridos",
        help_text="Insumos y materiales necesarios"
    )
    
    # === CAMPOS ADICIONALES ÚTILES ===
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_GUIA,
        default='borrador',
        verbose_name="Estado de la Guía"
    )
    
    resultados_esperados = models.TextField(
        blank=True,
        verbose_name="Resultados Esperados",
        help_text="Resultados que se esperan obtener"
    )
    
    criterios_evaluacion = models.TextField(
        blank=True,
        verbose_name="Criterios de Evaluación",
        help_text="Criterios para evaluar el desempeño del estudiante"
    )
    
    medidas_seguridad = models.TextField(
        blank=True,
        verbose_name="Medidas de Seguridad",
        help_text="Normas de seguridad a considerar"
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones",
        help_text="Observaciones adicionales para el instructor"
    )
    
    # === INFORMACIÓN DEL USUARIO Y METADATOS ===
    usuario_creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Creado por")
    
    # Archivos generados
    archivo_word = models.FileField(upload_to='guias/word/', blank=True, verbose_name="Archivo Word")
    archivo_pdf = models.FileField(upload_to='guias/pdf/', blank=True, verbose_name="Archivo PDF")
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Guía Generada"
        verbose_name_plural = "Guías Generadas"
        ordering = ['-created_at', 'carrera', 'asignatura', 'numero_practica']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['carrera', 'asignatura']),
            models.Index(fields=['carrera', 'semestre']),
            models.Index(fields=['tipo_practica', 'created_at']),
        ]
    
    def __str__(self):
        return f"Guía: {self.titulo} - {self.asignatura.nombre}"
