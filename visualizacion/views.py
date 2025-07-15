from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt
from ingreso_datos.models import *
import json
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from django.utils import timezone
import datetime

@login_required
def visualizacion_view(request):
    """Vista principal de visualización y análisis"""
    
    # Obtener datos para los filtros
    unidades = UnidadAcademica.objects.all()
    carreras = Carrera.objects.all()
    tipos_equipos = TipoEquipo.objects.all()
    
    # Obtener estadísticas generales
    stats = {
        'total_laboratorios': Laboratorio.objects.count(),
        'total_ensayos': Ensayo.objects.count(),
        'total_equipos': EquipoIndividual.objects.count(),
        'total_materias': Materia.objects.count(),
    }
    
    context = {
        'unidades': unidades,
        'carreras': carreras,
        'tipos_equipos': tipos_equipos,
        'stats': stats,
    }
    
    return render(request, 'visualizacion.html', context)

@login_required
def filtrar_datos(request):
    """Vista AJAX para filtrar datos según los criterios seleccionados"""
    
    # Obtener filtros del request
    filtros = {
        'unidad_academica': request.GET.get('unidad_academica'),
        'semestre': request.GET.get('semestre'),
        'carrera': request.GET.get('carrera'),
        'materia': request.GET.get('materia'),
        'laboratorio': request.GET.get('laboratorio'),
        'tipo_equipo': request.GET.get('tipo_equipo'),
    }
    
    # Construir la consulta base
    laboratorios = Laboratorio.objects.all()
    
    # Aplicar filtros
    if filtros['unidad_academica']:
        laboratorios = laboratorios.filter(unidad_academica__nombre=filtros['unidad_academica'])
    
    if filtros['semestre']:
        laboratorios = laboratorios.filter(materia__semestre=filtros['semestre'])
    
    if filtros['carrera']:
        laboratorios = laboratorios.filter(materia__carrera__nombre=filtros['carrera'])
    
    if filtros['materia']:
        laboratorios = laboratorios.filter(materia__nombre=filtros['materia'])
    
    if filtros['laboratorio']:
        laboratorios = laboratorios.filter(nombre=filtros['laboratorio'])
    
    # Preparar datos para las tablas
    datos_laboratorios = []
    datos_ensayos = []
    datos_equipos = []
    
    for laboratorio in laboratorios:
        # Datos del laboratorio
        datos_laboratorios.append({
            'unidad_academica': laboratorio.unidad_academica.get_nombre_display(),
            'semestre': f"{laboratorio.materia.semestre}° Semestre",
            'carrera': laboratorio.materia.carrera.get_nombre_display(),
            'materia': laboratorio.materia.get_nombre_display(),
            'laboratorio': laboratorio.get_nombre_display(),
            'llenado_por': laboratorio.usuario_creador.get_full_name() or laboratorio.usuario_creador.username,
        })
        
        # Datos de ensayos
        for ensayo in laboratorio.ensayos.all():
            datos_ensayos.append({
                'laboratorio': laboratorio.get_nombre_display(),
                'ensayo': ensayo.get_nombre_display(),
                'estudiantes': ensayo.cantidad_estudiantes,
                'unidad_academica': laboratorio.unidad_academica.get_nombre_display(),
                'carrera': laboratorio.materia.carrera.get_nombre_display(),
                'materia': laboratorio.materia.get_nombre_display(),
                'llenado_por': laboratorio.usuario_creador.get_full_name() or laboratorio.usuario_creador.username,
            })
            
            # Datos de equipos
            for equipo in ensayo.equipos.all():
                equipos_seleccionados = equipo.equipos_seleccionados.all()
                
                if equipos_seleccionados:
                    for equipo_individual in equipos_seleccionados:
                        datos_equipos.append({
                            'laboratorio': laboratorio.get_nombre_display(),
                            'ensayo': ensayo.get_nombre_display(),
                            'tipo_equipo': equipo.tipo_equipo.get_nombre_display(),
                            'codigo_equipo': equipo_individual.codigo,
                            'estado_fisico': equipo_individual.get_estado_fisico_display(),
                            'unidad_academica': laboratorio.unidad_academica.get_nombre_display(),
                            'carrera': laboratorio.materia.carrera.get_nombre_display(),
                            'llenado_por': laboratorio.usuario_creador.get_full_name() or laboratorio.usuario_creador.username,
                        })
                else:
                    datos_equipos.append({
                        'laboratorio': laboratorio.get_nombre_display(),
                        'ensayo': ensayo.get_nombre_display(),
                        'tipo_equipo': equipo.tipo_equipo.get_nombre_display(),
                        'codigo_equipo': 'Sin especificar',
                        'estado_fisico': '-',
                        'unidad_academica': laboratorio.unidad_academica.get_nombre_display(),
                        'carrera': laboratorio.materia.carrera.get_nombre_display(),
                        'llenado_por': laboratorio.usuario_creador.get_full_name() or laboratorio.usuario_creador.username,
                    })
    
    # Filtrar equipos si se especificó tipo de equipo
    if filtros['tipo_equipo']:
        datos_equipos = [e for e in datos_equipos if e['tipo_equipo'] == TipoEquipo.objects.get(nombre=filtros['tipo_equipo']).get_nombre_display()]
    
    # Calcular estadísticas de los datos filtrados
    stats_filtradas = {
        'total_laboratorios': len(datos_laboratorios),
        'total_ensayos': len(datos_ensayos),
        'total_equipos': len(datos_equipos),
    }
    
    return JsonResponse({
        'laboratorios': datos_laboratorios,
        'ensayos': datos_ensayos,
        'equipos': datos_equipos,
        'stats': stats_filtradas,
    })

