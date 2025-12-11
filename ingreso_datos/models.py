from django.db import models
from django.conf import settings

class UnidadAcademica(models.Model):
    UNIDADES = [
        ('la_paz', 'La Paz'),
        ('cochabamba', 'Cochabamba'),
        ('santa_cruz', 'Santa Cruz'),
        ('riberalta', 'Riberalta'),
        ('tropico', 'Trópico'),
    ]
    
    nombre = models.CharField(max_length=20, choices=UNIDADES, unique=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Unidad Académica'
        verbose_name_plural = 'Unidades Académicas'
    
    def __str__(self):
        return self.get_nombre_display()

class Carrera(models.Model):
    CARRERAS = [
        ('ingenieria_ambiental', 'Ingeniería Ambiental'),
        ('ingenieria_civil', 'Ingeniería Civil'),
        ('ingenieria_sistemas_electronicos', 'Ingeniería en Sistemas Electrónicos'),
        ('ingenieria_comercial', 'Ingeniería Comercial'),
        ('ingenieria_sistemas', 'Ingeniería de Sistemas'),
        ('ingenieria_agroindustrial', 'Ingeniería Agroindustrial'),
        ('sistemas_electronicos', 'Sistemas Electrónicos'),
        ('informatica', 'Informática'),
        ('construccion_civil', 'Construcción Civil'),
        ('energias_renovables', 'Energías Renovables'),
        ('diseno_grafico', 'Diseño Gráfico y Comunicación Audiovisual'),
    ]
    
    nombre = models.CharField(max_length=50, choices=CARRERAS, unique=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Carrera'
        verbose_name_plural = 'Carreras'
    
    def __str__(self):
        return self.get_nombre_display()

class Asignatura(models.Model):
    """Nuevo modelo para asignaturas con información extendida"""
    
    # Asignaturas comunes por semestre
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Generar choices dinámicamente basado en todas las asignaturas
        all_asignaturas = []
        for asignaturas_list in self.ASIGNATURAS_POR_SEMESTRE.values():
            all_asignaturas.extend(asignaturas_list)
        self._meta.get_field('nombre').choices = list(set(all_asignaturas))
    
    class Meta:
        verbose_name = 'Asignatura'
        verbose_name_plural = 'Asignaturas'
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
    
    class Meta:
        verbose_name = 'Unidad Temática'
        verbose_name_plural = 'Unidades Temáticas'
        unique_together = ['asignatura', 'numero']
        ordering = ['asignatura', 'numero']
    
    def __str__(self):
        return f"Unidad {self.numero}: {self.nombre} ({self.asignatura})"

class GuiaLaboratorio(models.Model):
    """Guías de laboratorio por unidad temática"""
    unidad_tematica = models.ForeignKey(UnidadTematica, on_delete=models.CASCADE, related_name='guias_laboratorio')
    nombre = models.CharField(max_length=200)
    numero = models.IntegerField(help_text="Número de la guía")
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Guía de Laboratorio'
        verbose_name_plural = 'Guías de Laboratorio'
        unique_together = ['unidad_tematica', 'numero']
        ordering = ['unidad_tematica', 'numero']
    
    def __str__(self):
        return f"Guía {self.numero}: {self.nombre} ({self.unidad_tematica.asignatura})"

class Practica(models.Model):
    """Prácticas de laboratorio"""
    guia_laboratorio = models.ForeignKey(GuiaLaboratorio, on_delete=models.CASCADE, related_name='practicas')
    nombre = models.CharField(max_length=200)
    numero = models.IntegerField(help_text="Número de la práctica")
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Práctica'
        verbose_name_plural = 'Prácticas'
        unique_together = ['guia_laboratorio', 'numero']
        ordering = ['guia_laboratorio', 'numero']
    
    def __str__(self):
        return f"Práctica {self.numero}: {self.nombre}"

class Laboratorio(models.Model):
    """Laboratorios físicos"""
    LABORATORIOS = [
        ('lab_fisica_mecanica', 'Laboratorio de Física Mecánica'),
        ('lab_quimica_general', 'Laboratorio de Química General'),
        ('lab_electronica_basica', 'Laboratorio de Electrónica Básica'),
        ('lab_programacion', 'Laboratorio de Programación'),
        ('lab_circuitos_electricos', 'Laboratorio de Circuitos Eléctricos'),
        ('lab_materiales_resistencia', 'Laboratorio de Materiales y Resistencia'),
        ('lab_fluidos_termodinamica', 'Laboratorio de Fluidos y Termodinámica'),
        ('lab_sistemas_control', 'Laboratorio de Sistemas de Control'),
        ('lab_redes_computadoras', 'Laboratorio de Redes de Computadoras'),
        ('lab_automatizacion', 'Laboratorio de Automatización Industrial'),
    ]
    
    nombre = models.CharField(max_length=50, choices=LABORATORIOS)
    unidad_academica = models.ForeignKey(UnidadAcademica, on_delete=models.CASCADE)
    seccion_area = models.CharField(max_length=100, help_text="Sección o área del laboratorio")
    identificador_aula = models.CharField(max_length=50, help_text="Número o identificador del aula")
    
    class Meta:
        verbose_name = 'Laboratorio'
        verbose_name_plural = 'Laboratorios'
    
    def __str__(self):
        return f"{self.get_nombre_display()} - {self.unidad_academica}"

class TipoEquipo(models.Model):
    """Tipos de equipos disponibles"""
    TIPOS_EQUIPO = [
        ('microscopio_optico', 'Microscopio Óptico'),
        ('balanza_analitica', 'Balanza Analítica'),
        ('espectrofotometro', 'Espectrofotómetro'),
        ('centrifuga', 'Centrífuga'),
        ('autoclave', 'Autoclave'),
        ('incubadora', 'Incubadora'),
        ('ph_metro', 'pH Metro'),
        ('agitador_magnetico', 'Agitador Magnético'),
        ('campana_extractora', 'Campana Extractora'),
        ('mechero_bunsen', 'Mechero Bunsen'),
    ]
    
    nombre = models.CharField(max_length=50, unique=True)
    nombre_display = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Tipo de Equipo'
        verbose_name_plural = 'Tipos de Equipos'
    
    def __str__(self):
        return self.get_nombre_display()
    
    def get_nombre_display(self):
        if self.nombre_display:
            return self.nombre_display
        
        for key, display_name in self.TIPOS_EQUIPO:
            if key == self.nombre:
                return display_name
        
        return self.nombre.replace('_', ' ').title()

class EquipoExistente(models.Model):
    """Equipos existentes en el laboratorio"""
    ESTADOS = [
        ('excelente', 'Excelente'),
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('malo', 'Malo'),
        ('inoperativo', 'Inoperativo'),
    ]
    
    tipo_equipo = models.ForeignKey(TipoEquipo, on_delete=models.CASCADE)
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='bueno')
    numero_unidades = models.IntegerField(default=1, help_text="Número de unidades de este equipo")
    es_activo_fijo = models.BooleanField(default=False, help_text="¿Es un activo fijo según acta de entrega?")
    fotografia_frontal = models.ImageField(upload_to='equipos/fotos_frontales/', blank=True, null=True)
    fotografia_placa = models.ImageField(upload_to='equipos/fotos_placas/', blank=True, null=True)
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE, related_name='equipos_existentes')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    usuario_creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Equipo Existente'
        verbose_name_plural = 'Equipos Existentes'
    
    def __str__(self):
        return f"{self.tipo_equipo} - {self.marca} {self.modelo} ({self.numero_unidades} unidades)"

