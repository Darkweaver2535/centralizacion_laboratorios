from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.core import serializers
import json
from .models import *
from .forms import *

@login_required
def ingreso_datos_view(request):
    if request.method == 'POST':
        # Si es una petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if request.POST.get('action') == 'get_materias':
                semestre = request.POST.get('semestre')
                if semestre:
                    try:
                        semestre_int = int(semestre)
                        materias = Materia.get_materias_por_semestre(semestre_int)
                        return JsonResponse({
                            'materias': materias
                        })
                    except ValueError:
                        pass
                return JsonResponse({'materias': []})
            
            elif request.POST.get('action') == 'get_equipos_individuales':
                tipo_equipo_id = request.POST.get('tipo_equipo')
                unidad_academica_id = request.POST.get('unidad_academica')
                
                if tipo_equipo_id:
                    try:
                        tipo_equipo = TipoEquipo.objects.get(nombre=tipo_equipo_id)
                        
                        # Filtrar equipos por unidad académica si se especifica
                        equipos_filter = {'tipo_equipo': tipo_equipo, 'estado_operativo': 'operativo'}
                        if unidad_academica_id:
                            equipos_filter['unidad_academica__nombre'] = unidad_academica_id
                        
                        equipos = EquipoIndividual.objects.filter(**equipos_filter)
                        
                        # Estadísticas generales (también filtradas por unidad académica)
                        stats_filter = {'tipo_equipo': tipo_equipo}
                        if unidad_academica_id:
                            stats_filter['unidad_academica__nombre'] = unidad_academica_id
                        
                        total_equipos = EquipoIndividual.objects.filter(**stats_filter).count()
                        equipos_operativos = equipos.count()
                        equipos_mantenimiento = EquipoIndividual.objects.filter(
                            **stats_filter,
                            estado_operativo='mantenimiento'
                        ).count()
                        equipos_reparacion = EquipoIndividual.objects.filter(
                            **stats_filter,
                            estado_operativo='reparacion'
                        ).count()
                        equipos_inoperativos = EquipoIndividual.objects.filter(
                            **stats_filter,
                            estado_operativo='inoperativo'
                        ).count()
                        
                        equipos_data = []
                        for equipo in equipos:
                            equipos_data.append({
                                'id': equipo.id,
                                'codigo': equipo.codigo,
                                'display_name': equipo.get_display_name(),
                                'estado_fisico': equipo.get_estado_fisico_display(),
                                'estado_operativo': equipo.get_estado_operativo_display()
                            })
                        
                        return JsonResponse({
                            'equipos': equipos_data,
                            'capacidad_estudiantes': tipo_equipo.capacidad_estudiantes,
                            'estadisticas': {
                                'total_equipos': total_equipos,
                                'operativos': equipos_operativos,
                                'mantenimiento': equipos_mantenimiento,
                                'reparacion': equipos_reparacion,
                                'inoperativos': equipos_inoperativos
                            }
                        })
                    except TipoEquipo.DoesNotExist:
                        pass
                return JsonResponse({
                    'equipos': [], 
                    'capacidad_estudiantes': 1, 
                    'estadisticas': {
                        'total_equipos': 0,
                        'operativos': 0,
                        'mantenimiento': 0,
                        'reparacion': 0,
                        'inoperativos': 0
                    }
                })
            
            elif request.POST.get('action') == 'get_recomendacion':
                tipo_equipo_id = request.POST.get('tipo_equipo')
                cantidad_estudiantes = request.POST.get('cantidad_estudiantes')
                
                if tipo_equipo_id and cantidad_estudiantes:
                    try:
                        tipo_equipo = TipoEquipo.objects.get(nombre=tipo_equipo_id)
                        estudiantes = int(cantidad_estudiantes)
                        
                        capacidad_por_equipo = tipo_equipo.capacidad_estudiantes
                        equipos_disponibles = EquipoIndividual.objects.filter(
                            tipo_equipo=tipo_equipo,
                            estado_operativo='operativo'
                        ).count()
                        
                        total_equipos = EquipoIndividual.objects.filter(tipo_equipo=tipo_equipo).count()
                        
                        equipos_necesarios = -(-estudiantes // capacidad_por_equipo)  # Ceil division
                        
                        if equipos_necesarios <= equipos_disponibles:
                            if capacidad_por_equipo == 1:
                                mensaje = f'✅ Cada estudiante usará un equipo individual. Se necesitan {equipos_necesarios} equipos de {equipos_disponibles} disponibles (Total: {total_equipos}).'
                                estado = 'suficiente'
                            else:
                                mensaje = f'✅ Se pueden agrupar {capacidad_por_equipo} estudiantes por equipo. Se necesitan {equipos_necesarios} equipos de {equipos_disponibles} disponibles (Total: {total_equipos}).'
                                estado = 'suficiente'
                        else:
                            faltante = equipos_necesarios - equipos_disponibles
                            mensaje = f'⚠️ Se necesitan {equipos_necesarios} equipos pero solo hay {equipos_disponibles} disponibles de {total_equipos} totales. Se recomienda comprar {faltante} equipos adicionales.'
                            estado = 'insuficiente'
                        
                        return JsonResponse({
                            'mensaje': mensaje,
                            'estado': estado,
                            'equipos_necesarios': equipos_necesarios,
                            'equipos_disponibles': equipos_disponibles,
                            'total_equipos': total_equipos,
                            'equipos_faltantes': equipos_necesarios - equipos_disponibles if equipos_necesarios > equipos_disponibles else 0
                        })
                    except (TipoEquipo.DoesNotExist, ValueError):
                        pass
                
                return JsonResponse({'mensaje': '', 'estado': 'error'})
            
            # Si es para validar paso
            step = request.POST.get('step')
            if step:
                return validate_step(request, step)
        
        # Procesar formulario completo
        try:
            with transaction.atomic():
                # Obtener o crear UnidadAcademica
                unidad_academica, created = UnidadAcademica.objects.get_or_create(
                    nombre=request.POST.get('unidad_academica')
                )
                
                # Obtener o crear Carrera
                carrera, created = Carrera.objects.get_or_create(
                    nombre=request.POST.get('carrera')
                )
                
                # Crear o obtener Materia
                materia, created = Materia.objects.get_or_create(
                    nombre=request.POST.get('materia'),
                    carrera=carrera,
                    semestre=int(request.POST.get('semestre'))
                )
                
                # Crear Laboratorio
                laboratorio = Laboratorio.objects.create(
                    nombre=request.POST.get('laboratorio'),
                    unidad_academica=unidad_academica,
                    materia=materia,
                    usuario_creador=request.user
                )
                
                # Procesar ensayos
                ensayos = request.POST.getlist('ensayos[]')
                estudiantes = request.POST.getlist('estudiantes[]')
                
                for i, ensayo_nombre in enumerate(ensayos):
                    if ensayo_nombre.strip():
                        cantidad_estudiantes = int(estudiantes[i]) if i < len(estudiantes) and estudiantes[i] else 1
                        
                        ensayo = Ensayo.objects.create(
                            nombre=ensayo_nombre,
                            laboratorio=laboratorio,
                            cantidad_estudiantes=cantidad_estudiantes
                        )
                        
                        # Procesar equipos para este ensayo
                        equipos_key = f'equipos[{i+1}][]'
                        equipos_individuales_key = f'equipos_individuales[{i+1}][]'
                        
                        equipos_tipos = request.POST.getlist(equipos_key)
                        equipos_individuales = request.POST.getlist(equipos_individuales_key)
                        
                        for j, equipo_tipo in enumerate(equipos_tipos):
                            if equipo_tipo:
                                tipo_equipo = TipoEquipo.objects.get(nombre=equipo_tipo)
                                
                                equipo = Equipo.objects.create(
                                    tipo_equipo=tipo_equipo,
                                    ensayo=ensayo,
                                    cantidad_necesaria=1
                                )
                                
                                # Asignar equipos individuales si fueron seleccionados
                                if j < len(equipos_individuales):
                                    equipos_ids = equipos_individuales[j].split(',') if equipos_individuales[j] else []
                                    for equipo_id in equipos_ids:
                                        if equipo_id.strip():
                                            try:
                                                equipo_individual = EquipoIndividual.objects.get(id=int(equipo_id))
                                                equipo.equipos_seleccionados.add(equipo_individual)
                                            except (EquipoIndividual.DoesNotExist, ValueError):
                                                pass
                
                # Guardar registro completo
                RegistroIngreso.objects.create(
                    laboratorio=laboratorio,
                    usuario=request.user,
                    datos_completos=dict(request.POST)
                )
                
                messages.success(request, 'Información guardada correctamente')
                return redirect('dashboard')
                
        except Exception as e:
            messages.error(request, f'Error al guardar la información: {str(e)}')
    
    # Preparar datos para JavaScript
    tipos_equipo = TipoEquipo.objects.all().order_by('nombre_display')
    tipos_equipo_json = []
    for tipo in tipos_equipo:
        tipos_equipo_json.append({
            'nombre': tipo.nombre,
            'nombre_display': tipo.get_nombre_display(),
        })

    # Inicializar formularios
    context = {
        'unidad_form': UnidadAcademicaForm(),
        'info_form': InformacionAcademicaForm(),
        'lab_form': LaboratorioForm(),
        'ensayo_form': EnsayoEquipoForm(),
        'tipos_equipo': tipos_equipo,
        'tipos_equipo_json': json.dumps(tipos_equipo_json),
    }
    
    return render(request, 'ingreso_datos.html', context)

def validate_step(request, step):
    """Validar paso específico via AJAX"""
    errors = {}
    
    if step == '1':
        form = UnidadAcademicaForm(request.POST)
        if not form.is_valid():
            errors = form.errors
    
    elif step == '2':
        form = InformacionAcademicaForm(request.POST)
        if not form.is_valid():
            errors = form.errors
    
    elif step == '3':
        form = LaboratorioForm(request.POST)
        if not form.is_valid():
            errors = form.errors
    
    elif step == '4':
        # Validar que haya al menos un ensayo
        ensayos = request.POST.getlist('ensayos[]')
        if not any(ensayo.strip() for ensayo in ensayos):
            errors = {'ensayos': ['Debe seleccionar al menos un ensayo']}
    
    return JsonResponse({
        'valid': len(errors) == 0,
        'errors': errors
    })