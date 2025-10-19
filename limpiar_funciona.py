#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

print("🔍 Verificando FUNCIONA FINAL...")

# Buscar contenidos con FUNCIONA
contenidos = ContenidoAnalitico.objects.filter(nombre__icontains='FUNCIONA')
for c in contenidos:
    print(f'🗑️ Eliminando contenido: ID {c.id} - "{c.nombre}" en {c.unidad_didactica.asignatura.nombre}')
    c.delete()

# Buscar títulos con FUNCIONA  
titulos = Titulo.objects.filter(texto__icontains='FUNCIONA')
for t in titulos:
    print(f'🗑️ Eliminando título: "{t.texto}" del contenido {t.contenido_analitico.nombre}')
    t.delete()

print("✅ Limpieza de FUNCIONA completada")