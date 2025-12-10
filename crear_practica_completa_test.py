"""
Script para crear una práctica completa con TODOS los campos del formulario
y verificar que TODO se refleje en el PDF
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import (
    Asignatura, ContenidoAnalitico, UnidadDidactica,
    PracticaLaboratorio, Bibliografia, Titulo,
    Competencias, ObjetivoPractica, FundamentoTeorico,
    MaterialesHerramientasEquipos, Procedimientos,
    CalculosResultados, Cuestionario
)

print("=" * 80)
print("CREANDO PRÁCTICA COMPLETA DE PRUEBA CON TODOS LOS CAMPOS")
print("=" * 80)

# Obtener asignatura existente
asignatura = Asignatura.objects.first()
print(f"\n✓ Asignatura: {asignatura.nombre}")

# Crear contenido analítico
contenido, created = ContenidoAnalitico.objects.get_or_create(
    nombre="Análisis Químico Cuantitativo",
    asignatura=asignatura,
    defaults={
        'descripcion': 'Contenido analítico sobre métodos cuantitativos de análisis químico',
        'orden': 100
    }
)
print(f"✓ Contenido Analítico: {contenido.nombre} ({'creado' if created else 'existente'})")

# Crear unidad didáctica
unidad, created = UnidadDidactica.objects.get_or_create(
    nombre="Métodos Volumétricos",
    contenido_analitico=contenido,
    defaults={'orden': 1}
)
print(f"✓ Unidad Didáctica: {unidad.nombre}")

# 1. CREAR PRÁCTICA
practica, created = PracticaLaboratorio.objects.get_or_create(
    nombre="Determinación de Nitrógeno por Método Kjeldahl",
    contenido_analitico=contenido,
    defaults={
        'duracion_horas': 3.0,
        'tipo_practica': 'grupal',
        'numero_estudiantes': 4,
        'orden': 1
    }
)
print(f"\n📝 Práctica: {practica.nombre} (ID: {practica.id})")

# 2. BIBLIOGRAFÍA
Bibliografia.objects.get_or_create(
    contenido_analitico=contenido,
    titulo="Química Analítica Cuantitativa - Skoog & West",
    defaults={'autor': 'Skoog, West, Holler', 'anio_publicacion': '2015', 'orden': 1}
)
Bibliografia.objects.get_or_create(
    contenido_analitico=contenido,
    titulo="Manual de Análisis Químico - Harris",
    defaults={'autor': 'Daniel C. Harris', 'anio_publicacion': '2016', 'orden': 2}
)
print("✓ Bibliografía: 2 referencias")

# 3. TÍTULO
Titulo.objects.get_or_create(
    contenido_analitico=contenido,
    texto="Determinación de Nitrógeno Total en Muestras Orgánicas",
    defaults={'orden': 1}
)
print("✓ Título: Determinación de Nitrógeno Total")

# 4. COMPETENCIAS (4 tipos)
competencias_data = [
    ('conceptual', 'Conoce los fundamentos teóricos del método Kjeldahl y su aplicación'),
    ('procedimental', 'Maneja correctamente los equipos de destilación y titulación'),
    ('actitudinal', 'Trabaja de forma ordenada, responsable y en equipo'),
    ('mixta', 'Interpreta resultados y los relaciona con la teoría química')
]
for tipo, desc in competencias_data:
    Competencias.objects.get_or_create(
        contenido_analitico=contenido,
        descripcion=desc,
        defaults={'tipo_competencia': tipo, 'orden': 1}
    )
print(f"✓ Competencias: {len(competencias_data)} tipos")

# 5. OBJETIVOS (Criterios de Desempeño)
criterios_data = [
    'Aplica correctamente las normas de seguridad en el laboratorio químico',
    'Prepara reactivos siguiendo el protocolo establecido',
    'Realiza mediciones precisas con equipos de vidrio volumétrico',
    'Registra datos experimentales de forma ordenada y completa'
]
for i, desc in enumerate(criterios_data, 1):
    ObjetivoPractica.objects.get_or_create(
        contenido_analitico=contenido,
        descripcion=desc,
        defaults={'tipo_objetivo': 'desempeno', 'orden': i}
    )
print(f"✓ Criterios de Desempeño: {len(criterios_data)}")

# 6. OBJETIVOS (General, Específico, Aprendizaje)
objetivos_data = [
    ('general', 'Determinar el contenido de nitrógeno total en muestras orgánicas mediante el método Kjeldahl'),
    ('especifico', 'Calcular el porcentaje de proteína en la muestra analizada'),
    ('aprendizaje', 'Desarrollar habilidades en técnicas de digestión ácida y destilación')
]
for tipo, desc in objetivos_data:
    ObjetivoPractica.objects.get_or_create(
        contenido_analitico=contenido,
        descripcion=desc,
        defaults={'tipo_objetivo': tipo, 'orden': 1}
    )
print(f"✓ Objetivos de la Práctica: {len(objetivos_data)}")

# 7. FUNDAMENTO TEÓRICO
FundamentoTeorico.objects.get_or_create(
    contenido_analitico=contenido,
    titulo="Método Kjeldahl",
    defaults={
        'contenido': '''El método Kjeldahl es una técnica analítica clásica para la determinación de 
nitrógeno en compuestos orgánicos. Consta de tres etapas principales:

1. Digestión: La muestra se trata con H2SO4 concentrado a alta temperatura
2. Destilación: El amonio formado se destila en medio alcalino
3. Titulación: El destilado se titula con ácido valorado

El contenido de proteína se estima multiplicando el nitrógeno por el factor 6.25.''',
        'orden': 1
    }
)
print("✓ Fundamento Teórico: Método Kjeldahl")

# 8. MATERIALES, EQUIPOS, HERRAMIENTAS, REACTIVOS
materiales_data = [
    ('equipo', 'Balanza analítica (0.0001 g)', '1'),
    ('equipo', 'Sistema de digestión Kjeldahl', '1'),
    ('equipo', 'Aparato de destilación', '1'),
    ('material', 'Matraz Kjeldahl 300 mL', '3'),
    ('material', 'Bureta 50 mL', '1'),
    ('material', 'Pipeta volumétrica 25 mL', '2'),
    ('herramienta', 'Pinzas para tubos de ensayo', '2'),
    ('herramienta', 'Espátula de acero inoxidable', '1'),
    ('reactivo', 'Ácido sulfúrico concentrado (98%)', '50 mL'),
    ('reactivo', 'Hidróxido de sodio (40%)', '100 mL'),
    ('reactivo', 'Ácido clorhídrico 0.1 N', '50 mL'),
    ('reactivo', 'Indicador mixto (verde de bromocresol)', '5 mL')
]
for tipo, nombre, cant in materiales_data:
    MaterialesHerramientasEquipos.objects.get_or_create(
        contenido_analitico=contenido,
        nombre=nombre,
        defaults={'tipo_elemento': tipo, 'cantidad': cant, 'orden': 1}
    )
print(f"✓ Materiales/Equipos/Herramientas/Reactivos: {len(materiales_data)}")

# 9. PROCEDIMIENTOS (Pasos detallados)
procedimientos_data = [
    ("Preparación de la muestra", "Pesar exactamente 1.0000 g de muestra seca y colocar en matraz Kjeldahl. Registrar el peso en la hoja de datos."),
    ("Digestión", "Agregar 10 mL de H2SO4 concentrado y calentar gradualmente hasta ebullición. Mantener hasta que la solución se torne verde claro (aprox. 2 horas)."),
    ("Destilación", "Enfriar, agregar 50 mL de NaOH 40% y destilar recogiendo 100 mL de destilado en 25 mL de HCl 0.1 N."),
    ("Titulación", "Titular el exceso de ácido con NaOH 0.1 N usando indicador mixto hasta viraje de rosa a verde."),
    ("Cálculo", "Calcular el porcentaje de nitrógeno y proteína usando las fórmulas proporcionadas.")
]
for i, (titulo, desc) in enumerate(procedimientos_data, 1):
    Procedimientos.objects.get_or_create(
        contenido_analitico=contenido,
        numero_paso=i,
        defaults={'titulo_paso': titulo, 'descripcion': desc, 'orden': i}
    )
print(f"✓ Procedimientos: {len(procedimientos_data)} pasos")

# 10. CÁLCULOS Y RESULTADOS
CalculosResultados.objects.get_or_create(
    contenido_analitico=contenido,
    titulo="Porcentaje de Nitrógeno",
    defaults={
        'formula': '%N = [(V_blanco - V_muestra) × N × 0.014 × 100] / W',
        'procedimiento_calculo': '''Donde:
- V_blanco = volumen de NaOH gastado en el blanco
- V_muestra = volumen de NaOH gastado en la muestra
- N = normalidad del NaOH
- W = peso de la muestra en gramos
- 0.014 = equivalente del nitrógeno''',
        'orden': 1
    }
)
CalculosResultados.objects.get_or_create(
    contenido_analitico=contenido,
    titulo="Porcentaje de Proteína",
    defaults={
        'formula': '%Proteína = %N × 6.25',
        'procedimiento_calculo': 'El factor 6.25 es el estándar para la mayoría de alimentos (16% de N en proteínas).',
        'orden': 2
    }
)
print("✓ Cálculos y Resultados: 2 fórmulas")

# 11. CUESTIONARIO
cuestionario_data = [
    '¿Por qué se usa ácido sulfúrico concentrado en la digestión?',
    '¿Qué función cumple el catalizador en la digestión Kjeldahl?',
    'Explique el fundamento químico de la destilación en medio alcalino',
    '¿Por qué se multiplica el %N por 6.25 para obtener %Proteína?',
    'Mencione 3 fuentes de error en esta determinación'
]
for i, pregunta in enumerate(cuestionario_data, 1):
    Cuestionario.objects.get_or_create(
        contenido_analitico=contenido,
        numero_pregunta=i,
        defaults={'pregunta': pregunta, 'orden': i}
    )
print(f"✓ Cuestionario: {len(cuestionario_data)} preguntas")

print("\n" + "=" * 80)
print(f"✅ PRÁCTICA COMPLETA CREADA - ID: {practica.id}")
print("=" * 80)
print("\nResumen de datos:")
print(f"  📚 Bibliografía: 2")
print(f"  📝 Título: 1")
print(f"  🏆 Competencias: 4")
print(f"  📋 Criterios de Desempeño: 4")
print(f"  🎯 Objetivos: 3")
print(f"  📖 Fundamentos: 1")
print(f"  🔧 Materiales/Equipos: {len(materiales_data)}")
print(f"  📋 Procedimientos: 5 pasos")
print(f"  🧮 Cálculos: 2 fórmulas")
print(f"  ❓ Cuestionario: 5 preguntas")
print(f"\n🎯 Para generar PDF, usar práctica ID: {practica.id}")
