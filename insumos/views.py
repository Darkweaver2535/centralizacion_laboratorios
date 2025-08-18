from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from django.utils import timezone
import json

from .models import TipoInsumo, Insumo, MovimientoInsumo, SolicitudInsumo
from core.models import UnidadAcademica, Carrera, Asignatura, UnidadTematica, GuiaLaboratorio, Practica, Laboratorio

@login_required
def insumos_view(request):
    """Vista principal de insumos con filtros y paginación"""
    
    # Obtener filtros
    filtros = {
        'unidad_academica': request.GET.get('unidad_academica', ''),
        'carrera': request.GET.get('carrera', ''),
        'semestre': request.GET.get('semestre', ''),
        'tipo_insumo': request.GET.get('tipo_insumo', ''),
        'estado': request.GET.get('estado', ''),
        'laboratorio': request.GET.get('laboratorio', ''),
        'busqueda': request.GET.get('busqueda', ''),
        'stock_bajo': request.GET.get('stock_bajo', ''),
    }
    
    # Construir queryset con filtros
    insumos = Insumo.objects.all()
    
    if filtros['unidad_academica']:
        insumos = insumos.filter(unidad_academica_id=filtros['unidad_academica'])
    
    if filtros['carrera']:
        insumos = insumos.filter(carrera_id=filtros['carrera'])
    
    if filtros['semestre']:
        insumos = insumos.filter(semestre=filtros['semestre'])
    
    if filtros['tipo_insumo']:
        insumos = insumos.filter(tipo_insumo_id=filtros['tipo_insumo'])
    
    if filtros['estado']:
        insumos = insumos.filter(estado=filtros['estado'])
    
    if filtros['laboratorio']:
        insumos = insumos.filter(laboratorio_id=filtros['laboratorio'])
    
    if filtros['busqueda']:
        insumos = insumos.filter(
            Q(nombre__icontains=filtros['busqueda']) |
            Q(descripcion__icontains=filtros['busqueda']) |
            Q(marca__icontains=filtros['busqueda']) |
            Q(codigo_inventario__icontains=filtros['busqueda'])
        )
    
    if filtros['stock_bajo']:
        # Filtrar insumos con stock bajo (cantidad actual <= cantidad mínima)
        from django.db.models import F
        insumos = insumos.filter(cantidad_actual__lte=F('cantidad_minima'))
    
    # Ordenar por fecha de creación (más recientes primero)
    insumos = insumos.order_by('-created_at')
    
    # Paginación
    paginator = Paginator(insumos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Datos para los filtros
    unidades = UnidadAcademica.objects.all()
    carreras = Carrera.objects.all()
    tipos_insumos = TipoInsumo.objects.all()
    laboratorios = Laboratorio.objects.all()
    
    # Estadísticas
    stats = {
        'total': insumos.count(),
        'disponibles': insumos.filter(estado='disponible').count(),
        'agotados': insumos.filter(estado='agotado').count(),
        'vencidos': insumos.filter(estado='vencido').count(),
        'en_proceso': insumos.filter(estado='en_proceso').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'filtros': filtros,
        'unidades': unidades,
        'carreras': carreras,
        'tipos_insumos': tipos_insumos,
        'laboratorios': laboratorios,
        'stats': stats,
        'estados_choices': Insumo.ESTADOS,
        'semestres_choices': [(i, f"{i}° Semestre") for i in range(1, 11)],
    }
    
    return render(request, 'insumos/lista.html', context)

@login_required
def nuevo_insumo_view(request):
    """Vista para crear un nuevo insumo"""
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Crear el insumo con todos los datos del formulario
                insumo = Insumo.objects.create(
                    unidad_academica_id=request.POST.get('unidad_academica'),
                    carrera_id=request.POST.get('carrera'),
                    semestre=int(request.POST.get('semestre')),
                    asignatura_id=request.POST.get('asignatura'),
                    unidad_tematica_id=request.POST.get('unidad_tematica'),
                    guia_laboratorio_id=request.POST.get('guia_laboratorio'),
                    practica_id=request.POST.get('practica'),
                    tipo_insumo_id=request.POST.get('tipo_insumo'),
                    nombre=request.POST.get('nombre'),
                    descripcion=request.POST.get('descripcion', ''),
                    marca=request.POST.get('marca', ''),
                    modelo=request.POST.get('modelo', ''),
                    cantidad_actual=float(request.POST.get('cantidad_actual', 0)),
                    cantidad_minima=float(request.POST.get('cantidad_minima', 0)),
                    cantidad_requerida=float(request.POST.get('cantidad_requerida', 0)),
                    unidad_medida=request.POST.get('unidad_medida', 'unidades'),
                    estado=request.POST.get('estado', 'disponible'),
                    laboratorio_id=request.POST.get('laboratorio'),
                    ubicacion_especifica=request.POST.get('ubicacion_especifica', ''),
                    numero_lote=request.POST.get('numero_lote', ''),
                    proveedor=request.POST.get('proveedor', ''),
                    precio_unitario=float(request.POST.get('precio_unitario') or 0) if request.POST.get('precio_unitario') else None,
                    es_peligroso=request.POST.get('es_peligroso') == 'on',
                    notas_seguridad=request.POST.get('notas_seguridad', ''),
                    usuario_creador=request.user,
                    observaciones=request.POST.get('observaciones', ''),
                )
                
                # Manejar fecha de vencimiento
                if request.POST.get('fecha_vencimiento'):
                    from datetime import datetime
                    insumo.fecha_vencimiento = datetime.strptime(request.POST.get('fecha_vencimiento'), '%Y-%m-%d').date()
                
                # Manejar archivo de imagen
                if 'fotografia' in request.FILES:
                    insumo.fotografia = request.FILES['fotografia']
                
                insumo.save()
                
                # Registrar movimiento inicial si hay cantidad
                if insumo.cantidad_actual > 0:
                    MovimientoInsumo.objects.create(
                        insumo=insumo,
                        tipo='entrada',
                        cantidad=insumo.cantidad_actual,
                        cantidad_anterior=0,
                        cantidad_nueva=insumo.cantidad_actual,
                        motivo='Registro inicial del insumo',
                        usuario=request.user
                    )
                
                messages.success(request, f'Insumo "{insumo.nombre}" creado exitosamente.')
                return redirect('insumos:detalle', pk=insumo.pk)
                
        except Exception as e:
            messages.error(request, f'Error al crear el insumo: {str(e)}')
    
    # Datos para los formularios
    unidades = UnidadAcademica.objects.all()
    carreras = Carrera.objects.all()
    tipos_insumos = TipoInsumo.objects.all()
    laboratorios = Laboratorio.objects.all()
    
    context = {
        'unidades': unidades,
        'carreras': carreras,
        'tipos_insumos': tipos_insumos,
        'laboratorios': laboratorios,
        'estados_choices': Insumo.ESTADOS,
        'unidades_medida_choices': Insumo.UNIDADES_MEDIDA,
        'semestres_choices': [(i, f"{i}° Semestre") for i in range(1, 11)],
    }
    
    return render(request, 'insumos/nuevo.html', context)

@login_required
def detalle_insumo_view(request, pk):
    """Vista detalle de un insumo específico"""
    insumo = get_object_or_404(Insumo, pk=pk)
    
    # Obtener historial de movimientos
    movimientos = MovimientoInsumo.objects.filter(insumo=insumo).order_by('-fecha_movimiento')[:10]
    
    # Obtener solicitudes relacionadas
    solicitudes = SolicitudInsumo.objects.filter(insumo=insumo).order_by('-fecha_solicitud')[:10]
    
    # Verificar alertas
    alertas = []
    if insumo.esta_por_agotarse:
        alertas.append({
            'tipo': 'warning',
            'mensaje': f'Stock bajo: {insumo.cantidad_actual} {insumo.get_unidad_medida_display()} (mínimo: {insumo.cantidad_minima})'
        })
    
    if insumo.esta_vencido:
        alertas.append({
            'tipo': 'danger',
            'mensaje': f'Producto vencido desde {insumo.fecha_vencimiento.strftime("%d/%m/%Y")}'
        })
    
    context = {
        'insumo': insumo,
        'movimientos': movimientos,
        'solicitudes': solicitudes,
        'alertas': alertas,
    }
    
    return render(request, 'insumos/detalle.html', context)

@login_required
def solicitar_insumo_view(request, pk):
    """Vista para solicitar un insumo"""
    insumo = get_object_or_404(Insumo, pk=pk)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                solicitud = SolicitudInsumo.objects.create(
                    insumo=insumo,
                    cantidad_solicitada=float(request.POST.get('cantidad_solicitada')),
                    fecha_necesaria=request.POST.get('fecha_necesaria'),
                    solicitante=request.user,
                    justificacion=request.POST.get('justificacion'),
                    observaciones=request.POST.get('observaciones', '')
                )
                
                messages.success(request, f'Solicitud de {solicitud.cantidad_solicitada} {insumo.get_unidad_medida_display()} de "{insumo.nombre}" creada exitosamente.')
                return redirect('insumos:detalle', pk=insumo.pk)
                
        except Exception as e:
            messages.error(request, f'Error al crear la solicitud: {str(e)}')
    
    context = {
        'insumo': insumo,
    }
    
    return render(request, 'insumos/solicitar.html', context)

@login_required
def exportar_insumos_excel(request):
    """Exportar insumos a Excel"""
    
    # Obtener filtros si existen
    filtros = {
        'unidad_academica': request.GET.get('unidad_academica', ''),
        'carrera': request.GET.get('carrera', ''),
        'tipo_insumo': request.GET.get('tipo_insumo', ''),
        'estado': request.GET.get('estado', ''),
    }
    
    # Construir queryset
    insumos = Insumo.objects.select_related(
        'unidad_academica', 'carrera', 'asignatura', 'tipo_insumo',
        'laboratorio', 'usuario_creador'
    ).all()
    
    # Aplicar filtros
    if filtros['unidad_academica']:
        insumos = insumos.filter(unidad_academica_id=filtros['unidad_academica'])
    
    if filtros['carrera']:
        insumos = insumos.filter(carrera_id=filtros['carrera'])
    
    if filtros['tipo_insumo']:
        insumos = insumos.filter(tipo_insumo_id=filtros['tipo_insumo'])
    
    if filtros['estado']:
        insumos = insumos.filter(estado=filtros['estado'])
    
    # Crear workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Insumos de Laboratorio"
    
    # Definir estilos
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    border = Border(
        left=Side(border_style="thin"),
        right=Side(border_style="thin"),
        top=Side(border_style="thin"),
        bottom=Side(border_style="thin")
    )
    
    # Encabezados
    headers = [
        'CÓDIGO INVENTARIO',
        'UNIDAD ACADÉMICA',
        'CARRERA',
        'SEMESTRE',
        'ASIGNATURA',
        'TIPO DE INSUMO',
        'NOMBRE',
        'DESCRIPCIÓN',
        'MARCA',
        'MODELO',
        'CANTIDAD ACTUAL',
        'CANTIDAD MÍNIMA',
        'CANTIDAD REQUERIDA',
        'UNIDAD DE MEDIDA',
        'ESTADO',
        'LABORATORIO',
        'UBICACIÓN ESPECÍFICA',
        'FECHA VENCIMIENTO',
        'NÚMERO DE LOTE',
        'PROVEEDOR',
        'PRECIO UNITARIO',
        'ES PELIGROSO',
        'NOTAS DE SEGURIDAD',
        'FECHA CREACIÓN',
        'USUARIO CREADOR'
    ]
    
    # Escribir encabezados
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border
    
    # Escribir datos
    for row, insumo in enumerate(insumos, 2):
        data = [
            insumo.codigo_inventario,
            insumo.unidad_academica.get_nombre_display(),
            insumo.carrera.get_nombre_display(),
            f"{insumo.semestre}° Semestre",
            insumo.asignatura.get_nombre_display(),
            insumo.tipo_insumo.get_nombre_display(),
            insumo.nombre,
            insumo.descripcion,
            insumo.marca,
            insumo.modelo,
            insumo.cantidad_actual,
            insumo.cantidad_minima,
            insumo.cantidad_requerida,
            insumo.get_unidad_medida_display(),
            insumo.get_estado_display(),
            insumo.laboratorio.get_nombre_display(),
            insumo.ubicacion_especifica,
            insumo.fecha_vencimiento.strftime('%d/%m/%Y') if insumo.fecha_vencimiento else '',
            insumo.numero_lote,
            insumo.proveedor,
            float(insumo.precio_unitario) if insumo.precio_unitario else '',
            'Sí' if insumo.es_peligroso else 'No',
            insumo.notas_seguridad,
            insumo.created_at.strftime('%d/%m/%Y %H:%M'),
            insumo.usuario_creador.get_full_name() or insumo.usuario_creador.username,
        ]
        
        for col, value in enumerate(data, 1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.border = border
    
    # Ajustar ancho de columnas
    for col in range(1, len(headers) + 1):
        column_letter = get_column_letter(col)
        ws.column_dimensions[column_letter].width = 15
    
    # Crear respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    fecha_actual = timezone.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="insumos_laboratorio_{fecha_actual}.xlsx"'
    
    wb.save(response)
    return response
