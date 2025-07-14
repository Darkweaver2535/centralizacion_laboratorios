from django.db import models
from django.contrib.auth.models import User

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
        ('ingenieria_sistemas', 'Ingeniería de Sistemas'),
        ('ingenieria_civil', 'Ingeniería Civil'),
        ('ingenieria_industrial', 'Ingeniería Industrial'),
        ('ingenieria_electronica', 'Ingeniería Electrónica'),
        ('ingenieria_mecanica', 'Ingeniería Mecánica'),
        ('ingenieria_quimica', 'Ingeniería Química'),
        ('ingenieria_petrolera', 'Ingeniería Petrolera'),
        ('ingenieria_ambiental', 'Ingeniería Ambiental'),
    ]
    
    nombre = models.CharField(max_length=50, choices=CARRERAS, unique=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Carrera'
        verbose_name_plural = 'Carreras'
    
    def __str__(self):
        return self.get_nombre_display()

class Materia(models.Model):
    # Materias comunes por semestre
    MATERIAS_POR_SEMESTRE = {
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Generar choices dinámicamente basado en todas las materias
        all_materias = []
        for materias_list in self.MATERIAS_POR_SEMESTRE.values():
            all_materias.extend(materias_list)
        self._meta.get_field('nombre').choices = list(set(all_materias))
    
    class Meta:
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
        unique_together = ['nombre', 'carrera', 'semestre']
    
    def __str__(self):
        return f"{self.get_nombre_display()} - {self.carrera} - {self.semestre}° Semestre"
    
    @classmethod
    def get_materias_por_semestre(cls, semestre):
        """Obtener materias disponibles para un semestre específico"""
        return cls.MATERIAS_POR_SEMESTRE.get(semestre, [])

class Laboratorio(models.Model):
    # Laboratorios predefinidos
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
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    usuario_creador = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Laboratorio'
        verbose_name_plural = 'Laboratorios'
    
    def __str__(self):
        return f"{self.get_nombre_display()} - {self.unidad_academica}"

class Ensayo(models.Model):
    # Ensayos predefinidos
    ENSAYOS = [
        ('ensayo_traccion', 'Ensayo de Tracción'),
        ('ensayo_compresion', 'Ensayo de Compresión'),
        ('ensayo_dureza', 'Ensayo de Dureza'),
        ('ensayo_impacto', 'Ensayo de Impacto'),
        ('ensayo_ph', 'Ensayo de pH'),
        ('ensayo_conductividad', 'Ensayo de Conductividad Eléctrica'),
        ('ensayo_densidad', 'Ensayo de Densidad'),
        ('ensayo_viscosidad', 'Ensayo de Viscosidad'),
        ('ensayo_microscopia', 'Ensayo de Microscopía'),
        ('ensayo_espectroscopia', 'Ensayo de Espectroscopía'),
    ]
    
    nombre = models.CharField(max_length=50, choices=ENSAYOS)
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE, related_name='ensayos')
    cantidad_estudiantes = models.IntegerField(default=1, help_text="Número de estudiantes que participarán en el ensayo")
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Ensayo'
        verbose_name_plural = 'Ensayos'
    
    def __str__(self):
        return f"{self.get_nombre_display()} - {self.laboratorio.nombre}"

class TipoEquipo(models.Model):
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
    
    nombre = models.CharField(max_length=50, choices=TIPOS_EQUIPO, unique=True)
    descripcion = models.TextField(blank=True)
    capacidad_estudiantes = models.IntegerField(default=1, help_text="Número de estudiantes que pueden usar simultáneamente este equipo")
    
    class Meta:
        verbose_name = 'Tipo de Equipo'
        verbose_name_plural = 'Tipos de Equipos'
    
    def __str__(self):
        return self.get_nombre_display()

class EquipoIndividual(models.Model):
    """Modelo para equipos individuales con códigos únicos"""
    ESTADOS = [
        ('operativo', 'Operativo'),
        ('mantenimiento', 'En Mantenimiento'),
        ('reparacion', 'En Reparación'),
        ('inoperativo', 'Inoperativo'),
    ]
    
    tipo_equipo = models.ForeignKey(TipoEquipo, on_delete=models.CASCADE, related_name='equipos_individuales')
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único del equipo")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='operativo')
    ubicacion = models.CharField(max_length=100, blank=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Equipo Individual'
        verbose_name_plural = 'Equipos Individuales'
        ordering = ['tipo_equipo', 'codigo']
    
    def __str__(self):
        return f"{self.tipo_equipo.get_nombre_display()} - {self.codigo}"

class Equipo(models.Model):
    """Modelo para la asignación de equipos a ensayos"""
    tipo_equipo = models.ForeignKey(TipoEquipo, on_delete=models.CASCADE)
    ensayo = models.ForeignKey(Ensayo, on_delete=models.CASCADE, related_name='equipos')
    equipos_seleccionados = models.ManyToManyField(EquipoIndividual, blank=True)
    cantidad_necesaria = models.IntegerField(default=1, help_text="Cantidad de equipos necesarios para el ensayo")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
    
    def __str__(self):
        return f"{self.tipo_equipo} - {self.ensayo.nombre}"
    
    def get_equipos_disponibles(self):
        """Obtener equipos disponibles del tipo seleccionado"""
        return EquipoIndividual.objects.filter(
            tipo_equipo=self.tipo_equipo,
            estado='operativo'
        )
    
    def get_recomendacion_uso(self):
        """Obtener recomendación de uso basada en estudiantes y capacidad"""
        estudiantes = self.ensayo.cantidad_estudiantes
        capacidad_por_equipo = self.tipo_equipo.capacidad_estudiantes
        equipos_disponibles = self.get_equipos_disponibles().count()
        
        equipos_necesarios = -(-estudiantes // capacidad_por_equipo)  # Ceil division
        
        if equipos_necesarios <= equipos_disponibles:
            if capacidad_por_equipo == 1:
                return {
                    'estado': 'suficiente',
                    'mensaje': f'Cada estudiante usará un equipo individual. Se necesitan {equipos_necesarios} equipos.',
                    'equipos_necesarios': equipos_necesarios,
                    'equipos_disponibles': equipos_disponibles
                }
            else:
                return {
                    'estado': 'suficiente',
                    'mensaje': f'Se pueden agrupar {capacidad_por_equipo} estudiantes por equipo. Se necesitan {equipos_necesarios} equipos.',
                    'equipos_necesarios': equipos_necesarios,
                    'equipos_disponibles': equipos_disponibles
                }
        else:
            faltante = equipos_necesarios - equipos_disponibles
            return {
                'estado': 'insuficiente',
                'mensaje': f'Se necesitan {equipos_necesarios} equipos pero solo hay {equipos_disponibles} disponibles. Se recomienda comprar {faltante} equipos adicionales.',
                'equipos_necesarios': equipos_necesarios,
                'equipos_disponibles': equipos_disponibles,
                'equipos_faltantes': faltante
            }

class RegistroIngreso(models.Model):
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    datos_completos = models.JSONField()
    
    class Meta:
        verbose_name = 'Registro de Ingreso'
        verbose_name_plural = 'Registros de Ingresos'
    
    def __str__(self):
        return f"Registro {self.laboratorio.nombre} - {self.fecha_ingreso}"
