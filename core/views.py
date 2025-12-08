from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from django.db import transaction
from django.contrib import messages
from .models import (
    UnidadAcademica, Carrera, Asignatura, UnidadTematica, GuiaLaboratorio, 
    Practica, Laboratorio, CriterioDesempeno, UnidadDidactica, ContenidoAnalitico,
    Bibliografia, PracticaLaboratorio, Titulo, Competencias, ObjetivoPractica,
    AuditoriaCreacionPractica,
    FundamentoTeorico, MaterialesHerramientasEquipos, Procedimientos, 
    CalculosResultados, Cuestionario
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
    """Obtener carreras filtradas por unidad académica - SOLO UALP para pruebas"""
    unidad_id = request.GET.get('unidad_id')
    
    # SOLO permitir carreras para UALP (ID=1) durante pruebas
    if unidad_id and unidad_id == '1':
        carreras = Carrera.objects.filter(unidad_academica_id=unidad_id).distinct()
    else:
        # Para otras unidades, devolver lista vacía
        carreras = Carrera.objects.none()
    
    carreras_data = [
        {'id': carrera.id, 'nombre': carrera.nombre, 'display': carrera.get_nombre_display()}
        for carrera in carreras
    ]
    
    return JsonResponse({'carreras': carreras_data})


@login_required
def get_asignaturas_por_carrera_ajax(request):
    """Obtener asignaturas filtradas por carrera y semestre con información adicional"""
    carrera_id = request.GET.get('carrera_id')
    semestre = request.GET.get('semestre')
    
    # Consulta optimizada con conteo de contenidos analíticos
    asignaturas = Asignatura.objects.annotate(
        contenido_analitico_count=Count('unidaddidactica__contenidoanalitico')
    ).select_related('carrera')
    
    if carrera_id:
        asignaturas = asignaturas.filter(carrera_id=carrera_id)
    
    if semestre:
        asignaturas = asignaturas.filter(semestre=semestre)
    
    asignaturas_data = []
    for asignatura in asignaturas:
        display_name = asignatura.get_nombre_display()
        
        # FILTRO DE SEGURIDAD: Omitir asignaturas con nombres problemáticos
        es_numerica = asignatura.nombre.isdigit()
        es_muy_corta = len(asignatura.nombre.strip()) <= 3
        tiene_solo_numeros = asignatura.nombre.replace(' ', '').isdigit()
        
        if es_numerica or (es_muy_corta and tiene_solo_numeros):
            continue  # Omitir esta asignatura problemática
        
        # FILTRO ADICIONAL: Omitir asignaturas duplicadas con nombres confusos
        nombres_similares = ['168', '169', '170', '171', '172', '173', '174', '175']
        if asignatura.nombre in nombres_similares:
            continue
        
        # FORMATO LIMPIO: Solo mostrar nombres descriptivos profesionales
        display_text = display_name
        if asignatura.sigla_curricular:
            display_text += f" ({asignatura.sigla_curricular})"
        
        asignaturas_data.append({
            'id': asignatura.id, 
            'nombre': asignatura.nombre, 
            'display': display_text,  # Formato mejorado con ID
            'display_simple': display_name,  # Nombre original por compatibilidad
            'semestre': asignatura.semestre,
            'carga_semanal': asignatura.carga_horaria_semanal,
            'carga_semestral': asignatura.carga_horaria_semestral,
            'codigo_competencia': asignatura.codigo_competencia or '',
            'sigla_curricular': asignatura.sigla_curricular or '',
            'carga_horaria_semestral': asignatura.carga_horaria_semestral,
            'carga_horaria_semanal': asignatura.carga_horaria_semanal,
            'warning_similar': False  # Se calculará después
        })
        
    # DETECCIÓN DE NOMBRES SIMILARES: Marcar asignaturas que podrían confundir
    nombres_vistos = {}
    for asig_data in asignaturas_data:
        nombre_base = asig_data['display_simple'].lower().strip()
        if nombre_base in nombres_vistos:
            # Marcar ambas como potencialmente confusas
            asig_data['warning_similar'] = True
            nombres_vistos[nombre_base]['warning_similar'] = True
        else:
            nombres_vistos[nombre_base] = asig_data
    
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
    
    # Aplicar filtros con django-filter - SOLO ASIGNATURAS DE UALP Y FILTRAR NOMBRES NUMÉRICOS
    try:
        ualp = UnidadAcademica.objects.get(id=1, nombre='UALP')
        # Filtrar asignaturas de UALP y excluir las que tienen nombres solo numéricos
        all_asignaturas = Asignatura.objects.filter(
            carrera__unidad_academica=ualp
        ).select_related('carrera', 'carrera__unidad_academica')
        
        # Filtrar las asignaturas problemáticas (nombres numéricos)
        asignaturas_validas = []
        for asig in all_asignaturas:
            if not asig.nombre.isdigit():  # Excluir nombres que sean solo números
                asignaturas_validas.append(asig.id)
        
        base_queryset = Asignatura.objects.filter(
            id__in=asignaturas_validas
        ).select_related('carrera', 'carrera__unidad_academica')
        
    except UnidadAcademica.DoesNotExist:
        base_queryset = Asignatura.objects.none()
    
    if categoria == 'asignaturas':
        # Usar AsignaturaFilter para filtrado automático solo con asignaturas de UALP
        filterset = AsignaturaFilter(request.GET, queryset=base_queryset)
        items = filterset.qs
    else:
        # Fallback para otras categorías
        filterset = None
        items = base_queryset
    
    # Paginación
    paginator = Paginator(items, 20)  # 20 elementos por página
    page_number = request.GET.get('page')
    items_page = paginator.get_page(page_number)
    
    # Estadísticas generales - SOLO DE UALP Y SIN ASIGNATURAS NUMÉRICAS
    try:
        ualp = UnidadAcademica.objects.get(id=1, nombre='UALP')
        # Filtrar asignaturas válidas para estadísticas
        asignaturas_ualp = Asignatura.objects.filter(carrera__unidad_academica=ualp)
        asignaturas_validas_ids = [asig.id for asig in asignaturas_ualp if not asig.nombre.isdigit()]
        
        stats = {
            'total_asignaturas': len(asignaturas_validas_ids),
            'total_criterios': CriterioDesempeno.objects.filter(asignatura__id__in=asignaturas_validas_ids).count(),
            'total_unidades_didacticas': UnidadDidactica.objects.filter(asignatura__id__in=asignaturas_validas_ids).count(),
            'total_contenidos': ContenidoAnalitico.objects.filter(unidad_didactica__asignatura__id__in=asignaturas_validas_ids).count(),
        }
    except UnidadAcademica.DoesNotExist:
        stats = {
            'total_asignaturas': 0,
            'total_criterios': 0,
            'total_unidades_didacticas': 0,
            'total_contenidos': 0,
        }
    
    # Asignaturas por carrera con datos de malla curricular - SOLO UALP
    carreras_con_malla = []
    # Solo mostrar carreras de UALP (ID=1) para pruebas
    try:
        ualp = UnidadAcademica.objects.get(id=1, nombre='UALP')
        carreras_ualp = Carrera.objects.filter(unidad_academica=ualp)
        
        for carrera in carreras_ualp:
            # Filtrar asignaturas excluyendo nombres numéricos
            all_asignaturas = Asignatura.objects.filter(carrera=carrera).order_by('semestre', 'nombre')
            asignaturas_validas_ids = [asig.id for asig in all_asignaturas if not asig.nombre.isdigit()]
            asignaturas = Asignatura.objects.filter(id__in=asignaturas_validas_ids).order_by('semestre', 'nombre')
            
            if asignaturas.exists():
                carreras_con_malla.append({
                    'carrera': carrera,
                    'asignaturas': asignaturas,
                    'total_asignaturas': asignaturas.count(),
                    'con_codigo_competencia': asignaturas.exclude(codigo_competencia__in=['', None]).count(),
                    'con_sigla_curricular': asignaturas.exclude(sigla_curricular__in=['', None]).count(),
                })
    except UnidadAcademica.DoesNotExist:
        pass  # Si no existe UALP, no mostrar carreras
    
    # Datos para filtros - SOLO UALP
    try:
        ualp = UnidadAcademica.objects.get(id=1, nombre='UALP')
        unidades_academicas = UnidadAcademica.objects.filter(id=1)  # Solo UALP
        carreras = Carrera.objects.filter(unidad_academica=ualp)    # Solo carreras de UALP
    except UnidadAcademica.DoesNotExist:
        unidades_academicas = UnidadAcademica.objects.none()
        carreras = Carrera.objects.none()
    
    context = {
        'stats': stats,
        'carreras_con_malla': carreras_con_malla,
        'unidades_academicas': unidades_academicas,
        'carreras': carreras,
        
        # Datos de paginación y filtros django-filter
        'asignaturas': items_page,  # Para compatibilidad con template existente
        'filterset': filterset,  # Para acceder a los filtros en el template
        'filtered_count': items.count(),  # Número de elementos filtrados
        'total_count': base_queryset.count(),  # Total sin filtros (solo UALP)
        'categoria': categoria,
        
        # Valores seleccionados para mantener en formulario
        'unidad_seleccionada': request.GET.get('unidad_academica', ''),
        'carrera_seleccionada': request.GET.get('carrera', ''),
        'semestre_seleccionado': request.GET.get('semestre', ''),
        'search_term': request.GET.get('search', ''),
        
        # Información de filtros para mostrar
        'has_filters': bool(request.GET and any(request.GET.values())),
        'show_filtered_results': bool(filterset and any(request.GET.values())),
    }
    
    return render(request, 'core/malla_curricular.html', context)


@login_required
def detalle_asignatura_view(request, asignatura_id):
    """Vista detallada mostrando las COMBINACIONES específicas creadas por el usuario"""
    
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    
    # Obtener todas las COMBINACIONES (contenidos analíticos) con sus componentes completos
    combinaciones = []
    
    # Cada contenido analítico es una "combinación" creada por el usuario
    # FILTRAR SOLO contenidos que tengan datos reales (no esqueletos vacíos)
    contenidos_analiticos = ContenidoAnalitico.objects.filter(
        unidad_didactica__asignatura=asignatura
    ).select_related('unidad_didactica').order_by('-created_at')  # Más recientes primero
    
    # Filtrar solo contenidos que tengan al menos algunos componentes reales
    contenidos_con_datos = []
    for contenido in contenidos_analiticos:
        tiene_datos = (
            Competencias.objects.filter(contenido_analitico=contenido).exists() or
            ObjetivoPractica.objects.filter(contenido_analitico=contenido).exists() or
            Procedimientos.objects.filter(contenido_analitico=contenido).exists() or
            MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido).exists() or
            FundamentoTeorico.objects.filter(contenido_analitico=contenido).exists() or
            CalculosResultados.objects.filter(contenido_analitico=contenido).exists() or
            Cuestionario.objects.filter(contenido_analitico=contenido).exists() or
            Bibliografia.objects.filter(contenido_analitico=contenido).exists() or
            Titulo.objects.filter(contenido_analitico=contenido).exists()
        )
        
        if tiene_datos:
            contenidos_con_datos.append(contenido)
    
    # Usar solo los contenidos que tienen datos reales
    contenidos_analiticos = contenidos_con_datos
    
    for indice, contenido in enumerate(contenidos_analiticos, 1):  # Enumerar desde 1
        # Para cada combinación, obtener TODOS sus componentes
        combinacion = {
            'id': contenido.id,  # ID real para URLs
            'numero_combinacion': indice,  # Número secuencial amigable
            'contenido_analitico': contenido,
            'unidad_didactica': contenido.unidad_didactica,
            
            # Todos los componentes de esta combinación específica
            'materiales_herramientas_equipos': MaterialesHerramientasEquipos.objects.filter(
                contenido_analitico=contenido
            ).order_by('tipo_elemento', 'orden'),
            
            'procedimientos': Procedimientos.objects.filter(
                contenido_analitico=contenido
            ).order_by('numero_paso'),
            
            'calculos_resultados': CalculosResultados.objects.filter(
                contenido_analitico=contenido
            ),
            
            'cuestionarios': Cuestionario.objects.filter(
                contenido_analitico=contenido
            ),
            
            'fundamentos_teoricos': FundamentoTeorico.objects.filter(
                contenido_analitico=contenido
            ),
            
            'objetivos_practica': ObjetivoPractica.objects.filter(
                contenido_analitico=contenido
            ),
            
            'bibliografia': Bibliografia.objects.filter(
                contenido_analitico=contenido
            ),
            
            # Campos adicionales para la vista simplificada
            'titulos': Titulo.objects.filter(
                contenido_analitico=contenido
            ).order_by('orden'),
            
            'competencias': Competencias.objects.filter(
                contenido_analitico=contenido
            ).order_by('orden'),
        }
        
        # Calcular estadísticas de esta combinación
        combinacion['stats'] = {
            'total_materiales': combinacion['materiales_herramientas_equipos'].filter(tipo_elemento='material').count(),
            'total_herramientas': combinacion['materiales_herramientas_equipos'].filter(tipo_elemento='herramienta').count(),
            'total_equipos': combinacion['materiales_herramientas_equipos'].filter(tipo_elemento='equipo').count(),
            'total_procedimientos': combinacion['procedimientos'].count(),
            'total_calculos': combinacion['calculos_resultados'].count(),
            'total_cuestionarios': combinacion['cuestionarios'].count(),
        }
        
        combinaciones.append(combinacion)
    
    # Estadísticas globales de todas las combinaciones
    total_combinaciones = len(combinaciones)
    total_componentes = sum(
        comb['stats']['total_materiales'] + 
        comb['stats']['total_herramientas'] + 
        comb['stats']['total_equipos'] + 
        comb['stats']['total_procedimientos']
        for comb in combinaciones
    )
    
    asignatura_stats = {
        'total_combinaciones': total_combinaciones,
        'total_componentes': total_componentes,
    }
    
    context = {
        'asignatura': asignatura,
        'combinaciones': combinaciones,  # Esta es la clave: las combinaciones específicas
        'asignatura_stats': asignatura_stats,
    }
    
    return render(request, 'core/detalle_asignatura.html', context)