@login_required
def obtener_opciones_filtro(request):
    """Vista AJAX para obtener opciones de filtro dinámicas"""
    
    campo = request.GET.get('campo')
    filtros_actuales = {
        'unidad_academica': request.GET.get('unidad_academica'),
        'semestre': request.GET.get('semestre'),
        'carrera': request.GET.get('carrera'),
        'materia': request.GET.get('materia'),
        'laboratorio': request.GET.get('laboratorio'),
    }
    
    opciones = []
    
    # Construir consulta base
    laboratorios = Laboratorio.objects.all()
    
    # Aplicar filtros existentes
    if filtros_actuales['unidad_academica']:
        laboratorios = laboratorios.filter(unidad_academica__nombre=filtros_actuales['unidad_academica'])
    
    if filtros_actuales['semestre']:
        laboratorios = laboratorios.filter(materia__semestre=filtros_actuales['semestre'])
    
    if filtros_actuales['carrera']:
        laboratorios = laboratorios.filter(materia__carrera__nombre=filtros_actuales['carrera'])
    
    if filtros_actuales['materia']:
        laboratorios = laboratorios.filter(materia__nombre=filtros_actuales['materia'])
    
    # Obtener opciones según el campo solicitado
    if campo == 'semestre':
        semestres = laboratorios.values_list('materia__semestre', flat=True).distinct()
        opciones = [(str(s), f"{s}° Semestre") for s in sorted(semestres)]
    
    elif campo == 'carrera':
        carreras = laboratorios.values_list('materia__carrera__nombre', 'materia__carrera__nombre').distinct()
        opciones = [(c[0], Carrera.objects.get(nombre=c[0]).get_nombre_display()) for c in carreras]
    
    elif campo == 'materia':
        materias = laboratorios.values_list('materia__nombre', 'materia__nombre').distinct()
        opciones = [(m[0], Materia.objects.filter(nombre=m[0]).first().get_nombre_display()) for m in materias]
    
    elif campo == 'laboratorio':
        labs = laboratorios.values_list('nombre', 'nombre').distinct()
        opciones = [(l[0], Laboratorio.objects.filter(nombre=l[0]).first().get_nombre_display()) for l in labs]
    
    return JsonResponse({'opciones': opciones})

