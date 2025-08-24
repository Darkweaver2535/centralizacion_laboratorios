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
from django.contrib.auth.models import User


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
                
                # Registrar log de creación
                LogReordenamientoInsumo.objects.create(
                    tarea=tarea,
                    usuario=request.user,
                    accion="Tarea creada",
                    descripcion="Nueva tarea de reordenamiento creada"
                )
                
                messages.success(request, 'Tarea de reordenamiento creada correctamente.')
                return redirect('insumos:detalle_tarea_reordenamiento', pk=tarea.pk)
                
        except Exception as e:
            messages.error(request, f'Error al crear la tarea: {str(e)}')
    
    # Datos para el formulario
    usuarios = User.objects.filter(is_active=True).order_by('username')
    
    context = {
        'tipos_tarea': TareaReordenamientoInsumo.TIPOS_TAREA,
        'prioridades': TareaReordenamientoInsumo.PRIORIDADES,
        'usuarios': usuarios,
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
    
    context = {
        'tarea': tarea,
        'tipos_tarea': TareaReordenamientoInsumo.TIPOS_TAREA,
        'estados_tarea': TareaReordenamientoInsumo.ESTADOS_TAREA,
        'prioridades': TareaReordenamientoInsumo.PRIORIDADES,
        'usuarios': usuarios,
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
