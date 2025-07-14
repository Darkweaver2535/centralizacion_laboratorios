from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from .models import *
from .forms import *

@login_required
def ingreso_datos_view(request):
    if request.method == 'POST':
        # Si es una petición AJAX para obtener materias
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
                for i, ensayo_nombre in enumerate(ensayos):
                    if ensayo_nombre.strip():
                        ensayo = Ensayo.objects.create(
                            nombre=ensayo_nombre,
                            laboratorio=laboratorio
                        )
                        
                        # Procesar equipos para este ensayo
                        equipos_key = f'equipos[{i+1}][]'
                        cantidades_key = f'cantidades[{i+1}][]'
                        estados_key = f'estados[{i+1}][]'
                        
                        equipos = request.POST.getlist(equipos_key)
                        cantidades = request.POST.getlist(cantidades_key)
                        estados = request.POST.getlist(estados_key)
                        
                        for j, equipo_tipo in enumerate(equipos):
                            if equipo_tipo:
                                tipo_equipo, created = TipoEquipo.objects.get_or_create(
                                    nombre=equipo_tipo
                                )
                                
                                Equipo.objects.create(
                                    tipo_equipo=tipo_equipo,
                                    ensayo=ensayo,
                                    cantidad=int(cantidades[j]) if j < len(cantidades) and cantidades[j] else 1,
                                    estado=estados[j] if j < len(estados) else 'operativo'
                                )
                
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
    
    # Inicializar formularios
    context = {
        'unidad_form': UnidadAcademicaForm(),
        'info_form': InformacionAcademicaForm(),
        'lab_form': LaboratorioForm(),
        'ensayo_form': EnsayoEquipoForm(),
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