@csrf_exempt
def equipos_ajax(request):
    """Vista AJAX para manejar peticiones relacionadas con equipos"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'get_tipos_equipo':
            unidad_academica = request.POST.get('unidad_academica')
            limit = request.POST.get('limit', '100')  # Límite por defecto
            offset = request.POST.get('offset', '0')
            search = request.POST.get('search', '')
            
            if not unidad_academica:
                return JsonResponse({'error': 'Unidad académica requerida'}, status=400)
            
            try:
                limit = int(limit)
                offset = int(offset)
                # Limitar máximo a 200 para evitar sobrecarga
                limit = min(limit, 200)
            except ValueError:
                return JsonResponse({'error': 'Parámetros de paginación inválidos'}, status=400)
            
            # Convertir a minúsculas para coincidir con la base de datos
            unidad_academica = unidad_academica.lower()
            
            # Filtrar tipos de equipo que tienen equipos individuales en la unidad académica
            tipos_equipo = TipoEquipo.objects.filter(
                equipos_individuales__unidad_academica__nombre=unidad_academica
            ).distinct()
            
            # Aplicar filtro de búsqueda si se proporciona
            if search:
                tipos_equipo = tipos_equipo.filter(
                    nombre__icontains=search
                )
            
            # Ordenar por nombre para consistencia
            tipos_equipo = tipos_equipo.order_by('nombre')
            
            # Contar total antes de aplicar paginación
            total_count = tipos_equipo.count()
            
            # Aplicar paginación
            tipos_equipo = tipos_equipo[offset:offset + limit]
            
            # Preparar datos para el frontend
            tipos_data = []
            for tipo in tipos_equipo:
                tipos_data.append({
                    'nombre': tipo.nombre,
                    'display_name': tipo.get_nombre_display()
                })
            
            return JsonResponse({
                'tipos_equipo': tipos_data,
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            })
        
        elif action == 'get_equipos_individuales':
            tipo_equipo = request.POST.get('tipo_equipo')
            unidad_academica = request.POST.get('unidad_academica')
            
            if not tipo_equipo or not unidad_academica:
                return JsonResponse({'error': 'Tipo de equipo y unidad académica requeridos'}, status=400)
            
            # Convertir a minúsculas para coincidir con la base de datos
            unidad_academica = unidad_academica.lower()
            
            # Filtrar equipos individuales operativos
            equipos = EquipoIndividual.objects.filter(
                tipo_equipo__nombre=tipo_equipo,
                unidad_academica__nombre=unidad_academica,
                estado_operativo='operativo'
            ).select_related('tipo_equipo')
            
            # Preparar datos para la respuesta
            equipos_data = []
            for equipo in equipos:
                equipos_data.append({
                    'id': equipo.id,
                    'codigo': equipo.codigo,
                    'tipo_equipo': equipo.tipo_equipo.nombre,
                    'estado_fisico': equipo.get_estado_fisico_display(),
                    'estado_operativo': equipo.get_estado_operativo_display(),
                    'ubicacion': equipo.ubicacion or 'Sin especificar',
                    'display_name': f"{equipo.codigo} - {equipo.tipo_equipo.nombre} ({equipo.get_estado_fisico_display()})"
                })
            
            return JsonResponse({
                'equipos': equipos_data,
                'estadisticas': {
                    'total': len(equipos_data),
                    'operativos': len(equipos_data)  # Ya están filtrados por operativo
                },
                'capacidad_estudiantes': len(equipos_data)  # Cada equipo puede atender 1 estudiante
            })
        
        elif action == 'get_recomendacion':
            tipo_equipo = request.POST.get('tipo_equipo')
            cantidad_estudiantes = request.POST.get('cantidad_estudiantes')
            unidad_academica = request.POST.get('unidad_academica')
            
            if not all([tipo_equipo, cantidad_estudiantes, unidad_academica]):
                return JsonResponse({'error': 'Todos los parámetros son requeridos'}, status=400)
            
            try:
                cantidad_estudiantes = int(cantidad_estudiantes)
            except ValueError:
                return JsonResponse({'error': 'Cantidad de estudiantes debe ser un número'}, status=400)
            
            # Convertir a minúsculas para coincidir con la base de datos
            unidad_academica = unidad_academica.lower()
            
            # Contar equipos disponibles
            equipos_disponibles = EquipoIndividual.objects.filter(
                tipo_equipo__nombre=tipo_equipo,
                unidad_academica__nombre=unidad_academica
            ).count()
            
            # Lógica de recomendación
            if equipos_disponibles >= cantidad_estudiantes:
                recomendacion = "SUFICIENTES"
                mensaje = f"Hay {equipos_disponibles} equipos disponibles para {cantidad_estudiantes} estudiantes"
            else:
                faltantes = cantidad_estudiantes - equipos_disponibles
                recomendacion = "INSUFICIENTES"
                mensaje = f"Faltan {faltantes} equipos. Hay {equipos_disponibles} disponibles para {cantidad_estudiantes} estudiantes"
            
            return JsonResponse({
                'recomendacion': recomendacion,
                'mensaje': mensaje,
                'equipos_disponibles': equipos_disponibles,
                'cantidad_estudiantes': cantidad_estudiantes
            })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def exportar_excel(request):
    """Vista para exportar datos a Excel según el tipo seleccionado"""
    
    # Obtener filtros del request
    filtros = {
        'unidad_academica': request.GET.get('unidad_academica'),
        'semestre': request.GET.get('semestre'),
        'carrera': request.GET.get('carrera'),
        'materia': request.GET.get('materia'),
        'laboratorio': request.GET.get('laboratorio'),
        'tipo_equipo': request.GET.get('tipo_equipo'),
    }
    
    # Obtener tipo de exportación
    tipo_exportacion = request.GET.get('tipo', 'general')
    
    # Crear workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    
    # Configurar estilos
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    
    border_style = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Obtener datos según el tipo
    if tipo_exportacion == 'general':
        datos = obtener_datos_general_completos(filtros)
        nombre_archivo = "datos_generales_completos"
        configurar_excel_general(ws, datos, header_font, header_fill, header_alignment, border_style)
    elif tipo_exportacion == 'laboratorios':
        datos = obtener_datos_laboratorios_completos(filtros)
        nombre_archivo = "laboratorios_completos"
        configurar_excel_laboratorios(ws, datos, header_font, header_fill, header_alignment, border_style)
    elif tipo_exportacion == 'ensayos':
        datos = obtener_datos_ensayos_completos(filtros)
        nombre_archivo = "ensayos_completos"
        configurar_excel_ensayos(ws, datos, header_font, header_fill, header_alignment, border_style)
    elif tipo_exportacion == 'equipos':
        datos = obtener_datos_equipos_completos(filtros)
        nombre_archivo = "equipos_completos"
        configurar_excel_equipos(ws, datos, header_font, header_fill, header_alignment, border_style)
    else:
        return JsonResponse({'error': 'Tipo de exportación no válido'}, status=400)
    
    # Configurar respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    # Generar nombre de archivo con fecha
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}_{fecha_actual}.xlsx"'
    
    # Guardar workbook
    wb.save(response)
    
    return response

def obtener_datos_general_completos(filtros):
    """Obtiene datos completos para la vista general"""
    laboratorios = Laboratorio.objects.all()
    
    # Aplicar filtros
    if filtros['unidad_academica']:
        laboratorios = laboratorios.filter(unidad_academica__nombre=filtros['unidad_academica'])
    if filtros['semestre']:
        laboratorios = laboratorios.filter(materia__semestre=filtros['semestre'])
    if filtros['carrera']:
        laboratorios = laboratorios.filter(materia__carrera__nombre=filtros['carrera'])
    if filtros['materia']:
        laboratorios = laboratorios.filter(materia__nombre=filtros['materia'])
    if filtros['laboratorio']:
        laboratorios = laboratorios.filter(nombre=filtros['laboratorio'])
    
    datos = []
    for laboratorio in laboratorios:
        # Obtener ensayos del laboratorio
        ensayos = Ensayo.objects.filter(laboratorio=laboratorio)
        
        if not ensayos.exists():
            # Laboratorio sin ensayos
            datos.append({
                'id_laboratorio': laboratorio.id,
                'unidad_academica': laboratorio.unidad_academica.get_nombre_display(),
                'codigo_unidad': laboratorio.unidad_academica.nombre,
                'semestre': f"{laboratorio.materia.semestre}° Semestre",
                'carrera': laboratorio.materia.carrera.get_nombre_display(),
                'materia': laboratorio.materia.get_nombre_display(),
                'laboratorio': laboratorio.nombre,
                'descripcion_laboratorio': laboratorio.get_nombre_display(),
                'fecha_creacion_lab': laboratorio.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                'ensayo': 'Sin ensayos',
                'tipo_ensayo': '',
                'estudiantes': 0,
                'fecha_creacion_ensayo': '',
                'tipo_equipo': 'Sin equipos',
                'nombre_equipo': '',
                'codigo_equipo': '',
                'descripcion_equipo': '',
                'estado_fisico': '',
                'observaciones_equipo': '',
                'fecha_creacion_equipo': '',
                'llenado_por': laboratorio.usuario_creador.username if laboratorio.usuario_creador else 'N/A',
                'email_usuario': laboratorio.usuario_creador.email if laboratorio.usuario_creador else 'N/A',
                'fecha_llenado': laboratorio.fecha_creacion.strftime("%Y-%m-%d"),
            })
        else:
            for ensayo in ensayos:
                # Obtener equipos del ensayo
                equipos_ensayo = Equipo.objects.filter(ensayo=ensayo)
                
                if not equipos_ensayo.exists():
                    # Ensayo sin equipos
                    datos.append({
                        'id_laboratorio': laboratorio.id,
                        'unidad_academica': laboratorio.unidad_academica.get_nombre_display(),
                        'codigo_unidad': laboratorio.unidad_academica.nombre,
                        'semestre': f"{laboratorio.materia.semestre}° Semestre",
                        'carrera': laboratorio.materia.carrera.get_nombre_display(),
                        'materia': laboratorio.materia.get_nombre_display(),
                        'laboratorio': laboratorio.nombre,
                        'descripcion_laboratorio': laboratorio.get_nombre_display(),
                        'fecha_creacion_lab': laboratorio.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                        'ensayo': ensayo.get_nombre_display(),
                        'tipo_ensayo': ensayo.nombre,
                        'estudiantes': ensayo.cantidad_estudiantes,
                        'fecha_creacion_ensayo': laboratorio.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                        'tipo_equipo': 'Sin equipos específicos',
                        'nombre_equipo': '',
                        'codigo_equipo': '',
                        'descripcion_equipo': '',
                        'estado_fisico': '',
                        'observaciones_equipo': '',
                        'fecha_creacion_equipo': '',
                        'llenado_por': laboratorio.usuario_creador.username if laboratorio.usuario_creador else 'N/A',
                        'email_usuario': laboratorio.usuario_creador.email if laboratorio.usuario_creador else 'N/A',
                        'fecha_llenado': laboratorio.fecha_creacion.strftime("%Y-%m-%d"),
                    })
                else:
                    for equipo_ensayo in equipos_ensayo:
                        # Obtener equipos individuales seleccionados
                        equipos_individuales = equipo_ensayo.equipos_seleccionados.all()
                        
                        if not equipos_individuales.exists():
                            # Tipo de equipo sin equipos individuales
                            datos.append({
                                'id_laboratorio': laboratorio.id,
                                'unidad_academica': laboratorio.unidad_academica.get_nombre_display(),
                                'codigo_unidad': laboratorio.unidad_academica.nombre,
                                'semestre': f"{laboratorio.materia.semestre}° Semestre",
                                'carrera': laboratorio.materia.carrera.get_nombre_display(),
                                'materia': laboratorio.materia.get_nombre_display(),
                                'laboratorio': laboratorio.nombre,
                                'descripcion_laboratorio': laboratorio.get_nombre_display(),
                                'fecha_creacion_lab': laboratorio.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                                'ensayo': ensayo.get_nombre_display(),
                                'tipo_ensayo': ensayo.nombre,
                                'estudiantes': ensayo.cantidad_estudiantes,
                                'fecha_creacion_ensayo': laboratorio.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                                'tipo_equipo': equipo_ensayo.tipo_equipo.get_nombre_display(),
                                'nombre_equipo': 'Sin equipos específicos',
                                'codigo_equipo': '',
                                'descripcion_equipo': '',
                                'estado_fisico': '',
                                'observaciones_equipo': '',
                                'fecha_creacion_equipo': '',
                                'llenado_por': laboratorio.usuario_creador.username if laboratorio.usuario_creador else 'N/A',
                                'email_usuario': laboratorio.usuario_creador.email if laboratorio.usuario_creador else 'N/A',
                                'fecha_llenado': laboratorio.fecha_creacion.strftime("%Y-%m-%d"),
                            })
                        else:
                            for equipo_individual in equipos_individuales:
                                datos.append({
                                    'id_laboratorio': laboratorio.id,
                                    'unidad_academica': laboratorio.unidad_academica.get_nombre_display(),
                                    'codigo_unidad': laboratorio.unidad_academica.nombre,
                                    'semestre': f"{laboratorio.materia.semestre}° Semestre",
                                    'carrera': laboratorio.materia.carrera.get_nombre_display(),
                                    'materia': laboratorio.materia.get_nombre_display(),
                                    'laboratorio': laboratorio.nombre,
                                    'descripcion_laboratorio': laboratorio.get_nombre_display(),
                                    'fecha_creacion_lab': laboratorio.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                                    'ensayo': ensayo.get_nombre_display(),
                                    'tipo_ensayo': ensayo.nombre,
                                    'estudiantes': ensayo.cantidad_estudiantes,
                                    'fecha_creacion_ensayo': laboratorio.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                                    'tipo_equipo': equipo_ensayo.tipo_equipo.get_nombre_display(),
                                    'nombre_equipo': equipo_individual.tipo_equipo.get_nombre_display(),
                                    'codigo_equipo': equipo_individual.codigo,
                                    'descripcion_equipo': equipo_individual.tipo_equipo.descripcion,
                                    'estado_fisico': equipo_individual.get_estado_fisico_display(),
                                    'observaciones_equipo': equipo_individual.observaciones,
                                    'fecha_creacion_equipo': equipo_individual.fecha_ingreso.strftime("%Y-%m-%d %H:%M:%S"),
                                    'llenado_por': laboratorio.usuario_creador.username if laboratorio.usuario_creador else 'N/A',
                                    'email_usuario': laboratorio.usuario_creador.email if laboratorio.usuario_creador else 'N/A',
                                    'fecha_llenado': laboratorio.fecha_creacion.strftime("%Y-%m-%d"),
                                })
    
    return datos

def obtener_datos_laboratorios_completos(filtros):
    """Obtiene datos completos para laboratorios"""
    laboratorios = Laboratorio.objects.all()
    
    # Aplicar filtros
    if filtros['unidad_academica']:
        laboratorios = laboratorios.filter(unidad_academica__nombre=filtros['unidad_academica'])
    if filtros['semestre']:
        laboratorios = laboratorios.filter(materia__semestre=filtros['semestre'])
    if filtros['carrera']:
        laboratorios = laboratorios.filter(materia__carrera__nombre=filtros['carrera'])
    if filtros['materia']:
        laboratorios = laboratorios.filter(materia__nombre=filtros['materia'])
    if filtros['laboratorio']:
        laboratorios = laboratorios.filter(nombre=filtros['laboratorio'])
    
    datos = []
    for laboratorio in laboratorios:
        # Contar ensayos y equipos
        total_ensayos = Ensayo.objects.filter(laboratorio=laboratorio).count()
        total_equipos = EquipoIndividual.objects.filter(
            equipo__ensayo__laboratorio=laboratorio
        ).count()
        
        datos.append({
            'id_laboratorio': laboratorio.id,
            'unidad_academica': laboratorio.unidad_academica.get_nombre_display(),
            'codigo_unidad': laboratorio.unidad_academica.nombre,
            'semestre': f"{laboratorio.materia.semestre}° Semestre",
            'numero_semestre': laboratorio.materia.semestre,
            'carrera': laboratorio.materia.carrera.get_nombre_display(),
            'materia': laboratorio.materia.get_nombre_display(),
            'laboratorio': laboratorio.nombre,
            'descripcion_laboratorio': laboratorio.get_nombre_display(),
            'total_ensayos': total_ensayos,
            'total_equipos': total_equipos,
            'fecha_creacion': laboratorio.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
            'llenado_por': laboratorio.usuario_creador.username if laboratorio.usuario_creador else 'N/A',
            'email_usuario': laboratorio.usuario_creador.email if laboratorio.usuario_creador else 'N/A',
            'nombre_completo_usuario': laboratorio.usuario_creador.get_full_name() if laboratorio.usuario_creador else 'N/A',
            'fecha_llenado': laboratorio.fecha_creacion.strftime("%Y-%m-%d"),
            'dia_semana': laboratorio.fecha_creacion.strftime("%A"),
            'mes_año': laboratorio.fecha_creacion.strftime("%B %Y"),
        })
    
    return datos

def obtener_datos_ensayos_completos(filtros):
    """Obtiene datos completos para ensayos"""
    ensayos = Ensayo.objects.all()
    
    # Aplicar filtros a través de laboratorio
    if filtros['unidad_academica']:
        ensayos = ensayos.filter(laboratorio__unidad_academica__nombre=filtros['unidad_academica'])
    if filtros['semestre']:
        ensayos = ensayos.filter(laboratorio__materia__semestre=filtros['semestre'])
    if filtros['carrera']:
        ensayos = ensayos.filter(laboratorio__materia__carrera__nombre=filtros['carrera'])
    if filtros['materia']:
        ensayos = ensayos.filter(laboratorio__materia__nombre=filtros['materia'])
    if filtros['laboratorio']:
        ensayos = ensayos.filter(laboratorio__nombre=filtros['laboratorio'])
    
    datos = []
    for ensayo in ensayos:
        # Obtener equipos del ensayo
        equipos_ensayo = Equipo.objects.filter(ensayo=ensayo)
        total_equipos = sum(equipo.equipos_seleccionados.count() for equipo in equipos_ensayo)
        tipos_equipos = [equipo.tipo_equipo.get_nombre_display() for equipo in equipos_ensayo]
        
        datos.append({
            'id_ensayo': ensayo.id,
            'laboratorio': ensayo.laboratorio.nombre,
            'id_laboratorio': ensayo.laboratorio.id,
            'unidad_academica': ensayo.laboratorio.unidad_academica.get_nombre_display(),
            'codigo_unidad': ensayo.laboratorio.unidad_academica.nombre,
            'semestre': f"{ensayo.laboratorio.materia.semestre}° Semestre",
            'numero_semestre': ensayo.laboratorio.materia.semestre,
            'carrera': ensayo.laboratorio.materia.carrera.get_nombre_display(),
            'materia': ensayo.laboratorio.materia.get_nombre_display(),
            'ensayo': ensayo.get_nombre_display(),
            'tipo_ensayo': ensayo.nombre,
            'cantidad_estudiantes': ensayo.cantidad_estudiantes,
            'total_equipos': total_equipos,
            'tipos_equipos': ', '.join(tipos_equipos) if tipos_equipos else 'Sin equipos',
            'fecha_creacion': ensayo.laboratorio.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
            'llenado_por': ensayo.laboratorio.usuario_creador.username if ensayo.laboratorio.usuario_creador else 'N/A',
            'email_usuario': ensayo.laboratorio.usuario_creador.email if ensayo.laboratorio.usuario_creador else 'N/A',
            'nombre_completo_usuario': ensayo.laboratorio.usuario_creador.get_full_name() if ensayo.laboratorio.usuario_creador else 'N/A',
            'fecha_llenado': ensayo.laboratorio.fecha_creacion.strftime("%Y-%m-%d"),
            'dia_semana': ensayo.laboratorio.fecha_creacion.strftime("%A"),
            'mes_año': ensayo.laboratorio.fecha_creacion.strftime("%B %Y"),
        })
    
    return datos

def obtener_datos_equipos_completos(filtros):
    """Obtiene datos completos para equipos"""
    equipos = EquipoIndividual.objects.all()
    
    # Aplicar filtros
    if filtros['unidad_academica']:
        equipos = equipos.filter(unidad_academica__nombre=filtros['unidad_academica'])
    if filtros['tipo_equipo']:
        equipos = equipos.filter(tipo_equipo__nombre=filtros['tipo_equipo'])
    
    # Filtros adicionales a través de ensayos
    if filtros['semestre'] or filtros['carrera'] or filtros['materia'] or filtros['laboratorio']:
        ensayos_filtrados = Ensayo.objects.all()
        
        if filtros['semestre']:
            ensayos_filtrados = ensayos_filtrados.filter(laboratorio__materia__semestre=filtros['semestre'])
        if filtros['carrera']:
            ensayos_filtrados = ensayos_filtrados.filter(laboratorio__materia__carrera__nombre=filtros['carrera'])
        if filtros['materia']:
            ensayos_filtrados = ensayos_filtrados.filter(laboratorio__materia__nombre=filtros['materia'])
        if filtros['laboratorio']:
            ensayos_filtrados = ensayos_filtrados.filter(laboratorio__nombre=filtros['laboratorio'])
        
        # Obtener equipos que están en esos ensayos
        equipos = equipos.filter(equipo__ensayo__in=ensayos_filtrados)
    
    datos = []
    for equipo in equipos:
        # Obtener todos los ensayos donde se usa este equipo
        ensayos_equipo = Ensayo.objects.filter(
            equipos__equipos_seleccionados=equipo
        ).distinct()
        
        if not ensayos_equipo.exists():
            # Equipo sin ensayos asociados
            datos.append({
                'id_equipo': equipo.id,
                'codigo_equipo': equipo.codigo,
                'nombre_equipo': equipo.tipo_equipo.get_nombre_display(),
                'descripcion_equipo': equipo.tipo_equipo.descripcion,
                'tipo_equipo': equipo.tipo_equipo.get_nombre_display(),
                'codigo_tipo_equipo': equipo.tipo_equipo.nombre,
                'estado_fisico': equipo.get_estado_fisico_display(),
                'codigo_estado': equipo.estado_fisico,
                'observaciones': equipo.observaciones,
                'unidad_academica': equipo.unidad_academica.get_nombre_display(),
                'codigo_unidad': equipo.unidad_academica.nombre,
                'laboratorio': 'Sin asignar',
                'ensayo': 'Sin asignar',
                'semestre': '',
                'carrera': '',
                'materia': '',
                'fecha_creacion': equipo.fecha_ingreso.strftime("%Y-%m-%d %H:%M:%S"),
                'fecha_llenado': equipo.fecha_ingreso.strftime("%Y-%m-%d"),
                'dia_semana': equipo.fecha_ingreso.strftime("%A"),
                'mes_año': equipo.fecha_ingreso.strftime("%B %Y"),
            })
        else:
            for ensayo in ensayos_equipo:
                datos.append({
                    'id_equipo': equipo.id,
                    'codigo_equipo': equipo.codigo,
                    'nombre_equipo': equipo.nombre,
                    'descripcion_equipo': equipo.descripcion,
                    'tipo_equipo': equipo.tipo_equipo.get_nombre_display(),
                    'codigo_tipo_equipo': equipo.tipo_equipo.nombre,
                    'estado_fisico': equipo.get_estado_fisico_display(),
                    'codigo_estado': equipo.estado_fisico,
                    'observaciones': equipo.observaciones,
                    'unidad_academica': equipo.unidad_academica.get_nombre_display(),
                    'codigo_unidad': equipo.unidad_academica.nombre,
                    'laboratorio': ensayo.laboratorio.nombre,
                    'id_laboratorio': ensayo.laboratorio.id,
                    'ensayo': ensayo.get_nombre_display(),
                    'tipo_ensayo': ensayo.nombre,
                    'cantidad_estudiantes': ensayo.cantidad_estudiantes,
                    'semestre': f"{ensayo.laboratorio.materia.semestre}° Semestre",
                    'numero_semestre': ensayo.laboratorio.materia.semestre,
                    'carrera': ensayo.laboratorio.materia.carrera.get_nombre_display(),
                    'materia': ensayo.laboratorio.materia.get_nombre_display(),
                    'fecha_creacion': equipo.fecha_ingreso.strftime("%Y-%m-%d %H:%M:%S"),
                    'llenado_por': ensayo.laboratorio.usuario_creador.username if ensayo.laboratorio.usuario_creador else 'N/A',
                    'email_usuario': ensayo.laboratorio.usuario_creador.email if ensayo.laboratorio.usuario_creador else 'N/A',
                    'nombre_completo_usuario': ensayo.laboratorio.usuario_creador.get_full_name() if ensayo.laboratorio.usuario_creador else 'N/A',
                    'fecha_llenado': equipo.fecha_ingreso.strftime("%Y-%m-%d"),
                    'dia_semana': equipo.fecha_ingreso.strftime("%A"),
                    'mes_año': equipo.fecha_ingreso.strftime("%B %Y"),
                })
    
    return datos

def configurar_excel_general(ws, datos, header_font, header_fill, header_alignment, border_style):
    """Configura el Excel para datos generales"""
    # Encabezados
    headers = [
        'ID Laboratorio', 'Unidad Académica', 'Código Unidad', 'Semestre', 'Carrera', 
        'Materia', 'Laboratorio', 'Descripción Laboratorio',
        'Fecha Creación Lab', 'Ensayo', 'Tipo Ensayo', 'Cantidad Estudiantes', 'Fecha Creación Ensayo',
        'Tipo Equipo', 'Nombre Equipo', 'Código Equipo', 'Descripción Equipo', 'Estado Físico',
        'Observaciones Equipo', 'Fecha Creación Equipo', 'Llenado Por', 'Email Usuario', 'Fecha Llenado'
    ]
    
    # Configurar título
    ws.title = "Datos Generales Completos"
    
    # Escribir encabezados
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border_style
    
    # Escribir datos
    for row, dato in enumerate(datos, 2):
        values = [
            dato['id_laboratorio'], dato['unidad_academica'], dato['codigo_unidad'],
            dato['semestre'], dato['carrera'], dato['materia'],
            dato['laboratorio'], dato['descripcion_laboratorio'],
            dato['fecha_creacion_lab'], dato['ensayo'], dato['tipo_ensayo'],
            dato['estudiantes'], dato['fecha_creacion_ensayo'], dato['tipo_equipo'],
            dato['nombre_equipo'], dato['codigo_equipo'], dato['descripcion_equipo'],
            dato['estado_fisico'], dato['observaciones_equipo'], dato['fecha_creacion_equipo'],
            dato['llenado_por'], dato['email_usuario'], dato['fecha_llenado']
        ]
        
        for col, value in enumerate(values, 1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.border = border_style
    
    # Ajustar ancho de columnas
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 20

def configurar_excel_laboratorios(ws, datos, header_font, header_fill, header_alignment, border_style):
    """Configura el Excel para laboratorios"""
    headers = [
        'ID Laboratorio', 'Unidad Académica', 'Código Unidad', 'Semestre', 'Número Semestre',
        'Carrera', 'Materia', 'Laboratorio',
        'Descripción', 'Total Ensayos', 'Total Equipos', 'Fecha Creación', 'Llenado Por',
        'Email Usuario', 'Nombre Completo', 'Fecha Llenado', 'Día Semana', 'Mes/Año'
    ]
    
    ws.title = "Laboratorios Completos"
    
    # Escribir encabezados
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border_style
    
    # Escribir datos
    for row, dato in enumerate(datos, 2):
        values = [
            dato['id_laboratorio'], dato['unidad_academica'], dato['codigo_unidad'],
            dato['semestre'], dato['numero_semestre'], dato['carrera'],
            dato['materia'], dato['laboratorio'], dato['descripcion_laboratorio'],
            dato['total_ensayos'], dato['total_equipos'], dato['fecha_creacion'],
            dato['llenado_por'], dato['email_usuario'], dato['nombre_completo_usuario'],
            dato['fecha_llenado'], dato['dia_semana'], dato['mes_año']
        ]
        
        for col, value in enumerate(values, 1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.border = border_style
    
    # Ajustar ancho de columnas
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18

def configurar_excel_ensayos(ws, datos, header_font, header_fill, header_alignment, border_style):
    """Configura el Excel para ensayos"""
    headers = [
        'ID Ensayo', 'Laboratorio', 'ID Laboratorio', 'Unidad Académica', 'Código Unidad',
        'Semestre', 'Número Semestre', 'Carrera', 'Materia',
        'Ensayo', 'Tipo Ensayo', 'Cantidad Estudiantes', 'Total Equipos', 'Tipos Equipos',
        'Fecha Creación', 'Llenado Por', 'Email Usuario', 'Nombre Completo',
        'Fecha Llenado', 'Día Semana', 'Mes/Año'
    ]
    
    ws.title = "Ensayos Completos"
    
    # Escribir encabezados
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border_style
    
    # Escribir datos
    for row, dato in enumerate(datos, 2):
        values = [
            dato['id_ensayo'], dato['laboratorio'], dato['id_laboratorio'],
            dato['unidad_academica'], dato['codigo_unidad'], dato['semestre'],
            dato['numero_semestre'], dato['carrera'],
            dato['materia'], dato['ensayo'], dato['tipo_ensayo'],
            dato['cantidad_estudiantes'], dato['total_equipos'], dato['tipos_equipos'],
            dato['fecha_creacion'], dato['llenado_por'], dato['email_usuario'],
            dato['nombre_completo_usuario'], dato['fecha_llenado'], dato['dia_semana'], dato['mes_año']
        ]
        
        for col, value in enumerate(values, 1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.border = border_style
    
    # Ajustar ancho de columnas
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18

def configurar_excel_equipos(ws, datos, header_font, header_fill, header_alignment, border_style):
    """Configura el Excel para equipos"""
    headers = [
        'ID Equipo', 'Código Equipo', 'Nombre Equipo', 'Descripción Equipo', 'Tipo Equipo',
        'Código Tipo Equipo', 'Estado Físico', 'Código Estado', 'Observaciones', 'Unidad Académica',
        'Código Unidad', 'Laboratorio', 'ID Laboratorio', 'Ensayo', 'Tipo Ensayo',
        'Cantidad Estudiantes', 'Semestre', 'Número Semestre', 'Carrera',
        'Materia', 'Fecha Creación', 'Llenado Por', 'Email Usuario',
        'Nombre Completo', 'Fecha Llenado', 'Día Semana', 'Mes/Año'
    ]
    
    ws.title = "Equipos Completos"
    
    # Escribir encabezados
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border_style
    
    # Escribir datos
    for row, dato in enumerate(datos, 2):
        values = [
            dato['id_equipo'], dato['codigo_equipo'], dato['nombre_equipo'],
            dato['descripcion_equipo'], dato['tipo_equipo'], dato['codigo_tipo_equipo'],
            dato['estado_fisico'], dato['codigo_estado'], dato['observaciones'],
            dato['unidad_academica'], dato['codigo_unidad'], dato['laboratorio'],
            dato.get('id_laboratorio', ''), dato['ensayo'], dato.get('tipo_ensayo', ''),
            dato.get('cantidad_estudiantes', ''), dato['semestre'], dato.get('numero_semestre', ''),
            dato['carrera'], dato['materia'],
            dato['fecha_creacion'], dato.get('llenado_por', ''),
            dato.get('email_usuario', ''), dato.get('nombre_completo_usuario', ''),
            dato['fecha_llenado'], dato['dia_semana'], dato['mes_año']
        ]
        
        for col, value in enumerate(values, 1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.border = border_style
    
    # Ajustar ancho de columnas
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18