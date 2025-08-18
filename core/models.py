from django.db import models
from django.contrib.auth.models import User

class UnidadAcademica(models.Model):
    """Modelo base para las unidades académicas"""
    UNIDADES = [
        ('UASC', 'UASC - Unidad Académica Santa Cruz'),
        ('UARIBE', 'UARIBE - Unidad Académica Riberalta'),
        ('UATROP', 'UATROP - Unidad Académica Trinidad'),
        ('UACBBA', 'UACBBA - Unidad Académica Cochabamba'),
    ]
    
    nombre = models.CharField(max_length=20, choices=UNIDADES, unique=True)
    descripcion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Unidad Académica"
        verbose_name_plural = "Unidades Académicas"
        ordering = ['nombre']
    
    def __str__(self):
        return self.get_nombre_display()

class Carrera(models.Model):
    """Modelo base para las carreras"""
    CARRERAS = [
        ('ING_SISTEMAS', 'Ingeniería de Sistemas'),
        ('ING_INDUSTRIAL', 'Ingeniería Industrial'),
        ('ING_COMERCIAL', 'Ingeniería Comercial'),
        ('ING_CIVIL', 'Ingeniería Civil'),
        ('ING_PETROLERA', 'Ingeniería Petrolera'),
        ('ING_QUIMICA', 'Ingeniería Química'),
        ('ING_MECATRONICA', 'Ingeniería Mecatrónica'),
        ('LIC_BIOTECNOLOGIA', 'Licenciatura en Biotecnología'),
        ('ING_SISTEMAS_RIBE', 'Ingeniería de Sistemas (Riberalta)'),
        ('ING_COMERCIAL_RIBE', 'Ingeniería Comercial (Riberalta)'),
        ('ING_SISTEMAS_TROP', 'Ingeniería de Sistemas (Trópico)'),
        ('ING_SISTEMAS_CBBA', 'Ingeniería de Sistemas (Cochabamba)'),
        ('ING_INDUSTRIAL_CBBA', 'Ingeniería Industrial (Cochabamba)'),
        ('ING_COMERCIAL_CBBA', 'Ingeniería Comercial (Cochabamba)'),
    ]
    
    unidad_academica = models.ForeignKey(UnidadAcademica, on_delete=models.CASCADE, related_name='carreras')
    nombre = models.CharField(max_length=50, choices=CARRERAS)
    descripcion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"
        unique_together = ['unidad_academica', 'nombre']
        ordering = ['nombre']
    
    def __str__(self):
        return self.get_nombre_display()

class Asignatura(models.Model):
    """Modelo base para las asignaturas"""
    
    # Asignaturas comunes organizadas por semestre
    ASIGNATURAS_POR_SEMESTRE = {
        1: [
            ('matematica_i', 'Matemática I'),
            ('fisica_i', 'Física I'),
            ('quimica_general', 'Química General'),
            ('dibujo_tecnico', 'Dibujo Técnico'),
            ('introduccion_ingenieria', 'Introducción a la Ingeniería'),
        ],
        2: [
            ('matematica_ii', 'Matemática II'),
            ('fisica_ii', 'Física II'),
            ('quimica_organica', 'Química Orgánica'),
            ('programacion_i', 'Programación I'),
            ('metodologia_investigacion', 'Metodología de la Investigación'),
        ],
        3: [
            ('matematica_iii', 'Matemática III'),
            ('fisica_iii', 'Física III'),
            ('mecanica_materiales', 'Mecánica de Materiales'),
            ('programacion_ii', 'Programación II'),
            ('estadistica_probabilidades', 'Estadística y Probabilidades'),
        ],
        4: [
            ('matematica_iv', 'Matemática IV'),
            ('termodinamica', 'Termodinámica'),
            ('resistencia_materiales', 'Resistencia de Materiales'),
            ('circuitos_electricos', 'Circuitos Eléctricos'),
            ('economia_ingenieria', 'Economía para Ingeniería'),
        ],
        5: [
            ('ecuaciones_diferenciales', 'Ecuaciones Diferenciales'),
            ('mecanica_fluidos', 'Mecánica de Fluidos'),
            ('analisis_sistemas', 'Análisis de Sistemas'),
            ('electronica_basica', 'Electrónica Básica'),
            ('gestion_proyectos', 'Gestión de Proyectos'),
        ],
        6: [
            ('metodos_numericos', 'Métodos Numéricos'),
            ('transferencia_calor', 'Transferencia de Calor'),
            ('bases_datos', 'Bases de Datos'),
            ('sistemas_control', 'Sistemas de Control'),
            ('investigacion_operativa', 'Investigación Operativa'),
        ],
        7: [
            ('simulacion_sistemas', 'Simulación de Sistemas'),
            ('ingenieria_software', 'Ingeniería de Software'),
            ('automatizacion_industrial', 'Automatización Industrial'),
            ('gestion_calidad', 'Gestión de Calidad'),
            ('evaluacion_proyectos', 'Evaluación de Proyectos'),
        ],
        8: [
            ('inteligencia_artificial', 'Inteligencia Artificial'),
            ('redes_computadoras', 'Redes de Computadoras'),
            ('procesos_industriales', 'Procesos Industriales'),
            ('seguridad_industrial', 'Seguridad Industrial'),
            ('formulacion_proyectos', 'Formulación de Proyectos'),
        ],
        9: [
            ('proyecto_grado_i', 'Proyecto de Grado I'),
            ('sistemas_distribuidos', 'Sistemas Distribuidos'),
            ('optimizacion_procesos', 'Optimización de Procesos'),
            ('gestion_ambiental', 'Gestión Ambiental'),
            ('practica_profesional', 'Práctica Profesional'),
        ],
        10: [
            ('proyecto_grado_ii', 'Proyecto de Grado II'),
            ('auditoria_sistemas', 'Auditoría de Sistemas'),
            ('mantenimiento_industrial', 'Mantenimiento Industrial'),
            ('legislacion_profesional', 'Legislación Profesional'),
            ('seminario_titulacion', 'Seminario de Titulación'),
        ],
    }
    
    nombre = models.CharField(max_length=50, choices=[])
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    semestre = models.IntegerField(choices=[(i, f"{i}° Semestre") for i in range(1, 11)])
    carga_horaria_semanal = models.IntegerField(help_text="Horas por semana")
    carga_horaria_semestral = models.IntegerField(help_text="Total de horas en el semestre")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Construir choices dinámicamente
        choices = []
        for semestre, materias in self.ASIGNATURAS_POR_SEMESTRE.items():
            choices.extend(materias)
        self._meta.get_field('nombre').choices = choices
    
    class Meta:
        verbose_name = "Asignatura"
        verbose_name_plural = "Asignaturas"
        ordering = ['semestre', 'nombre']
        unique_together = ['nombre', 'carrera', 'semestre']
    
    def __str__(self):
        return f"{self.get_nombre_display()} - {self.carrera} - {self.semestre}° Semestre"
    
    @classmethod
    def get_asignaturas_por_semestre(cls, semestre):
        """Obtener asignaturas disponibles para un semestre específico"""
        return cls.ASIGNATURAS_POR_SEMESTRE.get(semestre, [])

