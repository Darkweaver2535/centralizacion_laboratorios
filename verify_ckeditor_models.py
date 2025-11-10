#!/usr/bin/env python3

"""
Script de verificación rápida de CKEditor en los modelos
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import FundamentoTeorico, Procedimientos, CalculosResultados, Cuestionario
from django_ckeditor_5.fields import CKEditor5Field

print("🔍 Verificando modelos con CKEditor...")
print("=" * 60)

models_to_check = [
    (FundamentoTeorico, ['contenido']),
    (Procedimientos, ['descripcion']),
    (CalculosResultados, ['procedimiento_calculo']),
    (Cuestionario, ['pregunta', 'respuesta_esperada'])
]

all_good = True
for model_class, field_names in models_to_check:
    print(f"\n📋 Modelo: {model_class.__name__}")
    for field_name in field_names:
        try:
            field = model_class._meta.get_field(field_name)
            if isinstance(field, CKEditor5Field):
                print(f"   ✅ {field_name}: CKEditor5Field")
            else:
                print(f"   ⚠️  {field_name}: {type(field).__name__} (no es CKEditor5Field)")
                all_good = False
        except Exception as e:
            print(f"   ❌ {field_name}: Error - {e}")
            all_good = False

print("\n" + "=" * 60)
if all_good:
    print("🎉 ¡Todos los modelos tienen CKEditor correctamente configurado!")
else:
    print("⚠️  Algunos modelos necesitan ajustes")

print("\n📝 Próximos pasos:")
print("1. Visita: http://127.0.0.1:8000/dashboard/malla-curricular/agregar-datos/")
print("2. Llena los campos básicos del formulario")
print("3. Haz clic en 'Agregar Grupo de Datos Adicionales'")
print("4. Verifica que los 4 campos tengan la barra de herramientas de CKEditor:")
print("   - Fundamento Teórico")
print("   - Procedimientos")
print("   - Cálculos y Resultados")
print("   - Cuestionario")
print("\n✨ Los campos ahora soportan:")
print("   - Formato de texto (negrita, cursiva, etc.)")
print("   - Listas numeradas y con viñetas")
print("   - Insertar tablas")
print("   - Insertar imágenes")
print("   - Fórmulas matemáticas (subscript/superscript)")
print("   - Links e hipervínculos")