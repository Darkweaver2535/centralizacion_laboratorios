from django.db import models
from django.conf import settings

class UnidadAcademica(models.Model):
    """Modelo base para las unidades académicas"""
    UNIDADES = [
        ('UALP', 'UALP - La Paz'),
        ('UACB', 'UACB - Cochabamba'),
        ('UASC', 'UASC - Santa Cruz'),
        ('UATP', 'UATP - Trópico'),
        ('UARB', 'UARB - Riberalta'),
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
        ('ING_CIVIL', 'Ingeniería Civil'),
        ('ING_GEOGRAFICA', 'Ingeniería Geográfica'),
        ('ING_SISTEMAS_ELECTRONICOS', 'Ingeniería en Sistemas Electrónicos'),
        ('ING_INDUSTRIAL', 'Ingeniería Industrial'),
        ('ING_COMERCIAL', 'Ingeniería Comercial'),
        ('ING_SISTEMAS', 'Ingeniería de Sistemas'),
        ('ING_AMBIENTAL', 'Ingeniería Ambiental'),
        ('ING_PETROLERA', 'Ingeniería Petrolera'),
        ('ING_MECATRONICA', 'Ingeniería Mecatrónica'),
        ('ING_TELECOMUNICACIONES', 'Ingeniería en Telecomunicaciones'),
        ('ING_FINANCIERA', 'Ingeniería Financiera'),
        ('ING_AGROINDUSTRIAL', 'Ingeniería Agroindustrial'),
        ('ING_AGRONOMICA', 'Ingeniería Agronómica'),
        ('INFORMATICA', 'Informática'),
        ('SISTEMAS_ELECTRONICOS', 'Sistemas Electrónicos'),
        ('ENERGIAS_RENOVABLES', 'Energías Renovables'),
        ('CONSTRUCCION_CIVIL', 'Construcción Civil'),
        ('DISENO_GRAFICO', 'Diseño Gráfico y Comunicación Audiovisual'),
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
    
    # Asignaturas básicas comunes
    ASIGNATURAS_CHOICES = [
        # Matemáticas y Ciencias Básicas
        ('matematica_i', 'Matemática I'),
        ('matematica_ii', 'Matemática II'),
        ('matematica_iii', 'Matemática III'),
        ('matematica_iv', 'Matemática IV'),
        ('fisica_i', 'Física I'),
        ('fisica_ii', 'Física II'),
        ('fisica_iii', 'Física III'),
        ('quimica_general', 'Química General'),
        ('fisicoquimica', 'Fisicoquímica'),
        ('quimica_organica', 'Química Orgánica'),
        ('estadistica_probabilidades', 'Estadística y Probabilidades'),
        ('ecuaciones_diferenciales', 'Ecuaciones Diferenciales'),
        ('metodos_numericos', 'Métodos Numéricos'),
        
        # Programación y Sistemas
        ('programacion_i', 'Programación I'),
        ('programacion_ii', 'Programación II'),
        ('bases_datos', 'Bases de Datos'),
        ('analisis_sistemas', 'Análisis de Sistemas'),
        ('ingenieria_software', 'Ingeniería de Software'),
        ('redes_computadoras', 'Redes de Computadoras'),
        ('sistemas_distribuidos', 'Sistemas Distribuidos'),
        ('inteligencia_artificial', 'Inteligencia Artificial'),
        ('simulacion_sistemas', 'Simulación de Sistemas'),
        ('auditoria_sistemas', 'Auditoría de Sistemas'),
        
        # Ingeniería Básica
        ('dibujo_tecnico', 'Dibujo Técnico'),
        ('mecanica_materiales', 'Mecánica de Materiales'),
        ('resistencia_materiales', 'Resistencia de Materiales'),
        ('termodinamica', 'Termodinámica'),
        ('mecanica_fluidos', 'Mecánica de Fluidos'),
        ('transferencia_calor', 'Transferencia de Calor'),
        ('circuitos_electricos', 'Circuitos Eléctricos'),
        ('electronica_basica', 'Electrónica Básica'),
        ('sistemas_control', 'Sistemas de Control'),
        ('automatizacion_industrial', 'Automatización Industrial'),
        
        # Gestión y Administración
        ('economia_ingenieria', 'Economía para Ingeniería'),
        ('gestion_proyectos', 'Gestión de Proyectos'),
        ('evaluacion_proyectos', 'Evaluación de Proyectos'),
        ('formulacion_proyectos', 'Formulación de Proyectos'),
        ('investigacion_operativa', 'Investigación Operativa'),
        ('gestion_calidad', 'Gestión de Calidad'),
        ('calidad_procesos', 'Calidad de Procesos'),
        ('liderazgo_equipos', 'Liderazgo de Equipos'),
        ('emprendimiento', 'Emprendimiento'),
        
        # Procesos Industriales
        ('procesos_industriales', 'Procesos Industriales'),
        ('optimizacion_procesos', 'Optimización de Procesos'),
        ('mantenimiento_industrial', 'Mantenimiento Industrial'),
        ('seguridad_industrial', 'Seguridad Industrial'),
        ('gestion_ambiental', 'Gestión Ambiental'),
        ('desarrollo_sostenible', 'Desarrollo Sostenible'),
        ('innovacion_tecnologica', 'Innovación Tecnológica'),
        
        # Idiomas y Comunicación
        ('ingles_tecnico_i', 'Inglés Técnico I'),
        ('ingles_tecnico_ii', 'Inglés Técnico II'),
        ('comunicacion_tecnica', 'Comunicación Técnica'),
        ('metodologia_investigacion', 'Metodología de la Investigación'),
        
        # Formación General
        ('introduccion_ingenieria', 'Introducción a la Ingeniería'),
        ('etica_profesional', 'Ética Profesional'),
        ('legislacion_profesional', 'Legislación Profesional'),
        ('responsabilidad_social', 'Responsabilidad Social'),
        
        # Proyecto de Grado
        ('proyecto_grado_i', 'Proyecto de Grado I'),
        ('proyecto_grado_ii', 'Proyecto de Grado II'),
        ('seminario_titulacion', 'Seminario de Titulación'),
        ('practica_profesional', 'Práctica Profesional'),
    ]
    
    nombre = models.CharField(max_length=50, choices=ASIGNATURAS_CHOICES)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='asignaturas')
    semestre = models.IntegerField(choices=[(i, f"{i}° Semestre") for i in range(1, 11)])
    carga_horaria_semanal = models.IntegerField(default=4, help_text="Horas por semana")
    carga_horaria_semestral = models.IntegerField(default=80, help_text="Total de horas en el semestre")
    
    # Nuevos campos de malla curricular
    codigo_competencia = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name='Código de Competencia',
        help_text='Código de competencia de la materia'
    )
    sigla_curricular = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name='Sigla Curricular',
        help_text='Sigla curricular de la asignatura'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Asignatura"
        verbose_name_plural = "Asignaturas"
        ordering = ['semestre', 'nombre']
        unique_together = ['nombre', 'carrera', 'semestre']
    
    def __str__(self):
        return f"{self.get_nombre_display()} - {self.carrera} - {self.semestre}° Semestre"

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
        # Laboratorios según Excel de recopilación de materiales
        ('LAB_TRATAMIENTO_AGUAS', 'Planta de Tratamiento de Aguas'),
        ('LAB_ASFALTOS', 'Laboratorio de Asfaltos'),
        ('LAB_HORMIGONES', 'Laboratorio de Hormigones'),
        ('LAB_RESISTENCIA_MATERIALES', 'Laboratorio de Resistencia de Materiales y Suelos'),
        ('LAB_LACTEOS', 'Laboratorio de Lácteos'),
        
        # Laboratorios adicionales comunes en universidades técnicas
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