class EquipoRequerido(models.Model):
    """Equipos requeridos para una práctica específica"""
    practica = models.ForeignKey(Practica, on_delete=models.CASCADE, related_name='equipos_requeridos')
    tipo_equipo = models.ForeignKey(TipoEquipo, on_delete=models.CASCADE)
    numero_equipos_requeridos = models.IntegerField(help_text="Número de equipos necesarios")
    especificaciones = models.TextField(blank=True, help_text="Especificaciones técnicas requeridas")
    
    class Meta:
        verbose_name = 'Equipo Requerido'
        verbose_name_plural = 'Equipos Requeridos'
        unique_together = ['practica', 'tipo_equipo']
    
    def __str__(self):
        return f"{self.tipo_equipo} ({self.numero_equipos_requeridos} unidades) - {self.practica}"

class RegistroEquipos(models.Model):
    """Registro principal que conecta todo"""
    unidad_academica = models.ForeignKey(UnidadAcademica, on_delete=models.CASCADE)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    unidad_tematica = models.ForeignKey(UnidadTematica, on_delete=models.CASCADE)
    guia_laboratorio = models.ForeignKey(GuiaLaboratorio, on_delete=models.CASCADE)
    practica = models.ForeignKey(Practica, on_delete=models.CASCADE)
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    
    usuario_creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Registro de Equipos'
        verbose_name_plural = 'Registros de Equipos'
    
    def __str__(self):
        return f"{self.asignatura} - {self.practica} ({self.unidad_academica})"

