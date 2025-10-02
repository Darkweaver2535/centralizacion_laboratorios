from django.db import models
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field

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


# =====================================
# COMPONENTES DETALLADOS DE CONTENIDO ANALÍTICO
# =====================================

class Bibliografia(models.Model):
    """Bibliografia dentro del contenido analítico"""
    contenido_analitico = models.ForeignKey(ContenidoAnalitico, on_delete=models.CASCADE, related_name='bibliografias')
    titulo = models.CharField(max_length=300, verbose_name="Título de la bibliografía")
    autor = models.CharField(max_length=200, verbose_name="Autor")
    editorial = models.CharField(max_length=200, blank=True, verbose_name="Editorial")
    año_publicacion = models.IntegerField(blank=True, null=True, verbose_name="Año de publicación")
    paginas = models.CharField(max_length=50, blank=True, verbose_name="Páginas")
    isbn = models.CharField(max_length=50, blank=True, verbose_name="ISBN")
    tipo_referencia = models.CharField(max_length=50, choices=[
        ('libro', 'Libro'),
        ('articulo', 'Artículo'),
        ('tesis', 'Tesis'),
        ('manual', 'Manual'),
        ('web', 'Página Web'),
        ('otro', 'Otro')
    ], default='libro')
    orden = models.PositiveIntegerField(default=1, verbose_name="Orden de aparición")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Bibliografía"
        verbose_name_plural = "Bibliografías"
        ordering = ['orden', 'titulo']
    
    def __str__(self):
        return f"{self.titulo} - {self.autor}"


class PracticaLaboratorio(models.Model):
    """Práctica de laboratorio dentro del contenido analítico"""
    contenido_analitico = models.ForeignKey(ContenidoAnalitico, on_delete=models.CASCADE, related_name='practicas_laboratorio')
    nombre = models.CharField(max_length=300, verbose_name="Nombre de la práctica")
    duracion_horas = models.DecimalField(max_digits=4, decimal_places=1, default=2.0, verbose_name="Duración en horas")
    tipo_practica = models.CharField(max_length=50, choices=[
        ('individual', 'Individual'),
        ('grupal', 'Grupal'),
        ('demostrativa', 'Demostrativa'),
        ('virtual', 'Virtual')
    ], default='grupal')
    numero_estudiantes = models.PositiveIntegerField(default=1, verbose_name="Número de estudiantes")
    orden = models.PositiveIntegerField(default=1, verbose_name="Orden de la práctica")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Práctica de Laboratorio"
        verbose_name_plural = "Prácticas de Laboratorio"
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return f"Práctica {self.orden}: {self.nombre}"


class Titulo(models.Model):
    """Títulos/subtítulos dentro del contenido analítico"""
    contenido_analitico = models.ForeignKey(ContenidoAnalitico, on_delete=models.CASCADE, related_name='titulos')
    texto = models.CharField(max_length=300, verbose_name="Texto del título")
    nivel = models.PositiveIntegerField(default=1, choices=[
        (1, 'Título Principal'),
        (2, 'Subtítulo'),
        (3, 'Sub-subtítulo'),
        (4, 'Título de Sección'),
        (5, 'Título de Subsección')
    ], verbose_name="Nivel del título")
    orden = models.PositiveIntegerField(default=1, verbose_name="Orden de aparición")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Título"
        verbose_name_plural = "Títulos"
        ordering = ['orden', 'nivel']
    
    def __str__(self):
        return f"Nivel {self.nivel}: {self.texto}"


