#!/usr/bin/env python3
"""
Script para probar específicamente el filtrado de equipos como lo hace el frontend
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.conf import settings
from django.test import Client
from django.contrib.auth.models import User

from ingreso_datos.models import *

def test_filtrado_frontend():
    """Test que simula exactamente lo que hace el frontend"""
    print("=== PRUEBA DE FILTRADO COMO EL FRONTEND ===\n")
    
    # Crear un cliente de prueba
    client = Client()
    
    # Obtener el usuario admin
    try:
        user = User.objects.get(username='admin')
        client.force_login(user)
    except User.DoesNotExist:
        print("ERROR: Usuario admin no existe")
        return
    
    # Obtener un tipo de equipo para las pruebas
    tipo_equipo = TipoEquipo.objects.first()
    if not tipo_equipo:
        print("ERROR: No hay tipos de equipo en la base de datos")
        return
    
    print(f"Tipo de equipo de prueba: {tipo_equipo.nombre}")
    
    # Probar cada unidad académica
    unidades = ['la_paz', 'cochabamba', 'santa_cruz', 'riberalta', 'tropico']
    
    for unidad in unidades:
        print(f"\n--- Probando {unidad} ---")
        
        # Simular la petición POST que hace el frontend
        response = client.post('/ingreso-datos/', {
            'action': 'get_equipos_individuales',
            'tipo_equipo': tipo_equipo.nombre,
            'unidad_academica': unidad
        })
        
        if response.status_code == 200:
            try:
                data = response.json()
                equipos = data.get('equipos', [])
                stats = data.get('estadisticas', {})
                
                print(f"  ✓ Equipos encontrados: {len(equipos)}")
                print(f"  ✓ Total equipos: {stats.get('total_equipos', 0)}")
                print(f"  ✓ Operativos: {stats.get('operativos', 0)}")
                
                # Verificar que los equipos pertenecen a la unidad correcta
                if equipos:
                    for equipo in equipos[:3]:  # Mostrar solo los primeros 3
                        equipo_obj = EquipoIndividual.objects.get(id=equipo['id'])
                        unidad_real = equipo_obj.unidad_academica.nombre if equipo_obj.unidad_academica else 'sin_unidad'
                        if unidad_real != unidad:
                            print(f"  ❌ ERROR: Equipo {equipo['codigo']} pertenece a {unidad_real}, no a {unidad}")
                        else:
                            print(f"  ✓ Equipo {equipo['codigo']} pertenece correctamente a {unidad}")
                
            except Exception as e:
                print(f"  ❌ Error parsing JSON: {e}")
                print(f"  Response content: {response.content}")
        else:
            print(f"  ❌ Error HTTP: {response.status_code}")
    
    print("\n=== VERIFICACIÓN DIRECTA DE BASE DE DATOS ===")
    for unidad in unidades:
        try:
            ua = UnidadAcademica.objects.get(nombre=unidad)
            total_equipos = EquipoIndividual.objects.filter(unidad_academica=ua).count()
            equipos_tipo = EquipoIndividual.objects.filter(
                unidad_academica=ua,
                tipo_equipo=tipo_equipo
            ).count()
            print(f"{unidad}: {total_equipos} equipos totales, {equipos_tipo} del tipo {tipo_equipo.nombre}")
        except UnidadAcademica.DoesNotExist:
            print(f"{unidad}: Unidad académica no existe")

if __name__ == "__main__":
    test_filtrado_frontend()
