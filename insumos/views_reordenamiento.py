from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.db import transaction

from .models import (
    Insumo, TareaReordenamientoInsumo, InsumoTarea, LogReordenamientoInsumo
)
from core.models import UnidadAcademica, Carrera, Laboratorio
from django.contrib.auth import get_user_model

User = get_user_model()


# ================================
# VISTAS DE REORDENAMIENTO DE INSUMOS
# ================================

@login_required
def lista_tareas_reordenamiento_insumos(request):
    """Vista principal para mostrar la lista de tareas de reordenamiento de insumos"""
    
    # Obtener filtros
    filtros = {
        'estado': request.GET.get('estado', ''),
        'tipo': request.GET.get('tipo', ''),
        'prioridad': request.GET.get('prioridad', ''),
        'usuario_asignado': request.GET.get('usuario_asignado', ''),
        'busqueda': request.GET.get('busqueda', ''),
    }
    
    # Construir queryset con filtros
    tareas = TareaReordenamientoInsumo.objects.select_related('usuario_creador', 'usuario_asignado')
    
    if filtros['estado']:
        tareas = tareas.filter(estado=filtros['estado'])
    
    if filtros['tipo']:
        tareas = tareas.filter(tipo=filtros['tipo'])
    
    if filtros['prioridad']:
        tareas = tareas.filter(prioridad=filtros['prioridad'])
    
    if filtros['usuario_asignado']:
        tareas = tareas.filter(usuario_asignado_id=filtros['usuario_asignado'])
    
    if filtros['busqueda']:
        tareas = tareas.filter(
            Q(titulo__icontains=filtros['busqueda']) |
            Q(descripcion__icontains=filtros['busqueda'])
        )
    
    # Paginación
    paginator = Paginator(tareas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    stats = {
        'total': TareaReordenamientoInsumo.objects.count(),
        'pendientes': TareaReordenamientoInsumo.objects.filter(estado='pendiente').count(),
        'en_proceso': TareaReordenamientoInsumo.objects.filter(estado='en_proceso').count(),
        'completadas': TareaReordenamientoInsumo.objects.filter(estado='completada').count(),
    }
    
    # Obtener usuarios para el filtro
    usuarios = User.objects.filter(tareas_insumos_asignadas__isnull=False).distinct()
    
    context = {
        'tareas': page_obj,
        'filtros': filtros,
        'stats': stats,
        'tipos_tarea': TareaReordenamientoInsumo.TIPOS_TAREA,
        'estados_tarea': TareaReordenamientoInsumo.ESTADOS_TAREA,
        'prioridades': TareaReordenamientoInsumo.PRIORIDADES,
        'usuarios': usuarios,
    }
    
    return render(request, 'insumos/reordenamiento/lista_tareas.html', context)


@login_required
def nueva_tarea_reordenamiento_insumos(request):
    """Vista para crear una nueva tarea de reordenamiento de insumos"""
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Crear la tarea
                tarea = TareaReordenamientoInsumo.objects.create(
                    titulo=request.POST.get('titulo'),
                    descripcion=request.POST.get('descripcion'),
                    tipo=request.POST.get('tipo'),
                    prioridad=request.POST.get('prioridad'),
                    fecha_fin_estimada=request.POST.get('fecha_fin_estimada') or None,
                    usuario_creador=request.user,
                    usuario_asignado_id=request.POST.get('usuario_asignado') or None,
                    observaciones=request.POST.get('observaciones', ''),
                )
                
                # Procesar insumos seleccionados
                insumos_seleccionados = request.POST.getlist('insumos_seleccionados')
                insumos_procesados = 0
                
                for insumo_id in insumos_seleccionados:
                    try:
                        insumo = Insumo.objects.get(id=int(insumo_id))
                        InsumoTarea.objects.create(
                            tarea=tarea,
                            insumo=insumo,
                            unidad_academica_original=insumo.unidad_academica,
                            carrera_original=insumo.carrera,
                            laboratorio_original=insumo.laboratorio,
                            categoria_original=insumo.categoria,
                            observaciones_procesamiento=''
                        )
                        insumos_procesados += 1
                    except (Insumo.DoesNotExist, ValueError) as e:
                        continue
                
                # Registrar log de creación
                LogReordenamientoInsumo.objects.create(
                    tarea=tarea,
                    usuario=request.user,
                    accion="Tarea creada",
                    descripcion=f"Nueva tarea de reordenamiento creada con {insumos_procesados} insumos"
                )
                
                messages.success(request, f'Tarea de reordenamiento creada correctamente con {insumos_procesados} insumos.')
                return redirect('insumos:detalle_tarea_reordenamiento', pk=tarea.pk)
                
        except Exception as e:
            messages.error(request, f'Error al crear la tarea: {str(e)}')
    
    # Datos para el formulario
    usuarios = User.objects.filter(is_active=True).order_by('username')
    unidades_academicas = UnidadAcademica.objects.all().order_by('nombre')
    
    context = {
        'tipos_tarea': TareaReordenamientoInsumo.TIPOS_TAREA,
        'prioridades': TareaReordenamientoInsumo.PRIORIDADES,
        'usuarios': usuarios,
        'unidades_academicas': unidades_academicas,
    }
    
    return render(request, 'insumos/reordenamiento/nueva_tarea.html', context)


@login_required
def detalle_tarea_reordenamiento_insumos(request, pk):
    """Vista para mostrar los detalles de una tarea de reordenamiento"""
    
    tarea = get_object_or_404(TareaReordenamientoInsumo, pk=pk)
    
    # Obtener insumos asociados
    insumos_tarea = InsumoTarea.objects.filter(tarea=tarea).select_related('insumo')
    
    # Obtener logs de la tarea
    logs = LogReordenamientoInsumo.objects.filter(tarea=tarea).select_related('usuario')[:10]
    
    context = {
        'tarea': tarea,
        'insumos_tarea': insumos_tarea,
        'logs': logs,
    }
    
    return render(request, 'insumos/reordenamiento/detalle_tarea.html', context)


@login_required
def editar_tarea_reordenamiento_insumos(request, pk):
    """Vista para editar una tarea de reordenamiento"""
    
    tarea = get_object_or_404(TareaReordenamientoInsumo, pk=pk)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Guardar datos anteriores para el log
                datos_anteriores = {
                    'titulo': tarea.titulo,
                    'estado': tarea.estado,
                    'prioridad': tarea.prioridad,
                }
                
                # Actualizar la tarea
                tarea.titulo = request.POST.get('titulo')
                tarea.descripcion = request.POST.get('descripcion')
                tarea.tipo = request.POST.get('tipo')
                tarea.estado = request.POST.get('estado')
                tarea.prioridad = request.POST.get('prioridad')
                tarea.fecha_fin_estimada = request.POST.get('fecha_fin_estimada') or None
                tarea.usuario_asignado_id = request.POST.get('usuario_asignado') or None
                tarea.observaciones = request.POST.get('observaciones', '')
                tarea.porcentaje_completado = int(request.POST.get('porcentaje_completado', 0))
                
                # Si se marca como completada, establecer fecha fin real
                if tarea.estado == 'completada' and not tarea.fecha_fin_real:
                    tarea.fecha_fin_real = timezone.now()
                
                # Si se inicia, establecer fecha de inicio
                if tarea.estado == 'en_proceso' and not tarea.fecha_inicio:
                    tarea.fecha_inicio = timezone.now()
                
                tarea.save()
                
                # Registrar cambios en el log
                cambios = []
                if datos_anteriores['titulo'] != tarea.titulo:
                    cambios.append(f"Título: '{datos_anteriores['titulo']}' → '{tarea.titulo}'")
                if datos_anteriores['estado'] != tarea.estado:
                    cambios.append(f"Estado: '{datos_anteriores['estado']}' → '{tarea.estado}'")
                if datos_anteriores['prioridad'] != tarea.prioridad:
                    cambios.append(f"Prioridad: '{datos_anteriores['prioridad']}' → '{tarea.prioridad}'")
                
                if cambios:
                    LogReordenamientoInsumo.objects.create(
                        tarea=tarea,
                        usuario=request.user,
                        accion="Tarea editada",
                        descripcion=f"Cambios realizados: {'; '.join(cambios)}"
                    )
                
                messages.success(request, f'Tarea "{tarea.titulo}" actualizada exitosamente.')
                return redirect('insumos:detalle_tarea_reordenamiento', pk=tarea.pk)
                
        except Exception as e:
            messages.error(request, f'Error al actualizar la tarea: {str(e)}')
    
    # Datos para el formulario
    usuarios = User.objects.filter(is_active=True).order_by('username')
    unidades_academicas = UnidadAcademica.objects.all().order_by('nombre')
    
    # Obtener insumos asociados a la tarea
    insumos_tarea = InsumoTarea.objects.filter(tarea=tarea).select_related('insumo', 'insumo__unidad_academica')
    
    # Intentar obtener unidad académica desde los insumos o usar la primera disponible
    unidad = None
    if insumos_tarea.exists():
        # Obtener la unidad del primer insumo
        primer_insumo = insumos_tarea.first()
        if primer_insumo.insumo.unidad_academica:
            unidad = primer_insumo.insumo.unidad_academica
    
    # Si no hay unidad desde insumos, usar la primera disponible
    if not unidad and unidades_academicas.exists():
        unidad = unidades_academicas.first()
    
    context = {
        'tarea': tarea,
        'tipos_tarea': TareaReordenamientoInsumo.TIPOS_TAREA,
        'estados_tarea': TareaReordenamientoInsumo.ESTADOS_TAREA,
        'prioridades': TareaReordenamientoInsumo.PRIORIDADES,
        'usuarios': usuarios,
        'unidades_academicas': unidades_academicas,
        'insumos_tarea': insumos_tarea,
        'unidad': unidad,  # Agregar la unidad al contexto
    }
    
    return render(request, 'insumos/reordenamiento/editar_tarea.html', context)


@login_required
def eliminar_tarea_reordenamiento_insumos(request, pk):
    """Vista para eliminar una tarea de reordenamiento"""
    
    tarea = get_object_or_404(TareaReordenamientoInsumo, pk=pk)
    
    if request.method == 'POST':
        titulo_tarea = tarea.titulo
        tarea.delete()
        messages.success(request, f'Tarea "{titulo_tarea}" eliminada exitosamente.')
        return redirect('insumos:reordenamiento_insumos')
    
    context = {'tarea': tarea}
    return render(request, 'insumos/reordenamiento/eliminar_tarea.html', context)


@login_required
def buscar_insumos_reordenamiento(request):
    """API para buscar insumos disponibles para reordenamiento"""
    
    search = request.GET.get('search', '').strip()
    unidad_id = request.GET.get('unidad_academica', '')
    carrera_id = request.GET.get('carrera', '')
    laboratorio_id = request.GET.get('laboratorio', '')
    categoria = request.GET.get('categoria', '')
    
    # Construir queryset
    insumos = Insumo.objects.select_related(
        'unidad_academica', 'carrera', 'laboratorio'
    )
    
    # Aplicar filtros
    if search:
        insumos = insumos.filter(
            Q(nombre_elemento__icontains=search) |
            Q(marca__icontains=search) |
            Q(descripcion__icontains=search)
        )
    
    if unidad_id:
        insumos = insumos.filter(unidad_academica_id=unidad_id)
    
    if carrera_id:
        insumos = insumos.filter(carrera_id=carrera_id)
    
    if laboratorio_id:
        insumos = insumos.filter(laboratorio_id=laboratorio_id)
    
    if categoria:
        insumos = insumos.filter(categoria=categoria)
    
    # Limitar resultados
    insumos = insumos[:20]
    
    # Preparar respuesta JSON
    data = {
        'insumos': [
            {
                'id': insumo.id,
                'nombre': insumo.nombre_elemento,
                'marca': insumo.marca or '',
                'categoria': insumo.get_categoria_display(),
                'unidad_academica': insumo.unidad_academica.nombre if insumo.unidad_academica else '',
                'carrera': insumo.carrera.nombre if insumo.carrera else '',
                'laboratorio': insumo.laboratorio.get_nombre_display() if insumo.laboratorio else '',
                'stock_actual': insumo.stock_actual,
                'estado': insumo.get_estado_display(),
            }
            for insumo in insumos
        ]
    }
    
    return JsonResponse(data)


@login_required
def agregar_insumos_tarea(request, pk):
    """Vista para agregar insumos a una tarea de reordenamiento"""
    
    tarea = get_object_or_404(TareaReordenamientoInsumo, pk=pk)
    
    if request.method == 'POST':
        try:
            insumos_ids = request.POST.getlist('insumos_seleccionados')
            insumos_agregados = 0
            
            with transaction.atomic():
                for insumo_id in insumos_ids:
                    insumo = get_object_or_404(Insumo, pk=insumo_id)
                    
                    # Verificar si ya está en la tarea
                    if not InsumoTarea.objects.filter(tarea=tarea, insumo=insumo).exists():
                        InsumoTarea.objects.create(
                            tarea=tarea,
                            insumo=insumo,
                            unidad_academica_original=insumo.unidad_academica,
                            carrera_original=insumo.carrera,
                            laboratorio_original=insumo.laboratorio,
                            categoria_original=insumo.categoria,
                        )
                        insumos_agregados += 1
                
                # Registrar log
                if insumos_agregados > 0:
                    LogReordenamientoInsumo.objects.create(
                        tarea=tarea,
                        usuario=request.user,
                        accion="Insumos agregados",
                        descripcion=f"Se agregaron {insumos_agregados} insumos a la tarea"
                    )
            
            messages.success(request, f'{insumos_agregados} insumos agregados a la tarea.')
            
        except Exception as e:
            messages.error(request, f'Error al agregar insumos: {str(e)}')
    
    return redirect('insumos:detalle_tarea_reordenamiento', pk=pk)


@login_required
def procesar_tarea_reordenamiento_insumos(request, pk):
    """Vista para procesar (ejecutar) una tarea de reordenamiento"""
    
    tarea = get_object_or_404(TareaReordenamientoInsumo, pk=pk)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                insumos_procesados = 0
                errores = []
                
                # Obtener todos los insumos de la tarea que no han sido procesados
                insumos_tarea = InsumoTarea.objects.filter(
                    tarea=tarea, 
                    procesado=False
                ).select_related('insumo')
                
                for insumo_tarea in insumos_tarea:
                    try:
                        insumo = insumo_tarea.insumo
                        
                        # Aplicar cambios según el tipo de tarea
                        if insumo_tarea.unidad_academica_objetivo:
                            insumo.unidad_academica = insumo_tarea.unidad_academica_objetivo
                        
                        if insumo_tarea.carrera_objetivo:
                            insumo.carrera = insumo_tarea.carrera_objetivo
                        
                        if insumo_tarea.laboratorio_objetivo:
                            insumo.laboratorio = insumo_tarea.laboratorio_objetivo
                        
                        if insumo_tarea.categoria_objetivo:
                            insumo.categoria = insumo_tarea.categoria_objetivo
                        
                        insumo.save()
                        
                        # Marcar como procesado
                        insumo_tarea.procesado = True
                        insumo_tarea.fecha_procesamiento = timezone.now()
                        insumo_tarea.save()
                        
                        insumos_procesados += 1
                        
                    except Exception as e:
                        errores.append(f"Error con {insumo.nombre_elemento}: {str(e)}")
                
                # Actualizar estado de la tarea si todos los insumos fueron procesados
                if insumos_procesados > 0:
                    if not InsumoTarea.objects.filter(tarea=tarea, procesado=False).exists():
                        tarea.estado = 'completada'
                        tarea.fecha_fin_real = timezone.now()
                        tarea.porcentaje_completado = 100
                    else:
                        tarea.estado = 'en_proceso'
                        # Calcular porcentaje
                        total = InsumoTarea.objects.filter(tarea=tarea).count()
                        procesados = InsumoTarea.objects.filter(tarea=tarea, procesado=True).count()
                        tarea.porcentaje_completado = int((procesados / total) * 100)
                    
                    tarea.save()
                    
                    # Registrar log
                    LogReordenamientoInsumo.objects.create(
                        tarea=tarea,
                        usuario=request.user,
                        accion="Tarea procesada",
                        descripcion=f"Se procesaron {insumos_procesados} insumos exitosamente"
                    )
                
                if errores:
                    messages.warning(request, f'Procesados: {insumos_procesados}. Errores: {len(errores)}')
                else:
                    messages.success(request, f'{insumos_procesados} insumos procesados exitosamente.')
                
        except Exception as e:
            messages.error(request, f'Error al procesar la tarea: {str(e)}')
    
    return redirect('insumos:detalle_tarea_reordenamiento', pk=pk)


@login_required
def api_insumos_disponibles(request):
    """API para obtener insumos disponibles para reordenamiento con filtros"""
    
    from django.http import JsonResponse
    from django.db.models import Q
    
    try:
        # Obtener parámetros de filtro
        search = request.GET.get('search', '').strip()
        unidad_academica = request.GET.get('unidad_academica', '')
        laboratorio = request.GET.get('laboratorio', '')
        categoria = request.GET.get('categoria', '')
        estado = request.GET.get('estado', '')
        
        # Consulta base
        insumos = Insumo.objects.select_related(
            'unidad_academica',
            'laboratorio'
        ).all()
        
        # Aplicar filtros
        if search:
            insumos = insumos.filter(
                Q(nombre_elemento__icontains=search) |
                Q(codigo_inventario__icontains=search) |
                Q(marca_modelo__icontains=search) |
                Q(descripcion_caracteristicas__icontains=search)
            )
        
        if unidad_academica:
            insumos = insumos.filter(unidad_academica_id=unidad_academica)
        
        if laboratorio:
            insumos = insumos.filter(laboratorio_id=laboratorio)
        
        if categoria:
            # Mapear categorías según el modelo Insumo
            categoria_mapping = {
                'reactivos': 'reactivos',
                'materiales': 'materiales',
                'herramientas': 'herramientas'
            }
            if categoria in categoria_mapping:
                insumos = insumos.filter(categoria=categoria_mapping[categoria])
        
        if estado:
            insumos = insumos.filter(estado=estado)
        
        # Limitar resultados
        insumos = insumos[:100]
        
        # Serializar datos
        insumos_data = []
        for insumo in insumos:
            insumos_data.append({
                'id': insumo.id,
                'codigo_inventario': insumo.codigo_inventario or '',
                'nombre_elemento': insumo.nombre_elemento,
                'marca_modelo': insumo.marca_modelo or '',
                'estado': insumo.estado,
                'unidad_academica': insumo.unidad_academica.nombre if insumo.unidad_academica else '',
                'laboratorio': insumo.laboratorio.get_nombre_display() if insumo.laboratorio else '',
                'descripcion_caracteristicas': insumo.descripcion_caracteristicas or ''
            })
        
        return JsonResponse({
            'success': True,
            'insumos': insumos_data,
            'count': len(insumos_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_insumos_disponibles_por_unidad(request, unidad_id):
    """API para obtener insumos disponibles por unidad académica con filtros"""
    
    from django.http import JsonResponse
    from django.db.models import Q
    from core.models import UnidadAcademica
    
    try:
        # Verificar que la unidad existe
        unidad = get_object_or_404(UnidadAcademica, pk=unidad_id)
        
        # Obtener parámetros de filtro
        busqueda = request.GET.get('busqueda', '').strip()
        laboratorio_id = request.GET.get('laboratorio_id', '')
        
        # Consulta base - insumos de la unidad
        insumos = Insumo.objects.select_related(
            'unidad_academica',
            'laboratorio'
        ).filter(unidad_academica=unidad)
        
        # Aplicar filtros
        if busqueda:
            insumos = insumos.filter(
                Q(nombre_elemento__icontains=busqueda) |
                Q(descripcion_caracteristicas__icontains=busqueda) |
                Q(codigo_inventario__icontains=busqueda)
            )
        
        if laboratorio_id:
            insumos = insumos.filter(laboratorio_id=laboratorio_id)
        
        # Limitar resultados
        insumos = insumos.order_by('nombre_elemento')[:100]
        
        # Serializar datos
        insumos_data = []
        for insumo in insumos:
            try:
                insumos_data.append({
                    'id': insumo.id,
                    'nombre': insumo.nombre_elemento,
                    'descripcion': insumo.descripcion_caracteristicas or '',
                    'codigo': insumo.codigo_inventario or '',
                    'cantidad': getattr(insumo, 'cantidad', 0),
                    'unidad_medida': getattr(insumo, 'unidad_medida', ''),
                    'categoria_nombre': insumo.get_categoria_display(),
                    'laboratorio_nombre': insumo.laboratorio.get_nombre_display() if insumo.laboratorio else 'Sin laboratorio',
                    'unidad_academica_nombre': insumo.unidad_academica.nombre if insumo.unidad_academica else ''
                })
            except Exception as item_error:
                # Log del error individual pero continuar con otros insumos
                print(f"Error procesando insumo {insumo.id}: {str(item_error)}")
                continue
        
        return JsonResponse(insumos_data, safe=False)
        
    except Exception as e:
        print(f"Error en api_insumos_disponibles_por_unidad: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_laboratorios_por_unidad(request, unidad_id):
    """API para obtener laboratorios disponibles (todos los laboratorios)"""
    
    from django.http import JsonResponse
    from core.models import Laboratorio
    
    try:
        # En este modelo, los laboratorios son un catálogo general
        # por lo tanto devolvemos todos los laboratorios disponibles
        laboratorios = Laboratorio.objects.all().values('id', 'nombre')
        
        laboratorios_data = []
        for lab in laboratorios:
            laboratorio_obj = Laboratorio.objects.get(id=lab['id'])
            laboratorios_data.append({
                'id': lab['id'],
                'nombre': laboratorio_obj.get_nombre_display()
            })
        
        return JsonResponse({
            'success': True,
            'laboratorios': laboratorios_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_procesar_insumo_individual(request, insumo_tarea_id):
    """API para procesar un insumo individual"""
    
    from django.http import JsonResponse
    from django.utils import timezone
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        with transaction.atomic():
            insumo_tarea = get_object_or_404(InsumoTarea, pk=insumo_tarea_id)
            
            if insumo_tarea.procesado:
                return JsonResponse({
                    'success': False,
                    'error': 'Este insumo ya ha sido procesado'
                })
            
            # Marcar como procesado
            insumo_tarea.procesado = True
            insumo_tarea.fecha_procesado = timezone.now()
            insumo_tarea.save()
            
            # Actualizar progreso de la tarea
            tarea = insumo_tarea.tarea
            total = InsumoTarea.objects.filter(tarea=tarea).count()
            procesados = InsumoTarea.objects.filter(tarea=tarea, procesado=True).count()
            
            if total > 0:
                tarea.porcentaje_completado = int((procesados / total) * 100)
                tarea.save()
            
            # Registrar log
            LogReordenamientoInsumo.objects.create(
                tarea=tarea,
                usuario=request.user,
                accion="Insumo procesado",
                descripcion=f"Procesado insumo: {insumo_tarea.insumo.nombre_elemento}"
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Insumo procesado correctamente'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_procesar_todos_insumos(request, pk):
    """API para procesar todos los insumos de una tarea"""
    
    from django.http import JsonResponse
    from django.utils import timezone
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        with transaction.atomic():
            tarea = get_object_or_404(TareaReordenamientoInsumo, pk=pk)
            
            # Procesar todos los insumos pendientes
            insumos_pendientes = InsumoTarea.objects.filter(
                tarea=tarea,
                procesado=False
            )
            
            procesados = 0
            for insumo_tarea in insumos_pendientes:
                insumo_tarea.procesado = True
                insumo_tarea.fecha_procesado = timezone.now()
                insumo_tarea.save()
                procesados += 1
            
            # Actualizar progreso de la tarea
            tarea.porcentaje_completado = 100
            tarea.save()
            
            # Registrar log
            LogReordenamientoInsumo.objects.create(
                tarea=tarea,
                usuario=request.user,
                accion="Procesamiento masivo",
                descripcion=f"Se procesaron {procesados} insumos masivamente"
            )
            
            return JsonResponse({
                'success': True,
                'procesados': procesados,
                'message': f'{procesados} insumos procesados correctamente'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_completar_tarea(request, pk):
    """API para marcar una tarea como completada"""
    
    from django.http import JsonResponse
    from django.utils import timezone
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        with transaction.atomic():
            tarea = get_object_or_404(TareaReordenamientoInsumo, pk=pk)
            
            if tarea.estado == 'completada':
                return JsonResponse({
                    'success': False,
                    'error': 'Esta tarea ya está completada'
                })
            
            # Marcar como completada
            tarea.estado = 'completada'
            tarea.fecha_fin_real = timezone.now()
            tarea.porcentaje_completado = 100
            tarea.save()
            
            # Registrar log
            LogReordenamientoInsumo.objects.create(
                tarea=tarea,
                usuario=request.user,
                accion="Tarea completada",
                descripcion="Tarea marcada como completada manualmente"
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Tarea completada correctamente'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_detalle_insumo_tarea(request, insumo_tarea_id):
    """API para obtener detalles de un insumo en una tarea"""
    
    from django.http import JsonResponse
    from django.template.loader import render_to_string
    
    try:
        insumo_tarea = get_object_or_404(InsumoTarea, pk=insumo_tarea_id)
        
        # Generar HTML con los detalles
        context = {
            'insumo_tarea': insumo_tarea,
            'insumo': insumo_tarea.insumo
        }
        
        html = render_to_string('insumos/reordenamiento/detalle_insumo_modal.html', context)
        
        return JsonResponse({
            'success': True,
            'html': html
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ================================
# VISTAS DE API PARA EDICIÓN DE INSUMOS EN TAREAS
# ================================

@login_required
def api_agregar_insumos_tarea(request, tarea_id):
    """API para agregar insumos a una tarea existente"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        import json
        
        tarea = get_object_or_404(TareaReordenamientoInsumo, pk=tarea_id)
        data = json.loads(request.body)
        insumos_ids = data.get('insumos_ids', [])
        
        if not insumos_ids:
            return JsonResponse({'success': False, 'error': 'No se proporcionaron insumos'})
        
        # Validar que los insumos existen y no están ya en la tarea
        insumos = Insumo.objects.filter(id__in=insumos_ids)
        insumos_existentes = InsumoTarea.objects.filter(
            tarea=tarea,
            insumo__in=insumos
        ).values_list('insumo_id', flat=True)
        
        insumos_a_agregar = insumos.exclude(id__in=insumos_existentes)
        
        # Crear las relaciones InsumoTarea
        with transaction.atomic():
            for insumo in insumos_a_agregar:
                InsumoTarea.objects.create(
                    tarea=tarea,
                    insumo=insumo,
                    unidad_academica_original=insumo.unidad_academica,
                    carrera_original=insumo.carrera,
                    laboratorio_original=insumo.laboratorio,
                    categoria_original=insumo.categoria,
                    procesado=False
                )
            
            # Registrar en el log
            LogReordenamientoInsumo.objects.create(
                tarea=tarea,
                usuario=request.user,
                accion='insumos_agregados',
                descripcion=f'Se agregaron {len(insumos_a_agregar)} insumos a la tarea'
            )
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Se agregaron {len(insumos_a_agregar)} insumos correctamente',
            'total_agregados': len(insumos_a_agregar),
            'ya_existentes': len(insumos_existentes)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al agregar insumos: {str(e)}'
        }, status=500)


@login_required
def api_remover_insumo_tarea(request, tarea_id, insumo_tarea_id):
    """API para remover un insumo de una tarea"""
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        tarea = get_object_or_404(TareaReordenamientoInsumo, pk=tarea_id)
        insumo_tarea = get_object_or_404(InsumoTarea, pk=insumo_tarea_id, tarea=tarea)
        
        # Verificar que no esté procesado
        if insumo_tarea.procesado:
            return JsonResponse({
                'success': False,
                'error': 'No se puede remover un insumo que ya ha sido procesado'
            })
        
        insumo_nombre = insumo_tarea.insumo.nombre_elemento
        
        with transaction.atomic():
            # Eliminar la relación
            insumo_tarea.delete()
            
            # Registrar en el log
            LogReordenamientoInsumo.objects.create(
                tarea=tarea,
                usuario=request.user,
                accion='insumo_removido',
                descripcion=f'Se removió el insumo "{insumo_nombre}" de la tarea'
            )
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Insumo "{insumo_nombre}" removido correctamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al remover insumo: {str(e)}'
        }, status=500)