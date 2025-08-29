from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from equipos.models import Equipo
from core.models import UnidadAcademica, Carrera, Laboratorio
import json
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from django.utils import timezone
import datetime

@login_required
def visualizacion_view(request):
    """Vista principal de visualización con tabla completa de equipos"""
    
    # Obtener parámetros de filtrado
    unidad_academica = request.GET.get('unidad_academica', '')
    carrera = request.GET.get('carrera', '') 
    semestre = request.GET.get('semestre', '')
    estado = request.GET.get('estado', '')
    laboratorio = request.GET.get('laboratorio', '')
    responsable = request.GET.get('responsable', '')
    busqueda = request.GET.get('busqueda', '')
    
    # Obtener todos los equipos
    equipos = Equipo.objects.select_related(
        'unidad_academica', 'carrera', 'asignatura', 'unidad_tematica', 
        'guia_laboratorio', 'practica', 'laboratorio'
    ).all()
    
    # Aplicar filtros
    if unidad_academica:
        equipos = equipos.filter(unidad_academica_id=unidad_academica)
    if carrera:
        equipos = equipos.filter(carrera_id=carrera)
    if semestre:
        equipos = equipos.filter(semestre=semestre)
    if estado:
        equipos = equipos.filter(estado=estado)
    if laboratorio:
        equipos = equipos.filter(laboratorio_id=laboratorio)
    if responsable:
        equipos = equipos.filter(responsable_excel__icontains=responsable)
    if busqueda:
        equipos = equipos.filter(
            Q(equipo_existente__icontains=busqueda) |
            Q(marca__icontains=busqueda) |
            Q(modelo__icontains=busqueda) |
            Q(responsable_excel__icontains=busqueda)
        )
    
    # Estadísticas
    stats = {
        'total_equipos': equipos.count(),
        'total_laboratorios': Laboratorio.objects.count(),
        'equipos_operativos': equipos.filter(estado='operativo').count(),
        'equipos_mantenimiento': equipos.filter(estado='mantenimiento').count(),
    }
    
    # Paginación
    paginator = Paginator(equipos, 50)  # 50 equipos por página
    page_number = request.GET.get('page')
    equipos_page = paginator.get_page(page_number)
    
    # Datos para filtros
    unidades = UnidadAcademica.objects.all()
    carreras = Carrera.objects.all()
    laboratorios = Laboratorio.objects.all()
    
    # Obtener responsables únicos (solo los que tienen equipos)
    responsables = Equipo.objects.exclude(responsable_excel='').values_list('responsable_excel', flat=True).distinct().order_by('responsable_excel')
    
    # Choices para dropdowns
    semestres_choices = [(i, f'{i}°') for i in range(1, 11)]
    estados_choices = [
        ('operativo', 'Operativo'),
        ('mantenimiento', 'En Mantenimiento'),
        ('reparacion', 'En Reparación'),
        ('inoperativo', 'Inoperativo'),
    ]
    
    # Filtros aplicados (para mantener en la paginación)
    filtros = {
        'unidad_academica': unidad_academica,
        'carrera': carrera,
        'semestre': semestre,
        'estado': estado,
        'laboratorio': laboratorio,
        'responsable': responsable,
        'busqueda': busqueda,
    }
    
    context = {
        'equipos': equipos_page,
        'stats': stats,
        'unidades': unidades,
        'carreras': carreras,
        'laboratorios': laboratorios,
        'responsables': responsables,
        'semestres_choices': semestres_choices,
        'estados_choices': estados_choices,
        'filtros': filtros,
    }
    
    return render(request, 'visualizacion.html', context)

@login_required
def filtrar_datos(request):
    """Vista AJAX para filtrar datos"""
    return JsonResponse({
        'status': 'success',
        'message': 'Filtros aplicados correctamente'
    })

@login_required
def obtener_opciones_filtro(request):
    """Vista AJAX para obtener opciones de filtro"""
    return JsonResponse({
        'status': 'success',
        'opciones': []
    })

@login_required
def equipos_ajax(request):
    """Vista AJAX para obtener equipos"""
    return JsonResponse({
        'status': 'success',
        'equipos': []
    })

@login_required
def exportar_excel(request):
    """Vista para exportar datos a Excel"""
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="equipos.xlsx"'
    
    # Crear workbook simple
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Equipos"
    
    # Headers
    headers = ['ID', 'Equipo', 'Marca', 'Modelo', 'Estado']
    for col, header in enumerate(headers, 1):
        ws.cell(row=1, column=col, value=header)
    
    # Datos
    equipos = Equipo.objects.all()[:100]  # Limitar a 100 para evitar problemas
    for row, equipo in enumerate(equipos, 2):
        ws.cell(row=row, column=1, value=equipo.id)
        ws.cell(row=row, column=2, value=equipo.equipo_existente)
        ws.cell(row=row, column=3, value=equipo.marca or '')
        ws.cell(row=row, column=4, value=equipo.modelo or '')
        ws.cell(row=row, column=5, value=equipo.get_estado_display())
    
    wb.save(response)
    return response
