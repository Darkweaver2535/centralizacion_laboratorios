from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt
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

@csrf_exempt
def equipos_ajax(request):
    """Vista AJAX para manejar peticiones relacionadas con equipos"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'get_tipos_equipo':
            unidad_academica = request.POST.get('unidad_academica')
            limit = request.POST.get('limit', '100')  # Límite por defecto
            offset = request.POST.get('offset', '0')
            search = request.POST.get('search', '')
            
            if not unidad_academica:
                return JsonResponse({'error': 'Unidad académica requerida'}, status=400)
            
            try:
                limit = int(limit)
                offset = int(offset)
                # Limitar máximo a 200 para evitar sobrecarga
                limit = min(limit, 200)
            except ValueError:
                return JsonResponse({'error': 'Parámetros de paginación inválidos'}, status=400)
            
            # Convertir a minúsculas para coincidir con la base de datos
            unidad_academica = unidad_academica.lower()
            
            # Filtrar tipos de equipo que tienen equipos individuales en la unidad académica
            tipos_equipo = TipoEquipo.objects.filter(
                equipos_individuales__unidad_academica__nombre=unidad_academica
            ).distinct()
            
            # Aplicar filtro de búsqueda si se proporciona
            if search:
                tipos_equipo = tipos_equipo.filter(
                    nombre__icontains=search
                )
            
            # Ordenar por nombre para consistencia
            tipos_equipo = tipos_equipo.order_by('nombre')
            
            # Contar total antes de aplicar paginación
            total_count = tipos_equipo.count()
            
            # Aplicar paginación
            tipos_equipo = tipos_equipo[offset:offset + limit]
            
            # Preparar datos para el frontend
            tipos_data = []
            for tipo in tipos_equipo:
                tipos_data.append({
                    'nombre': tipo.nombre,
                    'display_name': tipo.get_nombre_display()
                })
            
            return JsonResponse({
                'tipos_equipo': tipos_data,
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            })
        
        elif action == 'get_equipos_individuales':
            tipo_equipo = request.POST.get('tipo_equipo')
            unidad_academica = request.POST.get('unidad_academica')
            
            if not tipo_equipo or not unidad_academica:
                return JsonResponse({'error': 'Tipo de equipo y unidad académica requeridos'}, status=400)
            
            # Convertir a minúsculas para coincidir con la base de datos
            unidad_academica = unidad_academica.lower()
            
            # Filtrar equipos individuales operativos
            equipos = EquipoIndividual.objects.filter(
                tipo_equipo__nombre=tipo_equipo,
                unidad_academica__nombre=unidad_academica,
                estado_operativo='operativo'
            ).select_related('tipo_equipo')
            
            # Preparar datos para la respuesta
            equipos_data = []
            for equipo in equipos:
                equipos_data.append({
                    'id': equipo.id,
                    'codigo': equipo.codigo,
                    'tipo_equipo': equipo.tipo_equipo.nombre,
                    'estado_fisico': equipo.get_estado_fisico_display(),
                    'estado_operativo': equipo.get_estado_operativo_display(),
                    'ubicacion': equipo.ubicacion or 'Sin especificar',
                    'display_name': f"{equipo.codigo} - {equipo.tipo_equipo.nombre} ({equipo.get_estado_fisico_display()})"
                })
            
            return JsonResponse({
                'equipos': equipos_data,
                'estadisticas': {
                    'total': len(equipos_data),
                    'operativos': len(equipos_data)  # Ya están filtrados por operativo
                },
                'capacidad_estudiantes': len(equipos_data)  # Cada equipo puede atender 1 estudiante
            })
        
        elif action == 'get_recomendacion':
            tipo_equipo = request.POST.get('tipo_equipo')
            cantidad_estudiantes = request.POST.get('cantidad_estudiantes')
            unidad_academica = request.POST.get('unidad_academica')
            
            if not all([tipo_equipo, cantidad_estudiantes, unidad_academica]):
                return JsonResponse({'error': 'Todos los parámetros son requeridos'}, status=400)
            
            try:
                cantidad_estudiantes = int(cantidad_estudiantes)
            except ValueError:
                return JsonResponse({'error': 'Cantidad de estudiantes debe ser un número'}, status=400)
            
            # Convertir a minúsculas para coincidir con la base de datos
            unidad_academica = unidad_academica.lower()
            
            # Contar equipos disponibles
            equipos_disponibles = EquipoIndividual.objects.filter(
                tipo_equipo__nombre=tipo_equipo,
                unidad_academica__nombre=unidad_academica
            ).count()
            
            # Lógica de recomendación
            if equipos_disponibles >= cantidad_estudiantes:
                recomendacion = "SUFICIENTES"
                mensaje = f"Hay {equipos_disponibles} equipos disponibles para {cantidad_estudiantes} estudiantes"
            else:
                faltantes = cantidad_estudiantes - equipos_disponibles
                recomendacion = "INSUFICIENTES"
                mensaje = f"Faltan {faltantes} equipos. Hay {equipos_disponibles} disponibles para {cantidad_estudiantes} estudiantes"
            
            return JsonResponse({
                'recomendacion': recomendacion,
                'mensaje': mensaje,
                'equipos_disponibles': equipos_disponibles,
                'cantidad_estudiantes': cantidad_estudiantes
            })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)