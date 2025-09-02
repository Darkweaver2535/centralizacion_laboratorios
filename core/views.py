from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from .models import (
    UnidadAcademica, Carrera, Asignatura, UnidadTematica, GuiaLaboratorio, 
    Practica, Laboratorio, CriterioDesempeno, UnidadDidactica, ContenidoAnalitico
)

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
        stats['equipos_buenos'] = Equipo.objects.filter(estado='bueno').count()
        stats['equipos_regulares'] = Equipo.objects.filter(estado='regular').count()
        stats['equipos_malos'] = Equipo.objects.filter(estado='malo').count()
    except ImportError:
        stats['total_equipos'] = 0
        stats['equipos_buenos'] = 0
        stats['equipos_regulares'] = 0
        stats['equipos_malos'] = 0
    
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
        # Obtener todas las carreras disponibles para esta unidad académica
        carreras = Carrera.objects.filter(unidad_academica_id=unidad_id).distinct()
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


# =====================================
# VISTAS PARA MALLA CURRICULAR
# =====================================

@login_required
def malla_curricular_view(request):
    """Vista principal de malla curricular"""
    
    # Estadísticas generales
    stats = {
        'total_asignaturas': Asignatura.objects.count(),
        'total_criterios': CriterioDesempeno.objects.count(),
        'total_unidades_didacticas': UnidadDidactica.objects.count(),
        'total_contenidos': ContenidoAnalitico.objects.count(),
    }
    
    # Asignaturas por carrera con datos de malla curricular
    carreras_con_malla = []
    for carrera in Carrera.objects.all():
        asignaturas = Asignatura.objects.filter(carrera=carrera).order_by('semestre', 'nombre')
        if asignaturas.exists():
            carreras_con_malla.append({
                'carrera': carrera,
                'asignaturas': asignaturas,
                'total_asignaturas': asignaturas.count(),
                'con_codigo_competencia': asignaturas.exclude(codigo_competencia__in=['', None]).count(),
                'con_sigla_curricular': asignaturas.exclude(sigla_curricular__in=['', None]).count(),
            })
    
    # Datos para filtros
    unidades_academicas = UnidadAcademica.objects.all()
    carreras = Carrera.objects.all()
    
    context = {
        'stats': stats,
        'carreras_con_malla': carreras_con_malla,
        'unidades_academicas': unidades_academicas,
        'carreras': carreras,
    }
    
    return render(request, 'core/malla_curricular.html', context)


@login_required
def detalle_asignatura_view(request, asignatura_id):
    """Vista detallada de una asignatura con toda su malla curricular"""
    
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    
    # Criterios de desempeño
    criterios = CriterioDesempeno.objects.filter(asignatura=asignatura)
    
    # Unidades didácticas
    unidades_didacticas = UnidadDidactica.objects.filter(asignatura=asignatura)
    
    # Contenidos analíticos por unidad didáctica
    contenidos_por_unidad = {}
    for unidad in unidades_didacticas:
        contenidos_por_unidad[unidad.id] = ContenidoAnalitico.objects.filter(unidad_didactica=unidad)
    
    # Unidades temáticas tradicionales (si existen)
    unidades_tematicas = UnidadTematica.objects.filter(asignatura=asignatura)
    
    # Estadísticas de la asignatura
    asignatura_stats = {
        'criterios_count': criterios.count(),
        'unidades_didacticas_count': unidades_didacticas.count(),
        'contenidos_count': sum(contenidos.count() for contenidos in contenidos_por_unidad.values()),
        'unidades_tematicas_count': unidades_tematicas.count(),
    }
    
    context = {
        'asignatura': asignatura,
        'criterios': criterios,
        'unidades_didacticas': unidades_didacticas,
        'contenidos_por_unidad': contenidos_por_unidad,
        'unidades_tematicas': unidades_tematicas,
        'asignatura_stats': asignatura_stats,
    }
    
    return render(request, 'core/detalle_asignatura.html', context)


@login_required
def get_criterios_desempeno_ajax(request):
    """Obtener criterios de desempeño por asignatura"""
    asignatura_id = request.GET.get('asignatura_id')
    
    if asignatura_id:
        criterios = CriterioDesempeno.objects.filter(asignatura_id=asignatura_id)
    else:
        criterios = CriterioDesempeno.objects.all()
    
    criterios_data = [
        {
            'id': criterio.id,
            'nombre': criterio.nombre,
            'descripcion': criterio.descripcion,
            'asignatura': criterio.asignatura.get_nombre_display()
        }
        for criterio in criterios
    ]
    
    return JsonResponse({'criterios': criterios_data})


@login_required
def get_unidades_didacticas_ajax(request):
    """Obtener unidades didácticas por asignatura"""
    asignatura_id = request.GET.get('asignatura_id')
    
    if asignatura_id:
        unidades = UnidadDidactica.objects.filter(asignatura_id=asignatura_id)
    else:
        unidades = UnidadDidactica.objects.all()
    
    unidades_data = [
        {
            'id': unidad.id,
            'nombre': unidad.nombre,
            'descripcion': unidad.descripcion,
            'asignatura': unidad.asignatura.get_nombre_display()
        }
        for unidad in unidades
    ]
    
    return JsonResponse({'unidades_didacticas': unidades_data})


@login_required
def get_contenidos_analiticos_ajax(request):
    """Obtener contenidos analíticos por unidad didáctica"""
    unidad_didactica_id = request.GET.get('unidad_didactica_id')
    asignatura_id = request.GET.get('asignatura_id')
    
    if unidad_didactica_id:
        contenidos = ContenidoAnalitico.objects.filter(unidad_didactica_id=unidad_didactica_id)
    elif asignatura_id:
        contenidos = ContenidoAnalitico.objects.filter(unidad_didactica__asignatura_id=asignatura_id)
    else:
        contenidos = ContenidoAnalitico.objects.all()
    
    contenidos_data = [
        {
            'id': contenido.id,
            'nombre': contenido.nombre,
            'descripcion': contenido.descripcion,
            'unidad_didactica': contenido.unidad_didactica.nombre,
            'asignatura': contenido.unidad_didactica.asignatura.get_nombre_display()
        }
        for contenido in contenidos
    ]
    
    return JsonResponse({'contenidos_analiticos': contenidos_data})