class CriterioDesempeno(models.Model):
    """Modelo para criterios de desempeño"""
    nombre = models.CharField(max_length=200, unique=True, verbose_name="Criterio de Desempeño")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, related_name='criterios_desempeno')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Criterio de Desempeño"
        verbose_name_plural = "Criterios de Desempeño"
        ordering = ['nombre']
    
    def __str__(self):
        return self.descripcion[:100] + "..." if len(self.descripcion) > 100 else self.descripcion


class UnidadDidactica(models.Model):
    """Modelo para unidades didácticas"""
    nombre = models.CharField(max_length=200, unique=True, verbose_name="Unidad Didáctica")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, related_name='unidades_didacticas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Unidad Didáctica"
        verbose_name_plural = "Unidades Didácticas"
        ordering = ['nombre']
    
    def __str__(self):
        return self.descripcion[:100] + "..." if len(self.descripcion) > 100 else self.descripcion


class ContenidoAnalitico(models.Model):
    """Modelo para contenidos analíticos"""
    nombre = models.CharField(max_length=300, unique=True, verbose_name="Contenido Analítico")
    descripcion = models.TextField(blank=True, verbose_name="Descripción detallada")
    unidad_didactica = models.ForeignKey(UnidadDidactica, on_delete=models.CASCADE, related_name='contenidos_analiticos')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Contenido Analítico"
        verbose_name_plural = "Contenidos Analíticos"
        ordering = ['nombre']
    
    def __str__(self):
        return self.descripcion[:100] + "..." if self.descripcion and len(self.descripcion) > 100 else (self.descripcion or self.nombre)