# Modelos heredados para compatibilidad (mantener temporalmente)
class Materia(Asignatura):
    """Alias para compatibilidad con código existente"""
    class Meta:
        proxy = True
        verbose_name = 'Materia (Deprecado)'
        verbose_name_plural = 'Materias (Deprecadas)'

# Temporal fix - commenting out problematic proxy model
"""
class Ensayo(Practica):
    # Alias para compatibilidad con código existente
    cantidad_estudiantes = models.IntegerField(default=1, null=True, blank=True)
    laboratorio_old = models.ForeignKey('Laboratorio', on_delete=models.CASCADE, related_name='ensayos_old', null=True, blank=True)
    
    class Meta:
        proxy = True
        verbose_name = 'Ensayo (Deprecado)'
        verbose_name_plural = 'Ensayos (Deprecados)'
"""

class Equipo(models.Model):
    """Mantenido para compatibilidad temporal"""
    tipo_equipo = models.ForeignKey(TipoEquipo, on_delete=models.CASCADE)
    # Commented out to fix migration issue
    # ensayo = models.ForeignKey(Ensayo, on_delete=models.CASCADE, related_name='equipos', null=True, blank=True)
    equipos_seleccionados = models.ManyToManyField('EquipoIndividual', blank=True)
    cantidad_necesaria = models.IntegerField(default=1)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Equipo (Deprecado)'
        verbose_name_plural = 'Equipos (Deprecados)'

class EquipoIndividual(models.Model):
    """Mantenido para compatibilidad temporal"""
    ESTADOS = [
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('malo', 'Malo'),
    ]
    
    ESTADOS_OPERATIVOS = [
        ('operativo', 'Operativo'),
        ('mantenimiento', 'En Mantenimiento'),
        ('reparacion', 'En Reparación'),
        ('inoperativo', 'Inoperativo'),
    ]
    
    tipo_equipo = models.ForeignKey(TipoEquipo, on_delete=models.CASCADE, related_name='equipos_individuales')
    codigo = models.CharField(max_length=20, unique=True)
    estado_fisico = models.CharField(max_length=20, choices=ESTADOS, default='bueno')
    estado_operativo = models.CharField(max_length=20, choices=ESTADOS_OPERATIVOS, default='operativo')
    unidad_academica = models.ForeignKey(UnidadAcademica, on_delete=models.CASCADE, null=True, blank=True)
    ubicacion = models.CharField(max_length=100, blank=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Equipo Individual (Deprecado)'
        verbose_name_plural = 'Equipos Individuales (Deprecados)'

class RegistroIngreso(models.Model):
    """Mantenido para compatibilidad temporal"""
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE, null=True, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    datos_completos = models.JSONField()
    
    class Meta:
        verbose_name = 'Registro de Ingreso (Deprecado)'
        verbose_name_plural = 'Registros de Ingresos (Deprecados)'