@login_required
def detalle_combinacion_view(request, combinacion_id):
    """Vista detallada de una combinación específica con TODA la información completa"""
    
    # Obtener el contenido analítico (que representa la combinación)
    contenido_analitico = get_object_or_404(ContenidoAnalitico, id=combinacion_id)
    asignatura = contenido_analitico.unidad_didactica.asignatura
    carrera = asignatura.carrera
    unidad_academica = carrera.unidad_academica
    
    # Calcular el número secuencial de esta combinación
    todos_contenidos = ContenidoAnalitico.objects.filter(
        unidad_didactica__asignatura=asignatura
    ).order_by('unidad_didactica__nombre', 'nombre')
    
    numero_combinacion = 1
    for indice, contenido in enumerate(todos_contenidos, 1):
        if contenido.id == combinacion_id:
            numero_combinacion = indice
            break
    
    # Obtener el criterio de desempeño asociado
    criterio = CriterioDesempeno.objects.filter(asignatura=asignatura).first()
    
    # Obtener TODOS los componentes de esta combinación
    datos_combinacion = {
        # INFORMACIÓN ACADÉMICA
        'unidad_academica': unidad_academica,
        'carrera': carrera,
        
        # DATOS DE LA ASIGNATURA  
        'asignatura': asignatura,
        'criterio_desempeno': criterio,
        
        # UNIDAD DIDÁCTICA
        'unidad_didactica': contenido_analitico.unidad_didactica,
        
        # CONTENIDO ANALÍTICO
        'contenido_analitico': contenido_analitico,
        
        # GRUPOS DE DATOS ADICIONALES - Todos los componentes
        'bibliografia': Bibliografia.objects.filter(contenido_analitico=contenido_analitico),
        
        # PRÁCTICA DE LABORATORIO - Todos los componentes
        'titulo': contenido_analitico.nombre,  # El título viene del contenido analítico
        'titulos': Titulo.objects.filter(contenido_analitico=contenido_analitico).order_by('orden'),  # Títulos específicos de la práctica
        'competencias': Competencias.objects.filter(contenido_analitico=contenido_analitico),
        'objetivos_practica': ObjetivoPractica.objects.filter(contenido_analitico=contenido_analitico),
        'fundamentos_teoricos': FundamentoTeorico.objects.filter(contenido_analitico=contenido_analitico),
        'procedimientos': Procedimientos.objects.filter(contenido_analitico=contenido_analitico).order_by('numero_paso'),
        
        # RECURSOS (Equipos, Materiales, Herramientas)
        'equipos': MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido_analitico, tipo_elemento='equipo').order_by('orden'),
        'materiales': MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido_analitico, tipo_elemento='material').order_by('orden'),  
        'herramientas': MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido_analitico, tipo_elemento='herramienta').order_by('orden'),
        
        # CÁLCULOS Y RESULTADOS
        'calculos_resultados': CalculosResultados.objects.filter(contenido_analitico=contenido_analitico),
        
        # CUESTIONARIO
        'cuestionarios': Cuestionario.objects.filter(contenido_analitico=contenido_analitico),
    }
    
    context = {
        'combinacion_id': combinacion_id,
        'numero_combinacion': numero_combinacion,  # Número secuencial amigable
        'datos': datos_combinacion,
        'asignatura': asignatura,  # Para el breadcrumb
    }
    
    return render(request, 'core/detalle_combinacion.html', context)


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
        try:
            with transaction.atomic():
                # 1. Datos básicos de la asignatura
                unidad_academica_id = request.POST.get('unidad_academica')
                carrera_id = request.POST.get('carrera')
                
                # Validar que existan la unidad académica y carrera
                unidad_academica = get_object_or_404(UnidadAcademica, id=unidad_academica_id)
                carrera = get_object_or_404(Carrera, id=carrera_id)
                
                # VALIDACIÓN ESPECÍFICA: Verificar que es la unidad correcta (UALP)
                if unidad_academica.id != 1:  # Solo UALP permitida
                    messages.error(request, 
                        f"⚠️ ERROR: Solo se permite crear prácticas para UALP. "
                        f"Unidad seleccionada: {unidad_academica.nombre}")
                    return redirect('core:agregar_datos_malla')
                
                # 2. Obtener asignatura por ID (el formulario envía IDs, no nombres)
                asignatura_id = request.POST.get('asignatura')
                
                # Validar que la asignatura existe
                try:
                    asignatura = Asignatura.objects.get(id=asignatura_id)
                except Asignatura.DoesNotExist:
                    messages.error(request, f"🚨 ERROR: Asignatura con ID {asignatura_id} no encontrada.")
                    return redirect('core:agregar_datos_malla')
                
                # VALIDACIÓN CRÍTICA: Prevenir uso de asignaturas problemáticas por NOMBRE
                asignatura_nombre = asignatura.nombre
                if asignatura_nombre.isdigit() or len(asignatura_nombre.strip()) <= 3:
                    messages.error(request, 
                        f"🚨 ERROR CRÍTICO: No se permite crear prácticas en asignaturas con nombres "
                        f"problemáticos: '{asignatura_nombre}'. Por favor seleccione una asignatura "
                        f"con nombre descriptivo (ej: FISICA I, QUIMICA GENERAL).")
                    return redirect('core:agregar_datos_malla')
                
                # Lista negra de nombres problemáticos
                nombres_prohibidos = ['168', '169', '170', '171', '172', '173', '174', '175', '176', '177']
                if asignatura_nombre in nombres_prohibidos:
                    messages.error(request, 
                        f"🚨 ERROR: La asignatura '{asignatura_nombre}' está en la lista negra. "
                        f"Use el nombre completo (ej: FISICA I, QUIMICA GENERAL).")
                    return redirect('core:agregar_datos_malla')
                
                # 3. Actualizar datos de la asignatura existente
                asignatura.codigo_competencia = request.POST.get('codigo_competencia', '')
                asignatura.sigla_curricular = request.POST.get('sigla_curricular', '')
                asignatura.codigo_competencia = request.POST.get('codigo_competencia', '')
                asignatura.sigla_curricular = request.POST.get('sigla_curricular', '')
                asignatura.carga_horaria_semanal = int(request.POST.get('carga_horaria_semanal', 4))
                asignatura.carga_horaria_semestral = int(request.POST.get('carga_horaria_semestral', 80))
                asignatura.semestre = int(request.POST.get('semestre'))
                asignatura.save()
                created = False
                
                # Verificar si hay asignaturas similares que podrían confundir al usuario
                asignaturas_similares = Asignatura.objects.filter(
                    carrera=carrera,
                    semestre=asignatura.semestre
                ).exclude(id=asignatura.id)
                
                # 4. Obtener criterio de desempeño por ID (el formulario envía IDs)
                criterio_id = request.POST.get('criterio_desempeno', '').strip()
                if criterio_id:
                    try:
                        criterio = CriterioDesempeno.objects.get(id=criterio_id)
                    except CriterioDesempeno.DoesNotExist:
                        criterio = CriterioDesempeno.objects.create(
                            asignatura=asignatura,
                            nombre=f'Criterio {criterio_id}',
                            descripcion=f'Criterio de desempeño {criterio_id}'
                        )
                
                # 5. Obtener unidad didáctica por ID (el formulario envía IDs)
                unidad_didactica_id = request.POST.get('unidad_didactica', '').strip()
                if unidad_didactica_id:
                    try:
                        unidad_didactica = UnidadDidactica.objects.get(id=unidad_didactica_id)
                    except UnidadDidactica.DoesNotExist:
                        messages.error(request, f"🚨 ERROR: Unidad didáctica con ID {unidad_didactica_id} no encontrada.")
                        return redirect('core:agregar_datos_malla')
                    
                    # 6. CREAR NUEVA PRÁCTICA INDEPENDIENTE
                    # Obtener el título de la práctica (será el nombre del nuevo contenido analítico)
                    titulo_practica = request.POST.get('titulo_0_0', '').strip()
                    
                    if titulo_practica:
                        # Crear un nuevo ContenidoAnalitico con el título como nombre
                        contenido = ContenidoAnalitico.objects.create(
                            nombre=titulo_practica,
                            descripcion=f"Práctica de laboratorio: {titulo_practica}",
                            unidad_didactica=unidad_didactica
                        )
                        
                        # REGISTRO DE AUDITORÍA: Guardar información completa de la creación
                        try:
                            # Obtener información del request
                            ip_address = request.META.get('REMOTE_ADDR', '')
                            user_agent = request.META.get('HTTP_USER_AGENT', '')
                            
                            # Detectar asignaturas similares que podrían confundir
                            asignaturas_similares = list(Asignatura.objects.filter(
                                carrera=carrera,
                                semestre=asignatura.semestre
                            ).exclude(id=asignatura.id).values('id', 'nombre'))
                            
                            # Crear registro de auditoría
                            auditoria = AuditoriaCreacionPractica.objects.create(
                                usuario=request.user,
                                ip_address=ip_address,
                                user_agent=user_agent[:500],  # Truncar si es muy largo
                                
                                asignatura=asignatura,
                                asignatura_nombre=asignatura.nombre,
                                asignatura_id_usado=asignatura.id,
                                
                                contenido_analitico=contenido,
                                practica_nombre=contenido.nombre[:500],
                                
                                unidad_academica_nombre=unidad_academica.nombre,
                                carrera_nombre=carrera.get_nombre_display(),
                                semestre=asignatura.semestre,
                                
                                asignaturas_similares_detectadas=asignaturas_similares,
                                confirmacion_usuario=True  # Asumimos que pasó la validación JS
                            )
                            
                        except Exception as e:
                            # No interrumpir el proceso principal si falla la auditoría
                            pass
                        
                        # 7. Procesar datos adicionales para la nueva práctica (usando i=0)
                        i = 0  # Solo procesamos una práctica
                        grupo_index = 0
                        
                        # Procesar todos los campos del formulario (formato: campo_0_0)
                        campos_grupo = {
                            'bibliografia': request.POST.get(f'bibliografia_{i}_{grupo_index}', ''),
                            'practica_laboratorio': request.POST.get(f'practica_laboratorio_{i}_{grupo_index}', ''),
                            'titulo': request.POST.get(f'titulo_{i}_{grupo_index}', ''),
                            'competencias': request.POST.get(f'competencias_{i}_{grupo_index}', ''),
                            'objetivo_practica': request.POST.get(f'objetivo_practica_{i}_{grupo_index}', ''),
                            'fundamento_teorico': request.POST.get(f'fundamento_teorico_{i}_{grupo_index}', ''),
                            'procedimientos': request.POST.get(f'procedimientos_{i}_{grupo_index}', ''),
                            'calculos_resultados': request.POST.get(f'calculos_resultados_{i}_{grupo_index}', ''),
                            'cuestionario': request.POST.get(f'cuestionario_{i}_{grupo_index}', ''),
                        }
                        
                        # Procesar selecciones múltiples de recursos
                        try:
                            import json
                            equipos_seleccionados_json = request.POST.get(f'equipos_seleccionados_{i}_{grupo_index}', '[]')
                            materiales_seleccionados_json = request.POST.get(f'materiales_seleccionados_{i}_{grupo_index}', '[]')
                            herramientas_seleccionados_json = request.POST.get(f'herramientas_seleccionados_{i}_{grupo_index}', '[]')
                            
                            equipos_seleccionados = json.loads(equipos_seleccionados_json) if equipos_seleccionados_json else []
                            materiales_seleccionados = json.loads(materiales_seleccionados_json) if materiales_seleccionados_json else []
                            herramientas_seleccionados = json.loads(herramientas_seleccionados_json) if herramientas_seleccionados_json else []
                        except (json.JSONDecodeError, ValueError):
                            equipos_seleccionados = []
                            materiales_seleccionados = []
                            herramientas_seleccionados = []
                        
                        # Solo crear registros si hay contenido en al menos un campo
                        if any(valor.strip() for valor in campos_grupo.values()):
                            
                            # Crear bibliografía si existe
                            if campos_grupo['bibliografia'].strip():
                                Bibliografia.objects.create(
                                    contenido_analitico=contenido,
                                    titulo=campos_grupo['bibliografia'][:300],
                                    autor='No especificado',
                                    orden=grupo_index + 1
                                )
                            
                            # Crear práctica de laboratorio si existe
                            if campos_grupo['practica_laboratorio'].strip():
                                PracticaLaboratorio.objects.create(
                                    contenido_analitico=contenido,
                                    nombre=campos_grupo['practica_laboratorio'][:300],
                                    orden=grupo_index + 1
                                )
                            
                            # Crear título si existe
                            if campos_grupo['titulo'].strip():
                                Titulo.objects.create(
                                    contenido_analitico=contenido,
                                    texto=campos_grupo['titulo'][:300],
                                    orden=grupo_index + 1
                                )
                            
                            # Crear competencias si existe
                            if campos_grupo['competencias'].strip():
                                Competencias.objects.create(
                                    contenido_analitico=contenido,
                                    descripcion=campos_grupo['competencias'],
                                    orden=grupo_index + 1
                                )
                            
                            # Crear objetivo de práctica si existe
                            if campos_grupo['objetivo_practica'].strip():
                                ObjetivoPractica.objects.create(
                                    contenido_analitico=contenido,
                                    descripcion=campos_grupo['objetivo_practica'],
                                    orden=grupo_index + 1
                                )
                            
                            # Crear fundamento teórico si existe
                            if campos_grupo['fundamento_teorico'].strip():
                                FundamentoTeorico.objects.create(
                                    contenido_analitico=contenido,
                                    titulo=f'Fundamento {grupo_index + 1}',
                                    contenido=campos_grupo['fundamento_teorico'],
                                    orden=grupo_index + 1
                                )
                            
                            # Crear equipos seleccionados (múltiples)
                            orden_contador = 1
                            for equipo_nombre in equipos_seleccionados:
                                if equipo_nombre.strip():
                                    MaterialesHerramientasEquipos.objects.create(
                                        contenido_analitico=contenido,
                                        nombre=equipo_nombre[:200],
                                        tipo_elemento='equipo',
                                        cantidad='1',
                                        orden=(grupo_index * 100) + orden_contador
                                    )
                                    orden_contador += 1
                            
                            # Crear materiales seleccionados (múltiples)
                            for material_nombre in materiales_seleccionados:
                                if material_nombre.strip():
                                    MaterialesHerramientasEquipos.objects.create(
                                        contenido_analitico=contenido,
                                        nombre=material_nombre[:200],
                                        tipo_elemento='material',
                                        cantidad='1',
                                        orden=(grupo_index * 100) + orden_contador
                                    )
                                    orden_contador += 1
                            
                            # Crear herramientas seleccionadas (múltiples)
                            for herramienta_nombre in herramientas_seleccionados:
                                if herramienta_nombre.strip():
                                    MaterialesHerramientasEquipos.objects.create(
                                        contenido_analitico=contenido,
                                        nombre=herramienta_nombre[:200],
                                        tipo_elemento='herramienta',
                                        cantidad='1',
                                        orden=(grupo_index * 100) + orden_contador
                                    )
                                    orden_contador += 1
                            
                            # Crear procedimientos si existe
                            if campos_grupo['procedimientos'].strip():
                                Procedimientos.objects.create(
                                    contenido_analitico=contenido,
                                    numero_paso=grupo_index + 1,
                                    titulo_paso=f'Procedimiento {grupo_index + 1}',
                                    descripcion=campos_grupo['procedimientos'],
                                    orden=grupo_index + 1
                                )
                            
                            # Crear cálculos y resultados si existe
                            if campos_grupo['calculos_resultados'].strip():
                                CalculosResultados.objects.create(
                                    contenido_analitico=contenido,
                                    titulo=f'Cálculo {grupo_index + 1}',
                                    procedimiento_calculo=campos_grupo['calculos_resultados'],
                                    orden=grupo_index + 1
                                )
                            
                            # Crear cuestionario si existe
                            if campos_grupo['cuestionario'].strip():
                                Cuestionario.objects.create(
                                    contenido_analitico=contenido,
                                    numero_pregunta=grupo_index + 1,
                                    pregunta=campos_grupo['cuestionario'],
                                    orden=grupo_index + 1
                                )
                    
                    else:
                        messages.error(request, "⚠️ Por favor complete al menos el título de la práctica.")
                        return redirect('core:agregar_datos_malla')
                
                action_text = 'creada' if created else 'actualizada'
                messages.success(request, f'Asignatura "{asignatura}" {action_text} exitosamente con todos sus componentes.')
                return redirect('core:malla_curricular')
                
        except Exception as e:
            messages.error(request, f'Error al guardar los datos: {str(e)}')
            import traceback
            print(traceback.format_exc())  # Para debugging
    
    # GET request o error en POST
    context = {
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


# Vista de prueba para CKEditor 5
@login_required
def prueba_ckeditor_view(request):
    """Vista para probar CKEditor 5"""
    from .forms import FundamentoTeoricoForm
    
    fundamento = None
    
    if request.method == 'POST':
        form = FundamentoTeoricoForm(request.POST)
        if form.is_valid():
            # Crear un objeto temporal para mostrar
            fundamento = form.save(commit=False)
            # Como no tenemos contenido_analitico, vamos a crear uno temporal
            # o simplemente mostrar los datos
            print("Contenido:", form.cleaned_data['contenido'])
            print("Referencias:", form.cleaned_data['referencias'])
    else:
        form = FundamentoTeoricoForm()
    
    context = {
        'form': form,
        'fundamento': fundamento,
    }
    
    return render(request, 'core/prueba_ckeditor.html', context)


# =====================================
# VISTAS API PARA FILTROS EN CASCADA
# =====================================

@login_required
def get_asignaturas_por_carrera_ajax(request):
    """Obtener asignaturas filtradas por carrera"""
    carrera_id = request.GET.get('carrera_id')
    
    if carrera_id:
        asignaturas = Asignatura.objects.filter(carrera_id=carrera_id).order_by('semestre', 'nombre')
    else:
        asignaturas = Asignatura.objects.all()
    
    asignaturas_data = [
        {
            'id': asignatura.id, 
            'nombre': asignatura.get_nombre_display(),
            'semestre': asignatura.semestre,
            'codigo_competencia': asignatura.codigo_competencia or '',
            'sigla_curricular': asignatura.sigla_curricular or '',
            'carga_horaria_semestral': asignatura.carga_horaria_semestral,
            'carga_horaria_semanal': asignatura.carga_horaria_semanal
        }
        for asignatura in asignaturas
    ]
    
    return JsonResponse({'asignaturas': asignaturas_data})


@login_required
def get_criterios_desempeno_por_asignatura_ajax(request):
    """Obtener criterios de desempeño filtrados por asignatura"""
    asignatura_id = request.GET.get('asignatura_id')
    
    if asignatura_id:
        criterios = CriterioDesempeno.objects.filter(asignatura_id=asignatura_id).order_by('nombre')
    else:
        criterios = CriterioDesempeno.objects.all()
    
    criterios_data = [
        {
            'id': criterio.id, 
            'nombre': criterio.nombre,
            'descripcion': criterio.descripcion
        }
        for criterio in criterios
    ]
    
    return JsonResponse({'criterios': criterios_data})


@login_required
def get_unidades_didacticas_por_criterio_ajax(request):
    """Obtener unidades didácticas filtradas por criterio de desempeño"""
    criterio_id = request.GET.get('criterio_id')
    
    if criterio_id:
        # Obtener la asignatura del criterio
        try:
            criterio = CriterioDesempeno.objects.get(id=criterio_id)
            unidades = UnidadDidactica.objects.filter(asignatura=criterio.asignatura).order_by('nombre')
        except CriterioDesempeno.DoesNotExist:
            unidades = UnidadDidactica.objects.none()
    else:
        unidades = UnidadDidactica.objects.all()
    
    unidades_data = [
        {
            'id': unidad.id, 
            'nombre': unidad.nombre,
            'descripcion': unidad.descripcion
        }
        for unidad in unidades
    ]
    
    return JsonResponse({'unidades': unidades_data})


@login_required
def get_contenidos_analiticos_por_unidad_ajax(request):
    """Obtener contenidos analíticos filtrados por unidad didáctica"""
    unidad_id = request.GET.get('unidad_id')
    
    if unidad_id:
        contenidos = ContenidoAnalitico.objects.filter(unidad_didactica_id=unidad_id).order_by('nombre')
    else:
        contenidos = ContenidoAnalitico.objects.all()
    
    contenidos_data = [
        {
            'id': contenido.id, 
            'nombre': contenido.nombre,
            'descripcion': contenido.descripcion
        }
        for contenido in contenidos
    ]
    
    return JsonResponse({'contenidos': contenidos_data})


@login_required
def get_equipos_por_unidad_ajax(request):
    """Obtener equipos filtrados por unidad académica usando datos importados"""
    unidad_id = request.GET.get('unidad_id')
    
    try:
        from equipos.models import EquipoImportado
        from core.models import UnidadAcademica
        
        if unidad_id:
            # Obtener la unidad académica
            unidad = UnidadAcademica.objects.filter(id=unidad_id).first()
            if unidad:
                # Filtrar por el nombre de la unidad (UALP, UACB, etc.)
                equipos = EquipoImportado.objects.filter(
                    unidad_academica__icontains=unidad.nombre
                ).order_by('descripcion_activo')[:200]  # Limitar para rendimiento
            else:
                equipos = EquipoImportado.objects.all().order_by('descripcion_activo')[:200]
        else:
            # Si no hay unidad específica, mostrar todos (limitado)
            equipos = EquipoImportado.objects.all().order_by('descripcion_activo')[:200]
        
        # Obtener solo descripciones únicas para simplificar la selección
        descripciones_unicas = set()
        equipos_unicos = []
        
        for equipo in equipos:
            if equipo.descripcion_activo and equipo.descripcion_activo.strip():
                descripcion = equipo.descripcion_activo.strip()
                if descripcion not in descripciones_unicas:
                    descripciones_unicas.add(descripcion)
                    equipos_unicos.append({
                        'id': equipo.codigo,
                        'nombre': descripcion,
                        'descripcion': descripcion,
                        'codigo': equipo.codigo,
                        'responsable': equipo.responsable or '',
                        'estado': equipo.estado,
                        'oficina': equipo.oficina or ''
                    })
        
        equipos_data = equipos_unicos
        
    except ImportError:
        equipos_data = []
    
    return JsonResponse(equipos_data, safe=False)


@login_required
def get_insumos_por_unidad_ajax(request):
    """Obtener insumos filtrados por unidad académica y categoría"""
    unidad_id = request.GET.get('unidad_id')
    categoria = request.GET.get('categoria', '')  # Material, Herramienta, Reactivo
    
    try:
        from insumos.models import Insumo
        from core.models import UnidadAcademica
        
        if unidad_id:
            # Buscar insumos para la unidad académica seleccionada
            insumos = Insumo.objects.all()
            
            # Filtrar por categoría si se especifica
            if categoria == 'Material':
                insumos = insumos.filter(categoria='materiales')
            elif categoria == 'Herramienta':
                insumos = insumos.filter(categoria='herramientas')
            elif categoria == 'Reactivo':
                insumos = insumos.filter(categoria='reactivos')
                
            insumos = insumos.order_by('nombre_elemento')[:200]  # Limitar para rendimiento
            
            # Obtener solo nombres únicos para simplificar la selección
            nombres_unicos = set()
            insumos_unicos = []
            
            for insumo in insumos:
                if insumo.nombre_elemento and insumo.nombre_elemento.strip():
                    nombre = insumo.nombre_elemento.strip()
                    if nombre not in nombres_unicos:
                        nombres_unicos.add(nombre)
                        insumos_unicos.append({
                            'id': insumo.id,
                            'nombre': nombre,
                            'categoria': insumo.get_categoria_display(),
                            'marca': insumo.marca_modelo or '',
                            'estado': insumo.estado,
                            'descripcion': insumo.descripcion_caracteristicas or ''
                        })
            
            insumos_data = insumos_unicos
        else:
            # Si no hay unidad específica, devolver lista vacía
            insumos_data = []
            
    except ImportError:
        insumos_data = []
    
    return JsonResponse(insumos_data, safe=False)


@login_required
def agregar_equipo_rapido_ajax(request):
    """Agregar un nuevo equipo rápidamente"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        unidad_id = request.POST.get('unidad_id')
        marca = request.POST.get('marca', '')
        modelo = request.POST.get('modelo', '')
        
        if nombre and unidad_id:
            try:
                from equipos.models import Equipo
                from core.models import UnidadAcademica
                
                unidad = UnidadAcademica.objects.get(id=unidad_id)
                
                equipo = Equipo.objects.create(
                    nombre_equipo_existente=nombre,
                    unidad_academica=unidad,
                    marca=marca,
                    modelo=modelo,
                    estado='bueno',  # Estado por defecto
                    numero_unidades=1,  # Cantidad por defecto
                )
                
                return JsonResponse({
                    'success': True,
                    'equipo': {
                        'id': equipo.id,
                        'nombre': equipo.nombre_equipo_existente,
                        'marca': equipo.marca,
                        'modelo': equipo.modelo
                    }
                })
                
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': 'Datos incompletos'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def agregar_insumo_rapido_ajax(request):
    """Agregar un nuevo insumo rápidamente"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        unidad_id = request.POST.get('unidad_id')
        categoria = request.POST.get('categoria', 'materiales')
        marca = request.POST.get('marca', '')
        modelo = request.POST.get('modelo', '')
        
        if nombre and unidad_id:
            try:
                from insumos.models import Insumo
                from core.models import UnidadAcademica
                
                unidad = UnidadAcademica.objects.get(id=unidad_id)
                
                insumo = Insumo.objects.create(
                    nombre=nombre,
                    unidad_academica=unidad,
                    categoria=categoria,
                    marca=marca,
                    modelo=modelo,
                    estado='bueno',  # Estado por defecto
                    cantidad_total=1,  # Cantidad por defecto
                )
                
                return JsonResponse({
                    'success': True,
                    'insumo': {
                        'id': insumo.id,
                        'nombre': insumo.nombre,
                        'categoria': insumo.categoria,
                        'marca': insumo.marca,
                        'modelo': insumo.modelo
                    }
                })
                
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        return JsonResponse({'success': False, 'error': 'Datos incompletos'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# VISTAS AJAX PARA FILTROS EN CASCADA DE MALLA CURRICULAR

@login_required
def carreras_por_unidad_ajax(request):
    """Obtener carreras por unidad académica"""
    unidad_id = request.GET.get('unidad_id')
    
    if unidad_id:
        carreras = Carrera.objects.filter(unidad_academica_id=unidad_id).values('id', 'nombre')
        return JsonResponse({
            'success': True,
            'carreras': list(carreras)
        })
    
    return JsonResponse({'success': False, 'error': 'Unidad académica no especificada'})


@login_required 
def semestres_por_carrera_ajax(request):
    """Obtener semestres disponibles por carrera"""
    carrera_id = request.GET.get('carrera_id')
    
    if carrera_id:
        # Obtener semestres únicos de las asignaturas de esta carrera
        semestres = Asignatura.objects.filter(
            carrera_id=carrera_id
        ).values_list('semestre', flat=True).distinct().order_by('semestre')
        
        semestres_data = []
        for semestre in semestres:
            if semestre:  # Evitar valores None
                semestres_data.append({
                    'id': semestre,
                    'nombre': f'{semestre}° Semestre'
                })
        
        return JsonResponse({
            'success': True,
            'semestres': semestres_data
        })
    
    return JsonResponse({'success': False, 'error': 'Carrera no especificada'})


@login_required
def asignaturas_por_filtros_ajax(request):
    """Obtener asignaturas filtradas por unidad, carrera y semestre"""
    unidad_id = request.GET.get('unidad_id')
    carrera_id = request.GET.get('carrera_id') 
    semestre = request.GET.get('semestre')
    
    queryset = Asignatura.objects.all()
    
    if unidad_id:
        queryset = queryset.filter(carrera__unidad_academica_id=unidad_id)
    if carrera_id:
        queryset = queryset.filter(carrera_id=carrera_id)
    if semestre:
        queryset = queryset.filter(semestre=semestre)
    
    # Filtrar asignaturas válidas (sin nombres numéricos)
    asignaturas_data = []
    for asignatura in queryset.order_by('nombre'):
        if not asignatura.nombre.isdigit():
            asignaturas_data.append({
                'id': asignatura.id,
                'nombre': asignatura.nombre
            })
    
    return JsonResponse({
        'success': True,
        'asignaturas': asignaturas_data
    })


@login_required
def criterios_por_asignatura_ajax(request):
    """Obtener criterios de desempeño por asignatura"""
    asignatura_id = request.GET.get('asignatura_id')
    
    if asignatura_id:
        criterios = CriterioDesempeno.objects.filter(
            asignatura_id=asignatura_id
        ).values('id', 'descripcion').order_by('descripcion')
        
        return JsonResponse({
            'success': True,
            'criterios': list(criterios)
        })
    
    return JsonResponse({'success': False, 'error': 'Asignatura no especificada'})


@login_required
def unidades_didacticas_por_asignatura_ajax(request):
    """Obtener unidades didácticas por asignatura"""
    asignatura_id = request.GET.get('asignatura_id')
    
    if asignatura_id:
        unidades = UnidadDidactica.objects.filter(
            asignatura_id=asignatura_id
        ).values('id', 'nombre').order_by('nombre')
        
        return JsonResponse({
            'success': True,
            'unidades': list(unidades)
        })
    
    return JsonResponse({'success': False, 'error': 'Asignatura no especificada'})


@login_required
def contenidos_por_asignatura_ajax(request):
    """Obtener contenidos analíticos por asignatura"""
    asignatura_id = request.GET.get('asignatura_id')
    
    if asignatura_id:
        contenidos = ContenidoAnalitico.objects.filter(
            unidad_didactica__asignatura_id=asignatura_id
        ).select_related('unidad_didactica').values(
            'id', 'nombre', 'unidad_didactica__nombre'
        ).order_by('unidad_didactica__nombre', 'nombre')
        
        return JsonResponse({
            'success': True,
            'contenidos': list(contenidos)
        })
    
    return JsonResponse({'success': False, 'error': 'Asignatura no especificada'})
