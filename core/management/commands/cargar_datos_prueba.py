from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import (
    UnidadAcademica, Carrera, Asignatura, UnidadTematica, 
    GuiaLaboratorio, Practica, Laboratorio
)


class Command(BaseCommand):
    help = 'Carga datos de prueba para la estructura académica completa'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando carga de datos de prueba...')
        
        try:
            with transaction.atomic():
                self.create_unidades_academicas()
                self.create_carreras()
                self.create_laboratorios()
                self.create_asignaturas()
                self.create_unidades_tematicas()
                self.create_guias_laboratorio()
                self.create_practicas()
                
            self.stdout.write(
                self.style.SUCCESS('✅ Datos de prueba cargados exitosamente!')
            )
            self.print_summary()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al cargar datos: {str(e)}')
            )

    def create_unidades_academicas(self):
        """Crear unidades académicas"""
        unidades = [
            ('UALP', 'UALP - La Paz'),
            ('UACB', 'UACB - Cochabamba'),
            ('UASC', 'UASC - Santa Cruz'),
            ('UATP', 'UATP - Trópico'),
            ('UCRB', 'UCRB - Riberalta'),
        ]
        
        for codigo, nombre in unidades:
            unidad, created = UnidadAcademica.objects.get_or_create(
                nombre=codigo,
                defaults={'descripcion': nombre}
            )
            if created:
                self.stdout.write(f'  ➕ Unidad Académica: {nombre}')

    def create_carreras(self):
        """Crear carreras por unidad académica"""
        carreras_data = {
            'UASC': [
                ('ING_SISTEMAS', 'Ingeniería de Sistemas'),
                ('ING_INDUSTRIAL', 'Ingeniería Industrial'),
                ('ING_COMERCIAL', 'Ingeniería Comercial'),
                ('ING_CIVIL', 'Ingeniería Civil'),
                ('ING_PETROLERA', 'Ingeniería Petrolera'),
                ('ING_QUIMICA', 'Ingeniería Química'),
                ('ING_MECATRONICA', 'Ingeniería Mecatrónica'),
                ('LIC_BIOTECNOLOGIA', 'Licenciatura en Biotecnología'),
            ],
            'UCRB': [
                ('ING_FORESTAL', 'Ingeniería Forestal'),
                ('ING_SISTEMAS', 'Ingeniería de Sistemas'),
                ('ING_COMERCIAL', 'Ingeniería Comercial'),
                ('LIC_TURISMO', 'Licenciatura en Turismo'),
            ],
            'UATP': [
                ('ING_ZOOTECNIA', 'Ingeniería Zootécnica'),
                ('ING_SISTEMAS', 'Ingeniería de Sistemas'),
                ('MED_VETERINARIA', 'Medicina Veterinaria y Zootecnia'),
            ],
            'UACB': [
                ('ING_SISTEMAS', 'Ingeniería de Sistemas'),
                ('ING_INDUSTRIAL', 'Ingeniería Industrial'),
                ('ING_COMERCIAL', 'Ingeniería Comercial'),
            ]
        }
        
        for unidad_codigo, carreras in carreras_data.items():
            unidad = UnidadAcademica.objects.get(nombre=unidad_codigo)
            for carrera_codigo, carrera_nombre in carreras:
                carrera, created = Carrera.objects.get_or_create(
                    unidad_academica=unidad,
                    nombre=carrera_codigo,
                    defaults={'descripcion': carrera_nombre}
                )
                if created:
                    self.stdout.write(f'  ➕ Carrera: {carrera_nombre} ({unidad_codigo})')

    def create_laboratorios(self):
        """Crear laboratorios"""
        laboratorios = [
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
        
        for codigo, nombre in laboratorios:
            laboratorio, created = Laboratorio.objects.get_or_create(
                nombre=codigo,
                defaults={
                    'descripcion': nombre,
                    'ubicacion': f'Edificio Principal - {nombre}',
                    'capacidad': 25,
                    'responsable': 'Por asignar'
                }
            )
            if created:
                self.stdout.write(f'  ➕ Laboratorio: {nombre}')

    def create_asignaturas(self):
        """Crear asignaturas por carrera y semestre"""
        asignaturas_comunes = {
            1: [
                'Cálculo I',
                'Álgebra Lineal', 
                'Física I',
                'Química General',
                'Introducción a la Ingeniería',
            ],
            2: [
                'Cálculo II',
                'Física II',
                'Química Orgánica',
                'Estadística',
                'Programación I',
            ],
            3: [
                'Cálculo III',
                'Física III',
                'Programación II',
                'Ecuaciones Diferenciales',
                'Métodos Numéricos',
            ]
        }
        
        asignaturas_especializadas = {
            'ING_SISTEMAS': {
                4: ['Base de Datos', 'Redes de Computadoras'],
                5: ['Ingeniería de Software I', 'Inteligencia Artificial'],
            },
            'ING_QUIMICA': {
                4: ['Termodinámica', 'Reactores Químicos'],
                5: ['Operaciones Unitarias I', 'Control de Procesos'],
            },
            'ING_MECATRONICA': {
                4: ['Electrónica Analógica', 'Automatización'],
                5: ['Robótica', 'Control Automático'],
            },
            'LIC_BIOTECNOLOGIA': {
                4: ['Microbiología', 'Bioquímica'],
                5: ['Genética Molecular', 'Bioingeniería'],
            }
        }
        
        # Crear asignaturas comunes para todas las carreras
        carreras = Carrera.objects.all()
        for carrera in carreras:
            # Asignaturas comunes (semestres 1-3)
            for semestre, materias in asignaturas_comunes.items():
                for nombre in materias:
                    asignatura, created = Asignatura.objects.get_or_create(
                        carrera=carrera,
                        semestre=semestre,
                        nombre=nombre,
                        defaults={
                            'carga_horaria_semanal': 6,
                            'carga_horaria_semestral': 96,
                        }
                    )
                    if created:
                        self.stdout.write(f'  ➕ Asignatura: {nombre} - {carrera.get_nombre_display()} (Sem {semestre})')
            
            # Asignaturas especializadas si existen para esta carrera
            if carrera.nombre in asignaturas_especializadas:
                for semestre, materias in asignaturas_especializadas[carrera.nombre].items():
                    for nombre in materias:
                        asignatura, created = Asignatura.objects.get_or_create(
                            carrera=carrera,
                            semestre=semestre,
                            nombre=nombre,
                            defaults={
                                'carga_horaria_semanal': 6,
                                'carga_horaria_semestral': 96,
                            }
                        )
                        if created:
                            self.stdout.write(f'  ➕ Asignatura: {nombre} - {carrera.get_nombre_display()} (Sem {semestre})')

    def create_unidades_tematicas(self):
        """Crear unidades temáticas para las asignaturas"""
        unidades_por_tipo = {
            'Física': [
                'Mecánica Clásica',
                'Termodinámica', 
                'Electromagnetismo',
                'Óptica',
            ],
            'Química': [
                'Estructura Atómica',
                'Enlaces Químicos',
                'Reacciones Químicas',
                'Equilibrio Químico',
            ],
            'Programación': [
                'Algoritmos Básicos',
                'Estructuras de Control',
                'Funciones y Procedimientos',
                'Estructuras de Datos',
            ],
            'Cálculo': [
                'Límites y Continuidad',
                'Derivadas',
                'Integrales',
                'Series',
            ]
        }
        
        asignaturas = Asignatura.objects.all()
        for asignatura in asignaturas:
            # Determinar tipo de unidades según el nombre de la asignatura
            tipo_unidades = None
            if 'Física' in asignatura.nombre:
                tipo_unidades = 'Física'
            elif 'Química' in asignatura.nombre:
                tipo_unidades = 'Química'
            elif 'Programación' in asignatura.nombre:
                tipo_unidades = 'Programación'
            elif 'Cálculo' in asignatura.nombre:
                tipo_unidades = 'Cálculo'
            
            if tipo_unidades and tipo_unidades in unidades_por_tipo:
                for i, nombre_unidad in enumerate(unidades_por_tipo[tipo_unidades], 1):
                    unidad, created = UnidadTematica.objects.get_or_create(
                        asignatura=asignatura,
                        numero=i,
                        defaults={
                            'nombre': nombre_unidad,
                        }
                    )
                    if created:
                        self.stdout.write(f'  ➕ Unidad Temática: {nombre_unidad} ({asignatura.nombre})')

    def create_guias_laboratorio(self):
        """Crear guías de laboratorio para las unidades temáticas"""
        unidades = UnidadTematica.objects.all()
        
        for unidad in unidades:
            # Crear 1-2 guías por unidad temática
            num_guias = 2 if 'Laboratorio' in unidad.asignatura.nombre or 'Práctica' in unidad.asignatura.nombre else 1
            
            for i in range(1, num_guias + 1):
                guia, created = GuiaLaboratorio.objects.get_or_create(
                    unidad_tematica=unidad,
                    numero=i,
                    defaults={
                        'nombre': f'Guía de Laboratorio {i} - {unidad.nombre}',
                        'descripcion': f'Guía práctica para {unidad.nombre}',
                    }
                )
                if created:
                    self.stdout.write(f'  ➕ Guía Lab: {guia.nombre}')

    def create_practicas(self):
        """Crear prácticas para las guías de laboratorio"""
        guias = GuiaLaboratorio.objects.all()
        
        for guia in guias:
            # Crear 1-3 prácticas por guía
            num_practicas = 2
            
            for i in range(1, num_practicas + 1):
                practica, created = Practica.objects.get_or_create(
                    guia_laboratorio=guia,
                    numero=i,
                    defaults={
                        'nombre': f'Práctica {i}: {guia.nombre}',
                        'descripcion': f'Práctica {i} correspondiente a {guia.nombre}',
                    }
                )
                if created:
                    self.stdout.write(f'  ➕ Práctica: {practica.nombre}')

    def print_summary(self):
        """Imprimir resumen de datos creados"""
        self.stdout.write('\n📊 RESUMEN DE DATOS CREADOS:')
        self.stdout.write(f'  🏛️  Unidades Académicas: {UnidadAcademica.objects.count()}')
        self.stdout.write(f'  🎓 Carreras: {Carrera.objects.count()}')
        self.stdout.write(f'  🔬 Laboratorios: {Laboratorio.objects.count()}')
        self.stdout.write(f'  📚 Asignaturas: {Asignatura.objects.count()}')
        self.stdout.write(f'  📖 Unidades Temáticas: {UnidadTematica.objects.count()}')
        self.stdout.write(f'  📋 Guías de Laboratorio: {GuiaLaboratorio.objects.count()}')
        self.stdout.write(f'  🧪 Prácticas: {Practica.objects.count()}')
        self.stdout.write('\n✨ ¡Listo para usar el sistema!')
