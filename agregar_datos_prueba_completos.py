"""
Script para crear datos de prueba completos con separación correcta de objetivos
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import (
    PracticaLaboratorio, ObjetivoPractica, Competencias,
    FundamentoTeorico, Procedimientos
)

practica = PracticaLaboratorio.objects.get(id=38)
contenido = practica.contenido_analitico

print("=" * 70)
print("AGREGANDO DATOS DE PRUEBA COMPLETOS")
print("=" * 70)
print()

# 1. Agregar más Criterios de Desempeño (tipo='desempeno')
print("📋 Agregando Criterios de Desempeño...")
criterios_nuevos = [
    "Aplica correctamente los procedimientos de seguridad en el laboratorio",
    "Identifica y utiliza adecuadamente los equipos de medición",
    "Registra datos experimentales de forma ordenada y precisa"
]

for i, desc in enumerate(criterios_nuevos, start=2):
    ObjetivoPractica.objects.get_or_create(
        contenido_analitico=contenido,
        descripcion=desc,
        defaults={'tipo_objetivo': 'desempeno', 'orden': i}
    )
    print(f"   ✓ {desc}")

# 2. Agregar Objetivos de la Práctica (otros tipos)
print("\n🎯 Agregando Objetivos de la Práctica...")
objetivos_nuevos = [
    ("general", "Comprender los principios fundamentales de la química analítica"),
    ("especifico", "Determinar la concentración de nitrógeno en muestras orgánicas"),
    ("aprendizaje", "Desarrollar habilidades en técnicas de titulación volumétrica")
]

for tipo, desc in objetivos_nuevos:
    ObjetivoPractica.objects.get_or_create(
        contenido_analitico=contenido,
        descripcion=desc,
        defaults={'tipo_objetivo': tipo, 'orden': 1}
    )
    print(f"   ✓ [{tipo.upper()}] {desc}")

# 3. Agregar Competencias
print("\n🏆 Agregando Competencias...")
competencias = [
    ("conceptual", "Conocimientos básicos de química analítica"),
    ("procedimental", "Manejo de equipos de laboratorio"),
    ("actitudinal", "Trabajo en equipo y responsabilidad")
]

for tipo, desc in competencias:
    Competencias.objects.get_or_create(
        contenido_analitico=contenido,
        descripcion=desc,
        defaults={'tipo_competencia': tipo, 'orden': 1}
    )
    print(f"   ✓ [{tipo.upper()}] {desc}")

# 4. Agregar Fundamento Teórico
print("\n📚 Agregando Fundamento Teórico...")
FundamentoTeorico.objects.get_or_create(
    contenido_analitico=contenido,
    titulo="Método Kjeldahl",
    defaults={
        'contenido': """El método Kjeldahl es una técnica analítica fundamental para la 
determinación cuantitativa de nitrógeno en compuestos orgánicos. Desarrollado por Johan Kjeldahl 
en 1883, este método se basa en la digestión de la muestra con ácido sulfúrico concentrado, 
seguida de destilación y titulación.""",
        'orden': 1
    }
)
print("   ✓ Fundamento teórico agregado")

# 5. Agregar Procedimientos
print("\n📝 Agregando Procedimientos...")
procedimientos = [
    ("Preparación de la muestra", "Pesar exactamente 1g de muestra y colocar en matraz Kjeldahl"),
    ("Digestión", "Agregar 10ml de H2SO4 concentrado y calentar hasta clarificación completa"),
    ("Destilación", "Destilar y recoger el destilado en solución de ácido bórico"),
    ("Titulación", "Titular con HCl 0.1N usando indicador mixto hasta cambio de color")
]

for i, (titulo, desc) in enumerate(procedimientos, start=1):
    Procedimientos.objects.get_or_create(
        contenido_analitico=contenido,
        numero_paso=i,
        defaults={
            'titulo_paso': titulo,
            'descripcion': desc,
            'orden': i
        }
    )
    print(f"   ✓ Paso {i}: {titulo}")

print("\n" + "=" * 70)
print("✅ DATOS DE PRUEBA AGREGADOS CORRECTAMENTE")
print("=" * 70)
print("\nResumen:")
print(f"  - Criterios de Desempeño: {ObjetivoPractica.objects.filter(contenido_analitico=contenido, tipo_objetivo='desempeno').count()}")
print(f"  - Objetivos de la Práctica: {ObjetivoPractica.objects.filter(contenido_analitico=contenido).exclude(tipo_objetivo='desempeno').count()}")
print(f"  - Competencias: {Competencias.objects.filter(contenido_analitico=contenido).count()}")
print(f"  - Fundamentos Teóricos: {FundamentoTeorico.objects.filter(contenido_analitico=contenido).count()}")
print(f"  - Procedimientos: {Procedimientos.objects.filter(contenido_analitico=contenido).count()}")
