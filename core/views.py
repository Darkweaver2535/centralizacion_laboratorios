from django.shortcuts import render, get_object_or_404, redirect
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
    """Vista principal de malla curricular con django-filter integrado"""
    
    # Importar filtros de django-filter
    from .filters import AsignaturaFilter
    from django.core.paginator import Paginator
    
    # Obtener parámetros de filtrado
    categoria = request.GET.get('categoria', 'asignaturas')
    
    # Aplicar filtros con django-filter
    if categoria == 'asignaturas':
        # Usar AsignaturaFilter para filtrado automático
        filterset = AsignaturaFilter(request.GET, queryset=Asignatura.objects.select_related(
            'carrera', 'carrera__unidad_academica'
        ))
        items = filterset.qs
    else:
        # Fallback para otras categorías
        filterset = None
        items = Asignatura.objects.select_related('carrera', 'carrera__unidad_academica')
    
    # Paginación
    paginator = Paginator(items, 20)  # 20 elementos por página
    page_number = request.GET.get('page')
    items_page = paginator.get_page(page_number)
    
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
        
        # Datos de paginación y filtros django-filter
        'asignaturas': items_page,  # Para compatibilidad con template existente
        'filterset': filterset,  # Para acceder a los filtros en el template
        'filtered_count': items.count(),  # Número de elementos filtrados
        'total_count': Asignatura.objects.count(),  # Total sin filtros
        'categoria': categoria,
        
        # Valores seleccionados para mantener en formulario
        'unidad_seleccionada': request.GET.get('unidad_academica', ''),
        'carrera_seleccionada': request.GET.get('carrera', ''),
        'semestre_seleccionado': request.GET.get('semestre', ''),
        'search_term': request.GET.get('search', ''),
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


# =====================================
# VISTAS PARA AGREGAR DATOS COMPLETOS
# =====================================

from .forms import (
    AsignaturaCompletaForm, CriterioDesempenoForm, UnidadDidacticaForm, 
    ContenidoAnaliticoForm, UnidadAcademicaCarreraForm,
    BibliografiaFormSet, PracticaLaboratorioFormSet, TituloFormSet, 
    CompetenciasFormSet, ObjetivoPracticaFormSet, FundamentoTeoricoFormSet,
    MaterialesHerramientasEquiposFormSet, ProcedimientosFormSet, 
    CalculosResultadosFormSet, CuestionarioFormSet
)
from django.contrib import messages
from django.db import transaction


