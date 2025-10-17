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
    """Obtener asignaturas filtradas por carrera y semestre"""
    carrera_id = request.GET.get('carrera_id')
    semestre = request.GET.get('semestre')
    
    asignaturas = Asignatura.objects.all()
    
    if carrera_id:
        asignaturas = asignaturas.filter(carrera_id=carrera_id)
    
    if semestre:
        asignaturas = asignaturas.filter(semestre=semestre)
    
    asignaturas_data = []
    for asignatura in asignaturas:
        display_name = asignatura.get_nombre_display()
        
        # Si el display_name es igual al nombre y el nombre es numérico, usar un nombre más descriptivo
        if display_name == asignatura.nombre and asignatura.nombre.isdigit():
            print(f"Corrigiendo nombre problemático: {asignatura.nombre} -> descripción más clara")
            continue  # Omitir esta asignatura problemática
        
        asignaturas_data.append({
            'id': asignatura.id, 
            'nombre': asignatura.nombre, 
            'display': display_name,
            'semestre': asignatura.semestre,
            'carga_semanal': asignatura.carga_horaria_semanal,
            'carga_semestral': asignatura.carga_horaria_semestral,
            'codigo_competencia': asignatura.codigo_competencia or '',
            'sigla_curricular': asignatura.sigla_curricular or '',
            'carga_horaria_semestral': asignatura.carga_horaria_semestral,
            'carga_horaria_semanal': asignatura.carga_horaria_semanal
        })
    
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
        try:
            with transaction.atomic():
                # 1. Datos básicos de la asignatura
                unidad_academica_id = request.POST.get('unidad_academica')
                carrera_id = request.POST.get('carrera')
                
                # Validar que existan la unidad académica y carrera
                unidad_academica = get_object_or_404(UnidadAcademica, id=unidad_academica_id)
                carrera = get_object_or_404(Carrera, id=carrera_id)
                
                # 2. Crear o actualizar asignatura
                asignatura, created = Asignatura.objects.get_or_create(
                    nombre=request.POST.get('asignatura'),
                    carrera=carrera,
                    semestre=int(request.POST.get('semestre')),
                    defaults={
                        'codigo_competencia': request.POST.get('codigo_competencia', ''),
                        'sigla_curricular': request.POST.get('sigla_curricular', ''),
                        'carga_horaria_semanal': int(request.POST.get('carga_horaria_semanal', 4)),
                        'carga_horaria_semestral': int(request.POST.get('carga_horaria_semestral', 80)),
                    }
                )
                
                if not created:
                    # Si la asignatura ya existe, actualizar los campos
                    asignatura.codigo_competencia = request.POST.get('codigo_competencia', '')
                    asignatura.sigla_curricular = request.POST.get('sigla_curricular', '')
                    asignatura.carga_horaria_semanal = int(request.POST.get('carga_horaria_semanal', 4))
                    asignatura.carga_horaria_semestral = int(request.POST.get('carga_horaria_semestral', 80))
                    asignatura.save()
                
                # 3. Crear criterio de desempeño (único)
                criterio_desc = request.POST.get('criterio_desempeno', '').strip()
                if criterio_desc:
                    CriterioDesempeno.objects.update_or_create(
                        asignatura=asignatura,
                        defaults={
                            'nombre': criterio_desc[:200],
                            'descripcion': criterio_desc
                        }
                    )
                
                # 4. Crear unidad didáctica (única)
                unidad_didactica_nombre = request.POST.get('unidad_didactica', '').strip()
                if unidad_didactica_nombre:
                    unidad_didactica, _ = UnidadDidactica.objects.update_or_create(
                        asignatura=asignatura,
                        defaults={
                            'nombre': unidad_didactica_nombre[:200],
                            'descripcion': unidad_didactica_nombre
                        }
                    )
                    
                    # 5. Procesar contenidos analíticos (múltiples)
                    contenidos_nombres = request.POST.getlist('contenidos_analiticos[]')
                    
                    # Limpiar contenidos existentes para esta unidad
                    ContenidoAnalitico.objects.filter(unidad_didactica=unidad_didactica).delete()
                    
                    for i, contenido_nombre in enumerate(contenidos_nombres):
                        if contenido_nombre.strip():
                            contenido = ContenidoAnalitico.objects.create(
                                nombre=contenido_nombre[:300],
                                descripcion=contenido_nombre,
                                unidad_didactica=unidad_didactica
                            )
                            
                            # 6. Procesar grupos de datos adicionales para este contenido
                            # Buscar todos los campos que pertenecen a este contenido
                            grupo_index = 0
                            while True:
                                # Verificar si existe al menos un campo para este grupo
                                bibliografia_key = f'bibliografia_{i}_{grupo_index}'
                                if bibliografia_key not in request.POST:
                                    break
                                
                                # Procesar todos los campos del grupo
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
                                
                                # Procesar selecciones múltiples de recursos (nuevo formato)
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
                                
                                grupo_index += 1
                
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
    """Obtener equipos filtrados por unidad académica usando datos importados - SOLO UALP"""
    unidad_id = request.GET.get('unidad_id')
    
    try:
        from equipos.models import EquipoImportado
        from core.models import UnidadAcademica
        
        # SOLO permitir UALP (ID=1) para pruebas
        if unidad_id and unidad_id == '1':
            unidad = UnidadAcademica.objects.filter(id=unidad_id).first()
            if unidad and unidad.nombre == 'UALP':
                # Filtrar por el nombre de la unidad (UALP, UACB, etc.)
                equipos = EquipoImportado.objects.filter(
                    unidad_academica=unidad.nombre
                ).order_by('descripcion_activo')
            else:
                equipos = EquipoImportado.objects.none()
        else:
            # Si no hay unidad específica, mostrar todos
            equipos = EquipoImportado.objects.all().order_by('descripcion_activo')
        
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
        
        equipos_data = equipos_unicos[:100]  # Limitar a 100 para rendimiento
        
    except ImportError:
        equipos_data = []
    
    return JsonResponse(equipos_data, safe=False)


@login_required
def get_insumos_por_unidad_ajax(request):
    """Obtener insumos filtrados por unidad académica - SOLO UALP"""
    unidad_id = request.GET.get('unidad_id')
    categoria = request.GET.get('categoria', '')  # Material, Herramienta, etc.
    
    try:
        from insumos.models import Insumo
        from core.models import UnidadAcademica
        
        # SOLO permitir UALP (ID=1) para pruebas
        if unidad_id and unidad_id == '1':
            unidad = UnidadAcademica.objects.filter(id=unidad_id).first()
            if unidad and unidad.nombre == 'UALP':
                # Buscar insumos para cualquier unidad académica
                insumos = Insumo.objects.all()
                
                # Filtrar por categoría si se especifica
                if categoria == 'Material':
                    insumos = insumos.filter(categoria='materiales')
                elif categoria == 'Herramienta':
                    insumos = insumos.filter(categoria='herramientas')
                elif categoria == 'Reactivo':
                    insumos = insumos.filter(categoria='reactivos')
                    
                insumos = insumos.order_by('nombre_elemento')
                
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
                insumos_data = []
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
