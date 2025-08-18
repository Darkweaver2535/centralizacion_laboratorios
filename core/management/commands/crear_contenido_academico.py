from django.core.management.base import BaseCommand
from core.models import Asignatura, UnidadTematica, GuiaLaboratorio, Practica

class Command(BaseCommand):
    help = 'Crear unidades temáticas, guías y prácticas para asignaturas existentes'
    
    def handle(self, *args, **options):
        self.stdout.write('🚀 Creando contenido académico...\n')
        
        # Definir contenido por asignatura
        contenido_asignaturas = {
            'fisica_i': {
                'unidades': [
                    {
                        'nombre': 'Cinemática y Movimiento',
                        'guias': [
                            {
                                'nombre': 'Movimiento Rectilíneo',
                                'practicas': [
                                    'ESTUDIO EXPERIMENTAL DEL MOVIMIENTO RECTILÍNEO UNIFORME (MRU)',
                                    'ANÁLISIS DEL MOVIMIENTO UNIFORMEMENTE ACELERADO (MRUA)',
                                    'MEDICIÓN DE ACELERACIÓN EN PLANO INCLINADO'
                                ]
                            },
                            {
                                'nombre': 'Movimiento en Dos Dimensiones',
                                'practicas': [
                                    'ANÁLISIS DE TRAYECTORIA PARABÓLICA',
                                    'ESTUDIO DE MOVIMIENTO CIRCULAR UNIFORME',
                                    'DETERMINACIÓN DE VELOCIDAD ANGULAR'
                                ]
                            }
                        ]
                    },
                    {
                        'nombre': 'Dinámica y Fuerzas',
                        'guias': [
                            {
                                'nombre': 'Leyes de Newton',
                                'practicas': [
                                    'VERIFICACIÓN DE LA SEGUNDA LEY DE NEWTON',
                                    'ANÁLISIS DE FUERZAS EN EQUILIBRIO',
                                    'ESTUDIO DE FRICCIÓN ESTÁTICA Y CINÉTICA'
                                ]
                            }
                        ]
                    },
                    {
                        'nombre': 'Trabajo y Energía',
                        'guias': [
                            {
                                'nombre': 'Conservación de Energía',
                                'practicas': [
                                    'VERIFICACIÓN DEL PRINCIPIO DE CONSERVACIÓN DE ENERGÍA',
                                    'ANÁLISIS DE ENERGÍA CINÉTICA Y POTENCIAL',
                                    'ESTUDIO DE COLISIONES ELÁSTICAS E INELÁSTICAS'
                                ]
                            }
                        ]
                    }
                ]
            },
            'matematica_i': {
                'unidades': [
                    {
                        'nombre': 'Límites y Continuidad',
                        'guias': [
                            {
                                'nombre': 'Cálculo de Límites',
                                'practicas': [
                                    'DETERMINACIÓN GRÁFICA DE LÍMITES',
                                    'APLICACIÓN DE REGLAS DE L\'HÔPITAL',
                                    'ANÁLISIS DE CONTINUIDAD DE FUNCIONES'
                                ]
                            }
                        ]
                    },
                    {
                        'nombre': 'Derivadas',
                        'guias': [
                            {
                                'nombre': 'Cálculo Diferencial',
                                'practicas': [
                                    'APLICACIÓN DE REGLAS DE DERIVACIÓN',
                                    'ANÁLISIS DE RAZONES DE CAMBIO',
                                    'OPTIMIZACIÓN DE FUNCIONES'
                                ]
                            }
                        ]
                    },
                    {
                        'nombre': 'Integrales',
                        'guias': [
                            {
                                'nombre': 'Cálculo Integral',
                                'practicas': [
                                    'TÉCNICAS DE INTEGRACIÓN BÁSICAS',
                                    'APLICACIONES DEL TEOREMA FUNDAMENTAL',
                                    'CÁLCULO DE ÁREAS BAJO CURVAS'
                                ]
                            }
                        ]
                    }
                ]
            },
            'quimica_general': {
                'unidades': [
                    {
                        'nombre': 'Estructura Atómica',
                        'guias': [
                            {
                                'nombre': 'Propiedades Atómicas',
                                'practicas': [
                                    'IDENTIFICACIÓN DE ELEMENTOS POR ESPECTROSCOPÍA',
                                    'DETERMINACIÓN DE CONFIGURACIÓN ELECTRÓNICA',
                                    'ANÁLISIS DE PROPIEDADES PERIÓDICAS'
                                ]
                            }
                        ]
                    },
                    {
                        'nombre': 'Enlaces Químicos',
                        'guias': [
                            {
                                'nombre': 'Tipos de Enlaces',
                                'practicas': [
                                    'FORMACIÓN DE ENLACES IÓNICOS Y COVALENTES',
                                    'PREDICCIÓN DE GEOMETRÍA MOLECULAR',
                                    'ANÁLISIS DE POLARIDAD MOLECULAR'
                                ]
                            }
                        ]
                    },
                    {
                        'nombre': 'Reacciones Químicas',
                        'guias': [
                            {
                                'nombre': 'Estequiometría',
                                'practicas': [
                                    'BALANCEO DE ECUACIONES QUÍMICAS',
                                    'CÁLCULOS ESTEQUIOMÉTRICOS EN LABORATORIO',
                                    'DETERMINACIÓN DE REACTIVO LIMITANTE'
                                ]
                            }
                        ]
                    }
                ]
            },
            'programacion_i': {
                'unidades': [
                    {
                        'nombre': 'Fundamentos de Programación',
                        'guias': [
                            {
                                'nombre': 'Algoritmos Básicos',
                                'practicas': [
                                    'IMPLEMENTACIÓN DE ESTRUCTURAS SECUENCIALES',
                                    'DESARROLLO DE ALGORITMOS CONDICIONALES',
                                    'CREACIÓN DE BUCLES Y ITERACIONES'
                                ]
                            }
                        ]
                    },
                    {
                        'nombre': 'Estructuras de Datos',
                        'guias': [
                            {
                                'nombre': 'Arrays y Listas',
                                'practicas': [
                                    'MANIPULACIÓN DE ARREGLOS UNIDIMENSIONALES',
                                    'IMPLEMENTACIÓN DE MATRICES',
                                    'ALGORITMOS DE BÚSQUEDA Y ORDENAMIENTO'
                                ]
                            }
                        ]
                    },
                    {
                        'nombre': 'Funciones y Procedimientos',
                        'guias': [
                            {
                                'nombre': 'Modularización',
                                'practicas': [
                                    'DISEÑO DE FUNCIONES REUTILIZABLES',
                                    'IMPLEMENTACIÓN DE RECURSIVIDAD',
                                    'DESARROLLO DE BIBLIOTECAS DE FUNCIONES'
                                ]
                            }
                        ]
                    }
                ]
            },
            'circuitos_electricos': {
                'unidades': [
                    {
                        'nombre': 'Leyes Fundamentales',
                        'guias': [
                            {
                                'nombre': 'Ley de Ohm y Kirchhoff',
                                'practicas': [
                                    'VERIFICACIÓN EXPERIMENTAL DE LA LEY DE OHM',
                                    'APLICACIÓN DE LEYES DE KIRCHHOFF',
                                    'ANÁLISIS DE CIRCUITOS RESISTIVOS'
                                ]
                            }
                        ]
                    },
                    {
                        'nombre': 'Circuitos AC y DC',
                        'guias': [
                            {
                                'nombre': 'Análisis de Circuitos',
                                'practicas': [
                                    'MEDICIÓN DE VOLTAJE Y CORRIENTE DC',
                                    'ANÁLISIS DE CIRCUITOS AC MONOFÁSICOS',
                                    'ESTUDIO DE IMPEDANCIA Y REACTANCIA'
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        
        # Obtener todas las asignaturas existentes
        asignaturas = Asignatura.objects.all()
        
        contador_unidades = 0
        contador_guias = 0
        contador_practicas = 0
        
        for asignatura in asignaturas:
            # Buscar contenido para esta asignatura
            contenido = contenido_asignaturas.get(asignatura.nombre)
            
            if contenido:
                self.stdout.write(f'📚 Procesando: {asignatura}')
                
                # Crear unidades temáticas
                for i, unidad_data in enumerate(contenido['unidades'], 1):
                    unidad, created = UnidadTematica.objects.get_or_create(
                        asignatura=asignatura,
                        numero=i,
                        defaults={
                            'nombre': unidad_data['nombre']
                        }
                    )
                    
                    if created:
                        contador_unidades += 1
                        self.stdout.write(f'  ✅ Unidad creada: {unidad.nombre}')
                    
                    # Crear guías de laboratorio
                    for j, guia_data in enumerate(unidad_data['guias'], 1):
                        guia, created = GuiaLaboratorio.objects.get_or_create(
                            unidad_tematica=unidad,
                            numero=j,
                            defaults={
                                'nombre': guia_data['nombre']
                            }
                        )
                        
                        if created:
                            contador_guias += 1
                            self.stdout.write(f'    ✅ Guía creada: {guia.nombre}')
                        
                        # Crear prácticas
                        for k, practica_nombre in enumerate(guia_data['practicas'], 1):
                            practica, created = Practica.objects.get_or_create(
                                guia_laboratorio=guia,
                                numero=k,
                                defaults={
                                    'nombre': practica_nombre
                                }
                            )
                            
                            if created:
                                contador_practicas += 1
                                self.stdout.write(f'      ✅ Práctica creada: {practica.nombre}')
        
        # Crear contenido genérico para asignaturas sin contenido específico
        asignaturas_sin_contenido = asignaturas.exclude(
            nombre__in=contenido_asignaturas.keys()
        )
        
        for asignatura in asignaturas_sin_contenido:
            self.stdout.write(f'📝 Contenido genérico para: {asignatura}')
            
            # Crear 3 unidades temáticas genéricas
            for i in range(1, 4):
                unidad, created = UnidadTematica.objects.get_or_create(
                    asignatura=asignatura,
                    numero=i,
                    defaults={
                        'nombre': f'Unidad {i}: Fundamentos de {asignatura.get_nombre_display()}'
                    }
                )
                
                if created:
                    contador_unidades += 1
                
                # Crear 2 guías por unidad
                for j in range(1, 3):
                    guia, created = GuiaLaboratorio.objects.get_or_create(
                        unidad_tematica=unidad,
                        numero=j,
                        defaults={
                            'nombre': f'Guía {j}: Laboratorio de {unidad.nombre}'
                        }
                    )
                    
                    if created:
                        contador_guias += 1
                    
                    # Crear 2 prácticas por guía
                    for k in range(1, 3):
                        practica, created = Practica.objects.get_or_create(
                            guia_laboratorio=guia,
                            numero=k,
                            defaults={
                                'nombre': f'PRÁCTICA {k}: ESTUDIO EXPERIMENTAL DE {unidad.nombre.upper()}'
                            }
                        )
                        
                        if created:
                            contador_practicas += 1
        
        # Mostrar resumen
        self.stdout.write(self.style.SUCCESS(f'\n🎉 ¡Contenido académico creado exitosamente!'))
        self.stdout.write(f'📊 Resumen:')
        self.stdout.write(f'   • Unidades Temáticas: {contador_unidades} nuevas')
        self.stdout.write(f'   • Guías de Laboratorio: {contador_guias} nuevas')
        self.stdout.write(f'   • Prácticas: {contador_practicas} nuevas')
        
        # Mostrar totales
        total_unidades = UnidadTematica.objects.count()
        total_guias = GuiaLaboratorio.objects.count()
        total_practicas = Practica.objects.count()
        
        self.stdout.write(f'\n📈 Totales en base de datos:')
        self.stdout.write(f'   • Total Unidades Temáticas: {total_unidades}')
        self.stdout.write(f'   • Total Guías de Laboratorio: {total_guias}')
        self.stdout.write(f'   • Total Prácticas: {total_practicas}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ ¡Ahora ya puedes seleccionar unidades temáticas, guías y prácticas en el formulario!'))