@login_required
def agregar_datos_malla_view(request):
    """Vista principal para agregar datos completos de malla curricular"""
    
    if request.method == 'POST':
        # Procesar formulario principal
        asignatura_form = AsignaturaCompletaForm(request.POST)
        unidad_carrera_form = UnidadAcademicaCarreraForm(request.POST)
        
        if asignatura_form.is_valid() and unidad_carrera_form.is_valid():
            try:
                with transaction.atomic():
                    # Guardar asignatura
                    asignatura = asignatura_form.save()
                    
                    # Crear criterios de desempeño si se proporcionaron
                    criterios_data = request.POST.getlist('criterios_desempeno')
                    for criterio_desc in criterios_data:
                        if criterio_desc.strip():
                            CriterioDesempeno.objects.create(
                                nombre=criterio_desc[:200],  # Limitar longitud
                                descripcion=criterio_desc,
                                asignatura=asignatura
                            )
                    
                    # Crear unidades didácticas si se proporcionaron
                    unidades_data = request.POST.getlist('unidades_didacticas')
                    unidades_desc = request.POST.getlist('unidades_didacticas_desc')
                    
                    for i, unidad_nombre in enumerate(unidades_data):
                        if unidad_nombre.strip():
                            descripcion = unidades_desc[i] if i < len(unidades_desc) else ''
                            unidad_didactica = UnidadDidactica.objects.create(
                                nombre=unidad_nombre[:200],
                                descripcion=descripcion,
                                asignatura=asignatura
                            )
                            
                            # Crear contenidos analíticos para esta unidad
                            contenidos_data = request.POST.getlist(f'contenidos_analiticos_{i}')
                            contenidos_desc = request.POST.getlist(f'contenidos_analiticos_desc_{i}')
                            
                            for j, contenido_nombre in enumerate(contenidos_data):
                                if contenido_nombre.strip():
                                    desc_contenido = contenidos_desc[j] if j < len(contenidos_desc) else ''
                                    ContenidoAnalitico.objects.create(
                                        nombre=contenido_nombre[:300],
                                        descripcion=desc_contenido,
                                        unidad_didactica=unidad_didactica
                                    )
                    
                    messages.success(request, f'Asignatura "{asignatura}" creada exitosamente con todos sus componentes.')
                    return redirect('core:malla_curricular')
                    
            except Exception as e:
                messages.error(request, f'Error al guardar los datos: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        asignatura_form = AsignaturaCompletaForm()
        unidad_carrera_form = UnidadAcademicaCarreraForm()
    
    context = {
        'asignatura_form': asignatura_form,
        'unidad_carrera_form': unidad_carrera_form,
        'unidades_academicas': UnidadAcademica.objects.all(),
        'carreras': Carrera.objects.all(),
    }
    
    return render(request, 'core/agregar_datos_malla.html', context)


@login_required
def agregar_componentes_contenido_view(request, contenido_id):
    """Vista para agregar componentes detallados a un contenido analítico"""
    
    contenido = get_object_or_404(ContenidoAnalitico, id=contenido_id)
    
    if request.method == 'POST':
        # Procesar todos los formsets
        formsets_data = {
            'bibliografia': BibliografiaFormSet(request.POST, instance=contenido, prefix='bibliografia'),
            'practicas': PracticaLaboratorioFormSet(request.POST, instance=contenido, prefix='practicas'),
            'titulos': TituloFormSet(request.POST, instance=contenido, prefix='titulos'),
            'competencias': CompetenciasFormSet(request.POST, instance=contenido, prefix='competencias'),
            'objetivos': ObjetivoPracticaFormSet(request.POST, instance=contenido, prefix='objetivos'),
            'fundamentos': FundamentoTeoricoFormSet(request.POST, instance=contenido, prefix='fundamentos'),
            'materiales': MaterialesHerramientasEquiposFormSet(request.POST, instance=contenido, prefix='materiales'),
            'procedimientos': ProcedimientosFormSet(request.POST, instance=contenido, prefix='procedimientos'),
            'calculos': CalculosResultadosFormSet(request.POST, instance=contenido, prefix='calculos'),
            'cuestionarios': CuestionarioFormSet(request.POST, instance=contenido, prefix='cuestionarios'),
        }
        
        all_valid = all(formset.is_valid() for formset in formsets_data.values())
        
        if all_valid:
            try:
                with transaction.atomic():
                    for formset in formsets_data.values():
                        formset.save()
                    
                    messages.success(request, f'Componentes agregados exitosamente al contenido "{contenido.nombre}".')
                    return redirect('core:detalle_asignatura', asignatura_id=contenido.unidad_didactica.asignatura.id)
                    
            except Exception as e:
                messages.error(request, f'Error al guardar los componentes: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en los formularios.')
    else:
        formsets_data = {
            'bibliografia': BibliografiaFormSet(instance=contenido, prefix='bibliografia'),
            'practicas': PracticaLaboratorioFormSet(instance=contenido, prefix='practicas'),
            'titulos': TituloFormSet(instance=contenido, prefix='titulos'),
            'competencias': CompetenciasFormSet(instance=contenido, prefix='competencias'),
            'objetivos': ObjetivoPracticaFormSet(instance=contenido, prefix='objetivos'),
            'fundamentos': FundamentoTeoricoFormSet(instance=contenido, prefix='fundamentos'),
            'materiales': MaterialesHerramientasEquiposFormSet(instance=contenido, prefix='materiales'),
            'procedimientos': ProcedimientosFormSet(instance=contenido, prefix='procedimientos'),
            'calculos': CalculosResultadosFormSet(instance=contenido, prefix='calculos'),
            'cuestionarios': CuestionarioFormSet(instance=contenido, prefix='cuestionarios'),
        }
    
    context = {
        'contenido': contenido,
        'formsets': formsets_data,
    }
    
    return render(request, 'core/agregar_componentes_contenido.html', context)


@login_required
def get_carreras_por_unidad_ajax(request):
    """API para obtener carreras filtradas por unidad académica"""
    unidad_id = request.GET.get('unidad_id')
    
    if unidad_id:
        carreras = Carrera.objects.filter(unidad_academica_id=unidad_id)
    else:
        carreras = Carrera.objects.all()
    
    carreras_data = [
        {
            'id': carrera.id,
            'nombre': carrera.nombre,
            'display': carrera.get_nombre_display()
        }
        for carrera in carreras
    ]
    
    return JsonResponse({'carreras': carreras_data})
