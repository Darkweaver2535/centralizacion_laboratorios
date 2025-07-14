from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q
from ingreso_datos.models import *
import json

@login_required
def visualizacion_view(request):
    """Vista principal de visualización y análisis"""
    
    # Obtener datos para los filtros
    unidades = UnidadAcademica.objects.all()
    carreras = Carrera.objects.all()
    tipos_equipos = TipoEquipo.objects.all()
    
    # Obtener estadísticas generales
    stats = {
        'total_laboratorios': Laboratorio.objects.count(),
        'total_ensayos': Ensayo.objects.count(),
        'total_equipos': EquipoIndividual.objects.count(),
        'total_materias': Materia.objects.count(),
    }
    
    context = {
        'unidades': unidades,
        'carreras': carreras,
        'tipos_equipos': tipos_equipos,
        'stats': stats,
    }
    
    return render(request, 'visualizacion.html', context)

@login_required
def filtrar_datos(request):
    """Vista AJAX para filtrar datos según los criterios seleccionados"""
    
    # Obtener filtros del request
    filtros = {
        'unidad_academica': request.GET.get('unidad_academica'),
        'semestre': request.GET.get('semestre'),
        'carrera': request.GET.get('carrera'),
        'materia': request.GET.get('materia'),
        'laboratorio': request.GET.get('laboratorio'),
        'tipo_equipo': request.GET.get('tipo_equipo'),
    }
    
    # Construir la consulta base
    laboratorios = Laboratorio.objects.all()
    
    # Aplicar filtros
    if filtros['unidad_academica']:
        laboratorios = laboratorios.filter(unidad_academica__nombre=filtros['unidad_academica'])
    
    if filtros['semestre']:
        laboratorios = laboratorios.filter(materia__semestre=filtros['semestre'])
    
    if filtros['carrera']:
        laboratorios = laboratorios.filter(materia__carrera__nombre=filtros['carrera'])
    
    if filtros['materia']:
        laboratorios = laboratorios.filter(materia__nombre=filtros['materia'])
    
    if filtros['laboratorio']:
        laboratorios = laboratorios.filter(nombre=filtros['laboratorio'])
    
    # Preparar datos para las tablas
    datos_laboratorios = []
    datos_ensayos = []
    datos_equipos = []
    
    for laboratorio in laboratorios:
        # Datos del laboratorio
        datos_laboratorios.append({
            'unidad_academica': laboratorio.unidad_academica.get_nombre_display(),
            'semestre': f"{laboratorio.materia.semestre}° Semestre",
            'carrera': laboratorio.materia.carrera.get_nombre_display(),
            'materia': laboratorio.materia.get_nombre_display(),
            'laboratorio': laboratorio.get_nombre_display(),
            'llenado_por': laboratorio.usuario_creador.get_full_name() or laboratorio.usuario_creador.username,
        })
        
        # Datos de ensayos
        for ensayo in laboratorio.ensayos.all():
            datos_ensayos.append({
                'laboratorio': laboratorio.get_nombre_display(),
                'ensayo': ensayo.get_nombre_display(),
                'estudiantes': ensayo.cantidad_estudiantes,
                'unidad_academica': laboratorio.unidad_academica.get_nombre_display(),
                'carrera': laboratorio.materia.carrera.get_nombre_display(),
                'materia': laboratorio.materia.get_nombre_display(),
                'llenado_por': laboratorio.usuario_creador.get_full_name() or laboratorio.usuario_creador.username,
            })
            
            # Datos de equipos
            for equipo in ensayo.equipos.all():
                equipos_seleccionados = equipo.equipos_seleccionados.all()
                
                if equipos_seleccionados:
                    for equipo_individual in equipos_seleccionados:
                        datos_equipos.append({
                            'laboratorio': laboratorio.get_nombre_display(),
                            'ensayo': ensayo.get_nombre_display(),
                            'tipo_equipo': equipo.tipo_equipo.get_nombre_display(),
                            'codigo_equipo': equipo_individual.codigo,
                            'estado_fisico': equipo_individual.get_estado_fisico_display(),
                            'unidad_academica': laboratorio.unidad_academica.get_nombre_display(),
                            'carrera': laboratorio.materia.carrera.get_nombre_display(),
                            'llenado_por': laboratorio.usuario_creador.get_full_name() or laboratorio.usuario_creador.username,
                        })
                else:
                    datos_equipos.append({
                        'laboratorio': laboratorio.get_nombre_display(),
                        'ensayo': ensayo.get_nombre_display(),
                        'tipo_equipo': equipo.tipo_equipo.get_nombre_display(),
                        'codigo_equipo': 'Sin especificar',
                        'estado_fisico': '-',
                        'unidad_academica': laboratorio.unidad_academica.get_nombre_display(),
                        'carrera': laboratorio.materia.carrera.get_nombre_display(),
                        'llenado_por': laboratorio.usuario_creador.get_full_name() or laboratorio.usuario_creador.username,
                    })
    
    # Filtrar equipos si se especificó tipo de equipo
    if filtros['tipo_equipo']:
        datos_equipos = [e for e in datos_equipos if e['tipo_equipo'] == TipoEquipo.objects.get(nombre=filtros['tipo_equipo']).get_nombre_display()]
    
    # Calcular estadísticas de los datos filtrados
    stats_filtradas = {
        'total_laboratorios': len(datos_laboratorios),
        'total_ensayos': len(datos_ensayos),
        'total_equipos': len(datos_equipos),
    }
    
    return JsonResponse({
        'laboratorios': datos_laboratorios,
        'ensayos': datos_ensayos,
        'equipos': datos_equipos,
        'stats': stats_filtradas,
    })

