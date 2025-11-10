#!/usr/bin/env python3

"""
Script para actualizar los modelos CalculosResultados y Cuestionario 
para que soporten CKEditor5 en los campos relevantes.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

def main():
    print("🔧 Actualizando modelos para soporte de CKEditor...")
    
    # Primero, vamos a modificar los modelos en el archivo
    models_file_path = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/core/models.py'
    
    print("📝 Leyendo archivo de modelos...")
    with open(models_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Hacer backup
    with open(models_file_path + '.backup_ckeditor', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Actualizar CalculosResultados
    old_calculos = """    procedimiento_calculo = models.TextField(verbose_name="Procedimiento de cálculo")"""
    new_calculos = """    procedimiento_calculo = CKEditor5Field('Procedimiento de cálculo', config_name='extends')"""
    
    if old_calculos in content:
        content = content.replace(old_calculos, new_calculos)
        print("✅ Actualizado campo procedimiento_calculo en CalculosResultados")
    
    # Actualizar Cuestionario  
    old_pregunta = """    pregunta = models.TextField(verbose_name="Texto de la pregunta")"""
    new_pregunta = """    pregunta = CKEditor5Field('Texto de la pregunta', config_name='extends')"""
    
    if old_pregunta in content:
        content = content.replace(old_pregunta, new_pregunta)
        print("✅ Actualizado campo pregunta en Cuestionario")
    
    old_respuesta = """    respuesta_esperada = models.TextField(blank=True, verbose_name="Respuesta esperada o criterios")"""
    new_respuesta = """    respuesta_esperada = CKEditor5Field('Respuesta esperada o criterios', config_name='default', blank=True)"""
    
    if old_respuesta in content:
        content = content.replace(old_respuesta, new_respuesta)
        print("✅ Actualizado campo respuesta_esperada en Cuestionario")
    
    # Guardar cambios
    with open(models_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("💾 Archivo de modelos actualizado")
    print("\n🔄 Ahora necesitas ejecutar:")
    print("1. python manage.py makemigrations")
    print("2. python manage.py migrate")
    
if __name__ == '__main__':
    main()