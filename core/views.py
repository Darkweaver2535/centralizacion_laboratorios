from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from .models import UnidadAcademica, Carrera, Asignatura, UnidadTematica, GuiaLaboratorio, Practica, Laboratorio

@login_required
def dashboard_view(request):
    """Vista principal del dashboard actualizada con nueva estructura"""
    
    # Estadísticas generales
    stats = {
        'total_unidades_academicas': UnidadAcademica.objects.count(),
        'total_carreras': Carrera.objects.count(),
        'total_asignaturas': Asignatura.objects.count(),
        'total_laboratorios': Laboratorio.objects.count(),
    }
    
    # Intentar obtener estadísticas de equipos e insumos si las apps están disponibles
    try:
        from equipos.models import Equipo
        stats['total_equipos'] = Equipo.objects.count()
        stats['equipos_operativos'] = Equipo.objects.filter(estado='operativo').count()
        stats['equipos_mantenimiento'] = Equipo.objects.filter(estado='mantenimiento').count()
    except ImportError:
        stats['total_equipos'] = 0
        stats['equipos_operativos'] = 0
        stats['equipos_mantenimiento'] = 0
    
    try:
        from insumos.models import Insumo
        stats['total_insumos'] = Insumo.objects.count()
        stats['insumos_disponibles'] = Insumo.objects.filter(estado='disponible').count()
        stats['insumos_agotados'] = Insumo.objects.filter(estado='agotado').count()
    except ImportError:
        stats['total_insumos'] = 0
        stats['insumos_disponibles'] = 0
        stats['insumos_agotados'] = 0
    
    # Datos por unidad académica
    unidades_stats = []
    for unidad in UnidadAcademica.objects.all():
        laboratorios_count = Laboratorio.objects.filter(unidad_academica=unidad).count()
        
        try:
            from equipos.models import Equipo
            equipos_count = Equipo.objects.filter(unidad_academica=unidad).count()
        except ImportError:
            equipos_count = 0
        
        try:
            from insumos.models import Insumo
            insumos_count = Insumo.objects.filter(unidad_academica=unidad).count()
        except ImportError:
            insumos_count = 0
        
        unidades_stats.append({
            'nombre': unidad.get_nombre_display(),
            'laboratorios': laboratorios_count,
            'equipos': equipos_count,
            'insumos': insumos_count,
        })
    
    # Estadísticas por carrera
    carreras_stats = []
    for carrera in Carrera.objects.all()[:5]:  # Top 5 carreras
        asignaturas_count = Asignatura.objects.filter(carrera=carrera).count()
        
        try:
            from equipos.models import Equipo
            equipos_count = Equipo.objects.filter(carrera=carrera).count()
        except ImportError:
            equipos_count = 0
        
        carreras_stats.append({
            'nombre': carrera.get_nombre_display(),
            'asignaturas': asignaturas_count,
            'equipos': equipos_count,
        })
    
    context = {
        'stats': stats,
        'unidades_stats': unidades_stats,
        'carreras_stats': carreras_stats,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def get_carreras_por_unidad_ajax(request):
    """Obtener carreras filtradas por unidad académica"""
    unidad_id = request.GET.get('unidad_id')
    
    if unidad_id:
        try:
            from equipos.models import Equipo
            carreras = Carrera.objects.filter(
                id__in=Equipo.objects.filter(unidad_academica_id=unidad_id).values_list('carrera_id', flat=True).distinct()
            ).distinct()
        except ImportError:
            carreras = Carrera.objects.all()
    else:
        carreras = Carrera.objects.all()
    
    carreras_data = [
        {'id': carrera.id, 'nombre': carrera.nombre, 'display': carrera.get_nombre_display()}
        for carrera in carreras
    ]
    
    return JsonResponse({'carreras': carreras_data})

@login_required
def get_asignaturas_por_carrera_ajax(request):
    """Obtener asignaturas filtradas por carrera y semestre"""
    carrera_id = request.GET.get('carrera_id')
    semestre = request.GET.get('semestre')
    
    asignaturas = Asignatura.objects.all()
    
    if carrera_id:
        asignaturas = asignaturas.filter(carrera_id=carrera_id)
    
    if semestre:
        asignaturas = asignaturas.filter(semestre=semestre)
    
    asignaturas_data = [
        {
            'id': asignatura.id, 
            'nombre': asignatura.nombre, 
            'display': asignatura.get_nombre_display(),
            'semestre': asignatura.semestre,
            'carga_semanal': asignatura.carga_horaria_semanal,
            'carga_semestral': asignatura.carga_horaria_semestral
        }
        for asignatura in asignaturas
    ]
    
    return JsonResponse({'asignaturas': asignaturas_data})

@login_required
def get_unidades_tematicas_ajax(request):
    """Obtener unidades temáticas por asignatura"""
    asignatura_id = request.GET.get('asignatura_id')
    
    if asignatura_id:
        unidades = UnidadTematica.objects.filter(asignatura_id=asignatura_id)
    else:
        unidades = UnidadTematica.objects.none()
    
    unidades_data = [
        {'id': unidad.id, 'numero': unidad.numero, 'nombre': unidad.nombre}
        for unidad in unidades
    ]
    
    return JsonResponse({'unidades_tematicas': unidades_data})

@login_required
def get_guias_laboratorio_ajax(request):
    """Obtener guías de laboratorio por unidad temática"""
    unidad_tematica_id = request.GET.get('unidad_tematica_id')
    
    if unidad_tematica_id:
        guias = GuiaLaboratorio.objects.filter(unidad_tematica_id=unidad_tematica_id)
    else:
        guias = GuiaLaboratorio.objects.none()
    
    guias_data = [
        {'id': guia.id, 'numero': guia.numero, 'nombre': guia.nombre}
        for guia in guias
    ]
    
    return JsonResponse({'guias_laboratorio': guias_data})

@login_required
def get_practicas_ajax(request):
    """Obtener prácticas por guía de laboratorio"""
    guia_id = request.GET.get('guia_id')
    
    if guia_id:
        practicas = Practica.objects.filter(guia_laboratorio_id=guia_id)
    else:
        practicas = Practica.objects.none()
    
    practicas_data = [
        {'id': practica.id, 'numero': practica.numero, 'nombre': practica.nombre}
        for practica in practicas
    ]
    
    return JsonResponse({'practicas': practicas_data})

@login_required
def get_laboratorios_ajax(request):
    """Obtener laboratorios por unidad académica"""
    unidad_id = request.GET.get('unidad_id')
    
    if unidad_id:
        laboratorios = Laboratorio.objects.filter(unidad_academica_id=unidad_id)
    else:
        laboratorios = Laboratorio.objects.all()
    
    laboratorios_data = [
        {
            'id': laboratorio.id, 
            'nombre': laboratorio.nombre, 
            'display': laboratorio.get_nombre_display(),
            'seccion_area': laboratorio.seccion_area,
            'identificador_aula': laboratorio.identificador_aula
        }
        for laboratorio in laboratorios
    ]
    
    return JsonResponse({'laboratorios': laboratorios_data})