@login_required
def obtener_opciones_filtro(request):
    """Vista AJAX para obtener opciones de filtro dinámicas"""
    
    campo = request.GET.get('campo')
    filtros_actuales = {
        'unidad_academica': request.GET.get('unidad_academica'),
        'semestre': request.GET.get('semestre'),
        'carrera': request.GET.get('carrera'),
        'materia': request.GET.get('materia'),
        'laboratorio': request.GET.get('laboratorio'),
    }
    
    opciones = []
    
    # Construir consulta base
    laboratorios = Laboratorio.objects.all()
    
    # Aplicar filtros existentes
    if filtros_actuales['unidad_academica']:
        laboratorios = laboratorios.filter(unidad_academica__nombre=filtros_actuales['unidad_academica'])
    
    if filtros_actuales['semestre']:
        laboratorios = laboratorios.filter(materia__semestre=filtros_actuales['semestre'])
    
    if filtros_actuales['carrera']:
        laboratorios = laboratorios.filter(materia__carrera__nombre=filtros_actuales['carrera'])
    
    if filtros_actuales['materia']:
        laboratorios = laboratorios.filter(materia__nombre=filtros_actuales['materia'])
    
    # Obtener opciones según el campo solicitado
    if campo == 'semestre':
        semestres = laboratorios.values_list('materia__semestre', flat=True).distinct()
        opciones = [(str(s), f"{s}° Semestre") for s in sorted(semestres)]
    
    elif campo == 'carrera':
        carreras = laboratorios.values_list('materia__carrera__nombre', 'materia__carrera__nombre').distinct()
        opciones = [(c[0], Carrera.objects.get(nombre=c[0]).get_nombre_display()) for c in carreras]
    
    elif campo == 'materia':
        materias = laboratorios.values_list('materia__nombre', 'materia__nombre').distinct()
        opciones = [(m[0], Materia.objects.filter(nombre=m[0]).first().get_nombre_display()) for m in materias]
    
    elif campo == 'laboratorio':
        labs = laboratorios.values_list('nombre', 'nombre').distinct()
        opciones = [(l[0], Laboratorio.objects.filter(nombre=l[0]).first().get_nombre_display()) for l in labs]
    
    return JsonResponse({'opciones': opciones})