class Competencias(models.Model):
    """Competencias desarrolladas en el contenido analítico"""
    contenido_analitico = models.ForeignKey(ContenidoAnalitico, on_delete=models.CASCADE, related_name='competencias')
    descripcion = models.TextField(verbose_name="Descripción de la competencia")
    tipo_competencia = models.CharField(max_length=50, choices=[
        ('conceptual', 'Conceptual'),
        ('procedimental', 'Procedimental'),
        ('actitudinal', 'Actitudinal'),
        ('mixta', 'Mixta')
    ], default='conceptual')
    nivel_desarrollo = models.CharField(max_length=50, choices=[
        ('inicial', 'Inicial'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
        ('experto', 'Experto')
    ], default='inicial')
    orden = models.PositiveIntegerField(default=1, verbose_name="Orden de desarrollo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Competencia"
        verbose_name_plural = "Competencias"
        ordering = ['orden', 'tipo_competencia']
    
    def __str__(self):
        return f"{self.tipo_competencia}: {self.descripcion[:50]}..."


class ObjetivoPractica(models.Model):
    """Objetivos de las prácticas"""
    contenido_analitico = models.ForeignKey(ContenidoAnalitico, on_delete=models.CASCADE, related_name='objetivos_practica')
    descripcion = models.TextField(verbose_name="Descripción del objetivo")
    tipo_objetivo = models.CharField(max_length=50, choices=[
        ('general', 'General'),
        ('especifico', 'Específico'),
        ('aprendizaje', 'De Aprendizaje'),
        ('desempeno', 'De Desempeño')
    ], default='especifico')
    orden = models.PositiveIntegerField(default=1, verbose_name="Orden del objetivo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Objetivo de la Práctica"
        verbose_name_plural = "Objetivos de las Prácticas"
        ordering = ['orden', 'tipo_objetivo']
    
    def __str__(self):
        return f"{self.tipo_objetivo}: {self.descripcion[:50]}..."


class FundamentoTeorico(models.Model):
    """Fundamentos teóricos del contenido analítico"""
    contenido_analitico = models.ForeignKey(ContenidoAnalitico, on_delete=models.CASCADE, related_name='fundamentos_teoricos')
    titulo = models.CharField(max_length=200, verbose_name="Título del fundamento")
    contenido = CKEditor5Field('Contenido teórico', config_name='extends')
    referencias = CKEditor5Field('Referencias adicionales', config_name='default', blank=True)
    orden = models.PositiveIntegerField(default=1, verbose_name="Orden de presentación")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Fundamento Teórico"
        verbose_name_plural = "Fundamentos Teóricos"
        ordering = ['orden', 'titulo']
    
    def __str__(self):
        return f"{self.titulo}"


class MaterialesHerramientasEquipos(models.Model):
    """Materiales, herramientas y equipos necesarios"""
    contenido_analitico = models.ForeignKey(ContenidoAnalitico, on_delete=models.CASCADE, related_name='materiales_herramientas_equipos')
    nombre = models.CharField(max_length=200, verbose_name="Nombre del material/herramienta/equipo")
    tipo_elemento = models.CharField(max_length=50, choices=[
        ('material', 'Material'),
        ('herramienta', 'Herramienta'),
        ('equipo', 'Equipo'),
        ('reactivo', 'Reactivo'),
        ('software', 'Software'),
        ('otro', 'Otro')
    ], default='material')
    cantidad = models.CharField(max_length=50, verbose_name="Cantidad necesaria")
    especificaciones = models.TextField(blank=True, verbose_name="Especificaciones técnicas")
    es_obligatorio = models.BooleanField(default=True, verbose_name="¿Es obligatorio?")
    orden = models.PositiveIntegerField(default=1, verbose_name="Orden de listado")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Material/Herramienta/Equipo"
        verbose_name_plural = "Materiales/Herramientas/Equipos"
        ordering = ['tipo_elemento', 'orden']
    
    def __str__(self):
        return f"{self.tipo_elemento}: {self.nombre}"


class Procedimientos(models.Model):
    """Procedimientos paso a paso"""
    contenido_analitico = models.ForeignKey(ContenidoAnalitico, on_delete=models.CASCADE, related_name='procedimientos')
    numero_paso = models.PositiveIntegerField(verbose_name="Número del paso")
    titulo_paso = models.CharField(max_length=200, verbose_name="Título del paso")
    descripcion = CKEditor5Field('Descripción detallada del paso', config_name='extends')
    tiempo_estimado = models.CharField(max_length=50, blank=True, verbose_name="Tiempo estimado")
    precauciones = CKEditor5Field('Precauciones especiales', config_name='default', blank=True)
    observaciones = CKEditor5Field('Observaciones', config_name='default', blank=True)
    orden = models.PositiveIntegerField(default=1, verbose_name="Orden del procedimiento")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Procedimiento"
        verbose_name_plural = "Procedimientos"
        ordering = ['orden', 'numero_paso']
    
    def __str__(self):
        return f"Paso {self.numero_paso}: {self.titulo_paso}"


class CalculosResultados(models.Model):
    """Cálculos y resultados esperados"""
    contenido_analitico = models.ForeignKey(ContenidoAnalitico, on_delete=models.CASCADE, related_name='calculos_resultados')
    titulo = models.CharField(max_length=200, verbose_name="Título del cálculo/resultado")
    formula = models.TextField(blank=True, verbose_name="Fórmula utilizada")
    procedimiento_calculo = models.TextField(verbose_name="Procedimiento de cálculo")
    resultado_esperado = models.TextField(blank=True, verbose_name="Resultado esperado")
    unidades = models.CharField(max_length=50, blank=True, verbose_name="Unidades de medida")
    margen_error = models.CharField(max_length=50, blank=True, verbose_name="Margen de error aceptable")
    orden = models.PositiveIntegerField(default=1, verbose_name="Orden de cálculo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cálculo y Resultado"
        verbose_name_plural = "Cálculos y Resultados"
        ordering = ['orden', 'titulo']
    
    def __str__(self):
        return f"{self.titulo}"


class Cuestionario(models.Model):
    """Cuestionarios y preguntas de evaluación"""
    contenido_analitico = models.ForeignKey(ContenidoAnalitico, on_delete=models.CASCADE, related_name='cuestionarios')
    numero_pregunta = models.PositiveIntegerField(verbose_name="Número de pregunta")
    pregunta = models.TextField(verbose_name="Texto de la pregunta")
    tipo_pregunta = models.CharField(max_length=50, choices=[
        ('abierta', 'Pregunta Abierta'),
        ('cerrada', 'Pregunta Cerrada'),
        ('multiple', 'Opción Múltiple'),
        ('verdadero_falso', 'Verdadero/Falso'),
        ('calculo', 'Cálculo'),
        ('analisis', 'Análisis')
    ], default='abierta')
    respuesta_esperada = models.TextField(blank=True, verbose_name="Respuesta esperada o criterios")
    puntuacion = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, verbose_name="Puntuación")
    orden = models.PositiveIntegerField(default=1, verbose_name="Orden de la pregunta")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cuestionario"
        verbose_name_plural = "Cuestionarios"
        ordering = ['orden', 'numero_pregunta']
    
    def __str__(self):
        return f"Pregunta {self.numero_pregunta}: {self.pregunta[:50]}..."