class UnidadTematica(models.Model):
    """Unidades temáticas dentro de una asignatura"""
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, related_name='unidades_tematicas')
    nombre = models.CharField(max_length=200)
    numero = models.IntegerField(help_text="Número de la unidad temática")
    descripcion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Unidad Temática"
        verbose_name_plural = "Unidades Temáticas"
        ordering = ['numero']
        unique_together = ['asignatura', 'numero']
    
    def __str__(self):
        return f"Unidad {self.numero}: {self.nombre} - {self.asignatura}"

class GuiaLaboratorio(models.Model):
    """Guías de laboratorio por unidad temática"""
    unidad_tematica = models.ForeignKey(UnidadTematica, on_delete=models.CASCADE, related_name='guias_laboratorio')
    nombre = models.CharField(max_length=200)
    numero = models.IntegerField(help_text="Número de la guía")
    descripcion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Guía de Laboratorio"
        verbose_name_plural = "Guías de Laboratorio"
        ordering = ['numero']
        unique_together = ['unidad_tematica', 'numero']
    
    def __str__(self):
        return f"Guía {self.numero}: {self.nombre}"

class Practica(models.Model):
    """Prácticas de laboratorio"""
    guia_laboratorio = models.ForeignKey(GuiaLaboratorio, on_delete=models.CASCADE, related_name='practicas')
    nombre = models.CharField(max_length=200)
    numero = models.IntegerField(help_text="Número de la práctica")
    descripcion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Práctica"
        verbose_name_plural = "Prácticas"
        ordering = ['numero']
        unique_together = ['guia_laboratorio', 'numero']
    
    def __str__(self):
        return f"Práctica {self.numero}: {self.nombre}"

class Laboratorio(models.Model):
    """Laboratorios físicos donde se ubican equipos"""
    LABORATORIOS = [
        ('LAB_FISICA_1', 'Laboratorio de Física Piso 1'),
        ('LAB_FISICA_4', 'Laboratorio de Física Piso 4'),
        ('LAB_QUIMICA', 'Laboratorio de Química'),
        ('LAB_BIOTECNOLOGIA', 'Laboratorio de Biotecnología'),
        ('LAB_SISTEMAS_1', 'Laboratorio de Sistemas Piso 1'),
        ('LAB_SISTEMAS_I', 'Laboratorio de Sistemas I'),
        ('LAB_MECATRONICA', 'Laboratorio de Mecatrónica'),
        ('LAB_INDUSTRIAL', 'Laboratorio Industrial'),
        ('LAB_CIVIL', 'Laboratorio de Civil'),
        ('LAB_COMERCIAL_301', 'Laboratorio Comercial Aula 301'),
        ('LAB_EDAFOLOGIA', 'Laboratorio de Edafología'),
        ('LAB_CIENCIAS_BASICAS', 'Laboratorio de Ciencias Básicas'),
        ('LAB_PETROLERA', 'Laboratorio Petrolero y Geográfico'),
        ('OFICINAS_UICYT', 'Oficinas Unidad de Investigación'),
    ]
    
    nombre = models.CharField(max_length=50, choices=LABORATORIOS)
    descripcion = models.TextField(blank=True)
    ubicacion = models.CharField(max_length=200, blank=True, help_text="Ubicación física del laboratorio")
    capacidad = models.PositiveIntegerField(default=25, help_text="Capacidad de estudiantes")
    responsable = models.CharField(max_length=200, blank=True, help_text="Responsable del laboratorio")
    seccion_area = models.CharField(max_length=100, blank=True, help_text="Sección o área específica")
    identificador_aula = models.CharField(max_length=50, blank=True, help_text="Número de aula o identificador")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Laboratorio"
        verbose_name_plural = "Laboratorios"
        ordering = ['nombre']
    
    def __str__(self):
        return self.get_nombre_display()
