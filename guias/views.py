from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
import os
import json
from datetime import datetime

# Importaciones para generación de documentos
try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor  # Agregar RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    DOCX_AVAILABLE = True
    REPORTLAB_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    REPORTLAB_AVAILABLE = False

from io import BytesIO

from core.models import Carrera, Asignatura
from .models import GuiaGenerada
from .forms import GuiaLaboratorioForm, GuiaFilterForm


@login_required
def lista_guias(request):
    """Vista para listar todas las guías de laboratorio"""
    
    # Filtros
    filter_form = GuiaFilterForm(request.GET)
    guias = GuiaGenerada.objects.all().select_related('carrera', 'asignatura', 'usuario_creador')
    
    # Aplicar filtros
    if filter_form.is_valid():
        if filter_form.cleaned_data['carrera']:
            guias = guias.filter(carrera=filter_form.cleaned_data['carrera'])
        if filter_form.cleaned_data['semestre']:
            guias = guias.filter(semestre=filter_form.cleaned_data['semestre'])
    
    # Búsqueda por texto
    buscar = request.GET.get('buscar')
    if buscar:
        guias = guias.filter(
            Q(titulo__icontains=buscar) |
            Q(asignatura__nombre__icontains=buscar) |
            Q(contenido_analitico__icontains=buscar)
        )
    
    # Ordenar por fecha de creación descendente
    guias = guias.order_by('-created_at')
    
    # Estadísticas
    total_guias = GuiaGenerada.objects.count()
    guias_con_word = GuiaGenerada.objects.exclude(archivo_word='').count()
    guias_con_pdf = GuiaGenerada.objects.exclude(archivo_pdf='').count()
    
    # Guías de este mes
    from datetime import datetime, timedelta
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    guias_este_mes = GuiaGenerada.objects.filter(created_at__gte=inicio_mes).count()
    
    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(guias, 12)  # 12 guías por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Opciones para filtros
    carreras = Carrera.objects.all()
    semestres = list(range(1, 11))  # Semestres 1-10
    
    # Datos adicionales para estadísticas
    guias_recientes = GuiaGenerada.objects.filter(created_at__gte=inicio_mes)
    
    context = {
        'guias': page_obj,  # Usar el objeto paginado
        'page_obj': page_obj,
        'filter_form': filter_form,
        'carreras': carreras,
        'semestres': semestres,
        'total_guias': total_guias,
        'guias_con_word': guias_con_word,
        'guias_con_pdf': guias_con_pdf,
        'guias_este_mes': guias_este_mes,
        'guias_recientes': guias_recientes,
    }
    
    return render(request, 'guias/lista.html', context)


@login_required
def nueva_guia(request):
    """Vista para crear una nueva guía de laboratorio"""
    
    if request.method == 'POST':
        form = GuiaLaboratorioForm(request.POST)
        if form.is_valid():
            try:
                guia = form.save(commit=False)
                guia.usuario_creador = request.user
                guia.save()
                
                # Generar documentos
                word_file = None
                pdf_file = None
                
                if DOCX_AVAILABLE:
                    word_file = generar_documento_word(guia)
                else:
                    messages.warning(request, 'No se pudo generar el archivo Word. Librería python-docx no disponible.')
                
                if REPORTLAB_AVAILABLE:
                    pdf_file = generar_documento_pdf(guia)
                else:
                    messages.warning(request, 'No se pudo generar el archivo PDF. Librería reportlab no disponible.')
                
                # Guardar archivos
                if word_file:
                    guia.archivo_word.save(
                        f'guia_{guia.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx',
                        word_file,
                        save=True
                    )
                
                if pdf_file:
                    guia.archivo_pdf.save(
                        f'guia_{guia.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
                        pdf_file,
                        save=True
                    )
                
                messages.success(request, 'Guía creada correctamente.')
                return redirect('guias:detalle', guia_id=guia.id)
                
            except Exception as e:
                messages.error(request, f'Error al crear la guía: {str(e)}')
        else:
            # Mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = GuiaLaboratorioForm()
    
    context = {
        'form': form,
        'title': 'Nueva Guía de Laboratorio'
    }
    
    return render(request, 'guias/nueva.html', context)


@login_required
def detalle_guia(request, guia_id):
    """Vista que redirige a la lista de guías"""
    return redirect('guias:lista')


@login_required
def eliminar_guia(request, guia_id):
    """Vista para eliminar una guía"""
    
    guia = get_object_or_404(GuiaGenerada, id=guia_id)
    
    if request.method == 'POST':
        titulo = guia.titulo
        
        # Eliminar archivos físicos si existen
        if guia.archivo_word and os.path.exists(guia.archivo_word.path):
            os.remove(guia.archivo_word.path)
        if guia.archivo_pdf and os.path.exists(guia.archivo_pdf.path):
            os.remove(guia.archivo_pdf.path)
            
        guia.delete()
        messages.success(request, f'Guía "{titulo}" eliminada exitosamente.')
        return redirect('guias:lista')
    
    return render(request, 'guias/eliminar.html', {'guia': guia})


@login_required
def descargar_word(request, guia_id):
    """Vista para descargar el archivo Word de una guía"""
    
    guia = get_object_or_404(GuiaGenerada, id=guia_id)
    
    if not guia.archivo_word:
        raise Http404("El archivo Word no está disponible")
    
    try:
        with open(guia.archivo_word.path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename="guia_{guia.id}_{guia.titulo[:30]}.docx"'
            return response
    except FileNotFoundError:
        raise Http404("El archivo no se encontró en el servidor")


@login_required
def descargar_pdf(request, guia_id):
    """Vista para descargar el archivo PDF de una guía"""
    
    guia = get_object_or_404(GuiaGenerada, id=guia_id)
    
    if not guia.archivo_pdf:
        raise Http404("El archivo PDF no está disponible")
    
    try:
        with open(guia.archivo_pdf.path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="guia_{guia.id}_{guia.titulo[:30]}.pdf"'
            return response
    except FileNotFoundError:
        raise Http404("El archivo no se encontró en el servidor")


# APIs para dropdowns dinámicos

def api_asignaturas(request):
    """API para obtener asignaturas filtradas por carrera"""
    
    carrera_id = request.GET.get('carrera')
    
    if carrera_id:
        asignaturas = Asignatura.objects.filter(carrera_id=carrera_id).order_by('semestre', 'nombre')
    else:
        asignaturas = Asignatura.objects.all().order_by('semestre', 'nombre')
    
    data = {
        'asignaturas': [
            {
                'id': asignatura.id, 
                'nombre': asignatura.get_nombre_display(), 
                'semestre': asignatura.semestre
            }
            for asignatura in asignaturas
        ]
    }
    
    return JsonResponse(data)


# Funciones auxiliares para generación de documentos

def generar_documento_word(guia):
    """Genera un documento Word con el formato oficial de la EMI"""
    if not DOCX_AVAILABLE:
        return None
        
    try:
        doc = Document()
        
        # Configurar márgenes del documento
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
        
        # ========== PÁGINA DE CARÁTULA ==========
        
        # Logo y encabezado de la institución (simulado con texto)
        header_table = doc.add_table(rows=1, cols=1)
        header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        header_cell = header_table.cell(0, 0)
        header_para = header_cell.paragraphs[0]
        
        # Título EMI
        run_emi = header_para.add_run('EMI')
        run_emi.font.name = 'Arial'
        run_emi.font.size = Pt(36)
        run_emi.font.bold = True
        run_emi.font.color.rgb = RGBColor(41, 84, 144)  # Azul EMI
        
        header_para.add_run('\n')
        
        # Subtítulo
        run_subtitle = header_para.add_run('ESCUELA MILITAR DE INGENIERÍA')
        run_subtitle.font.name = 'Arial'
        run_subtitle.font.size = Pt(14)
        run_subtitle.font.bold = True
        run_subtitle.font.color.rgb = RGBColor(41, 84, 144)
        
        header_para.add_run('\n')
        
        # Nombre del Mariscal
        run_name = header_para.add_run('Mcal. Antonio José de Sucre')
        run_name.font.name = 'Arial'
        run_name.font.size = Pt(12)
        run_name.font.color.rgb = RGBColor(41, 84, 144)
        
        header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Espacios
        doc.add_paragraph()
        doc.add_paragraph()
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Título principal de la guía
        titulo_principal = doc.add_paragraph('GUÍA DE LABORATORIO')
        titulo_principal.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in titulo_principal.runs:
            run.font.name = 'Arial'
            run.font.size = Pt(24)
            run.font.bold = True
        
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Nombre de la asignatura
        asignatura_para = doc.add_paragraph(f'NOMBRE DE LA ASIGNATURA: {guia.asignatura.nombre.upper()}')
        asignatura_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in asignatura_para.runs:
            run.font.name = 'Arial'
            run.font.size = Pt(16)
            run.font.bold = True
        
        # Línea decorativa
        line_para = doc.add_paragraph('_' * 50)
        line_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in line_para.runs:
            run.font.color.rgb = RGBColor(255, 193, 7)  # Amarillo EMI
            run.font.bold = True
        
        doc.add_paragraph()
        
        # Salto de página
        doc.add_page_break()
        
        # ========== PÁGINA DE CONTENIDO ==========
        
        # Encabezado con logo y título
        crear_encabezado_pagina(doc, "GUÍA DE LABORATORIO")
        
        doc.add_paragraph()
        
        # Título GUÍA DE LABORATORIO
        titulo_guia = doc.add_heading('GUÍA DE LABORATORIO', 1)
        titulo_guia.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph()
        
        # Título CONTENIDO
        contenido_title = doc.add_heading('CONTENIDO', 2)
        contenido_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Tabla de contenido
        contenido_table = doc.add_table(rows=11, cols=2)
        contenido_table.style = 'Table Grid'
        contenido_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Encabezados de la tabla
        contenido_table.cell(0, 0).text = 'PRÁCTICA'
        contenido_table.cell(0, 1).text = 'PÁGINA'
        
        # Formatear encabezados
        for i in range(2):
            cell = contenido_table.cell(0, i)
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Llenar contenido
        for i in range(1, 11):
            contenido_table.cell(i, 0).text = f'PL {i}.'
            contenido_table.cell(i, 1).text = 'Pág. 1'
            
            # Centrar contenido
            for j in range(2):
                contenido_table.cell(i, j).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Salto de página
        doc.add_page_break()
        
        # ========== PÁGINA PRINCIPAL ==========
        
        # Encabezado con logo y título
        crear_encabezado_pagina(doc, "GUÍA DE LABORATORIO")
        
        # Sección 1: DATOS GENERALES
        datos_title = doc.add_heading('1. DATOS GENERALES', 2)
        datos_title.runs[0].font.color.rgb = RGBColor(0, 0, 0)
        
        # Crear tabla de datos generales
        datos_table = doc.add_table(rows=9, cols=2)
        datos_table.style = 'Table Grid'
        
        # Datos para la tabla
        datos_info = [
            ('CARRERA:', guia.carrera.get_nombre_display()),
            ('SEMESTRE:', str(guia.semestre)),
            ('ASIGNATURA:', guia.asignatura.nombre),
            ('CONTENIDO ANALÍTICO:', guia.contenido_analitico),
            ('UNIDAD DIDÁCTICA:', guia.unidad_didactica),
            ('DOCENTE:', f'{guia.usuario_creador.first_name} {guia.usuario_creador.last_name}'),
            ('Correo Institucional:', ''),
            ('BIBLIOGRAFÍA DE REFERENCIA:', '-\n-\n-\n-'),
            ('', '')  # Fila en blanco
        ]
        
        # Llenar datos
        for i, (label, value) in enumerate(datos_info):
            cell_label = datos_table.cell(i, 0)
            cell_value = datos_table.cell(i, 1)
            
            cell_label.text = label
            cell_value.text = value
            
            # Formatear etiquetas en negrita
            if label:
                cell_label.paragraphs[0].runs[0].font.bold = True
        
        # Fila especial para práctica de laboratorio
        practica_row = datos_table.add_row()
        merged_cell = practica_row.cells[0].merge(practica_row.cells[1])
        merged_cell.text = f'PRÁCTICA DE LABORATORIO N°: ...... TÍTULO: {guia.titulo}'
        merged_cell.paragraphs[0].runs[0].font.bold = True
        
        doc.add_paragraph()
        
        # Secciones principales
        secciones = [
            ('2. COMPETENCIAS', True),
            ('3. CRITERIOS DE DESEMPEÑO', True), 
            ('4. OBJETIVO DE LA PRÁCTICA DE LABORATORIO', False),
            ('5. MATERIALES, HERRAMIENTAS Y EQUIPOS', False),
            ('6. PROCEDIMIENTO', True),
            ('7. CUESTIONARIO', True)
        ]
        
        for seccion_titulo, es_sombreada in secciones:
            # Título de sección
            seccion_heading = doc.add_heading(seccion_titulo, 2)
            seccion_heading.runs[0].font.color.rgb = RGBColor(0, 0, 0)
            
            if seccion_titulo == '5. MATERIALES, HERRAMIENTAS Y EQUIPOS':
                # Crear tabla de materiales especial
                crear_tabla_materiales(doc)
            else:
                # Agregar espacio para contenido
                content_para = doc.add_paragraph()
                if es_sombreada:
                    # Agregar sombreado ligero para secciones importantes
                    pass
                
                # Agregar espacio adicional
                doc.add_paragraph()
        
        doc.add_page_break()
        
        # ========== PÁGINA DE CONTINUACIÓN ==========
        crear_encabezado_pagina(doc, "GUÍA DE LABORATORIO")
        
        # Continuación de materiales
        reactivos_title = doc.add_paragraph('DETALLE REACTIVOS:')
        reactivos_title.runs[0].font.bold = True
        
        reactivos_table = doc.add_table(rows=5, cols=2)
        reactivos_table.style = 'Table Grid'
        
        # Encabezado
        reactivos_table.cell(0, 0).text = ''
        reactivos_table.cell(0, 1).text = 'CANTIDAD'
        reactivos_table.cell(0, 1).paragraphs[0].runs[0].font.bold = True
        reactivos_table.cell(0, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Herramientas
        doc.add_paragraph()
        herramientas_title = doc.add_paragraph('DETALLE HERRAMIENTAS')
        herramientas_title.runs[0].font.bold = True
        
        herramientas_table = doc.add_table(rows=8, cols=2)
        herramientas_table.style = 'Table Grid'
        
        # Encabezado
        herramientas_table.cell(0, 0).text = ''
        herramientas_table.cell(0, 1).text = 'CANTIDAD'
        herramientas_table.cell(0, 1).paragraphs[0].runs[0].font.bold = True
        herramientas_table.cell(0, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Secciones finales
        doc.add_paragraph()
        procedimiento_final = doc.add_heading('6. PROCEDIMIENTO', 2)
        doc.add_paragraph()
        doc.add_paragraph()
        doc.add_paragraph()
        
        cuestionario_final = doc.add_heading('7. CUESTIONARIO', 2) 
        doc.add_paragraph()
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Firma al final
        doc.add_paragraph()
        doc.add_paragraph()
        doc.add_paragraph()
        
        firma_nombre = doc.add_paragraph(f'{guia.usuario_creador.first_name} {guia.usuario_creador.last_name}'.upper())
        firma_nombre.alignment = WD_ALIGN_PARAGRAPH.CENTER
        firma_nombre.runs[0].font.bold = True
        
        firma_cargo = doc.add_paragraph(f'DOCENTE DE LABORATORIO DE LA ASIGNATURA ({guia.asignatura.nombre.upper()})')
        firma_cargo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Guardar en memoria
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        print(f"Error generando documento Word: {e}")
        return None


def crear_encabezado_pagina(doc, titulo_documento):
    """Crea el encabezado estándar de la EMI para páginas internas"""
    # Tabla del encabezado
    header_table = doc.add_table(rows=1, cols=3)
    header_table.style = 'Table Grid'
    
    # Logo EMI (celda izquierda)
    logo_cell = header_table.cell(0, 0)
    logo_para = logo_cell.paragraphs[0]
    logo_run = logo_para.add_run('EMI')
    logo_run.font.name = 'Arial'
    logo_run.font.size = Pt(14)
    logo_run.font.bold = True
    logo_run.font.color.rgb = RGBColor(41, 84, 144)
    
    logo_para.add_run('\n')
    subtitle_run = logo_para.add_run('ESCUELA MILITAR DE INGENIERÍA')
    subtitle_run.font.name = 'Arial'
    subtitle_run.font.size = Pt(8)
    subtitle_run.font.color.rgb = RGBColor(41, 84, 144)
    
    logo_para.add_run('\n')
    name_run = logo_para.add_run('Mcal. Antonio José de Sucre')
    name_run.font.name = 'Arial'
    name_run.font.size = Pt(7)
    name_run.font.color.rgb = RGBColor(41, 84, 144)
    
    # Título del documento (celda central)
    title_cell = header_table.cell(0, 1)
    title_para = title_cell.paragraphs[0]
    title_para.text = titulo_documento
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_para.runs[0]
    title_run.font.name = 'Arial'
    title_run.font.size = Pt(12)
    title_run.font.bold = True
    
    # Código y versión (celda derecha)
    code_cell = header_table.cell(0, 2)
    code_para = code_cell.paragraphs[0]
    code_para.text = 'Código:\nVersión: 1'
    code_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in code_para.runs:
        run.font.name = 'Arial'
        run.font.size = Pt(9)
    
    # Ajustar ancho de columnas
    header_table.columns[0].width = Inches(2.5)
    header_table.columns[1].width = Inches(3.5)
    header_table.columns[2].width = Inches(1.5)


def crear_tabla_materiales(doc):
    """Crea las tablas de materiales con el formato específico"""
    
    # Tabla de EQUIPOS
    equipos_title = doc.add_paragraph('DETALLE EQUIPOS:')
    equipos_title.runs[0].font.bold = True
    
    equipos_table = doc.add_table(rows=5, cols=2)
    equipos_table.style = 'Table Grid'
    
    # Encabezado
    equipos_table.cell(0, 0).text = ''
    equipos_table.cell(0, 1).text = 'CANTIDAD'
    equipos_table.cell(0, 1).paragraphs[0].runs[0].font.bold = True
    equipos_table.cell(0, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()
    
    # Tabla de MATERIALES
    materiales_title = doc.add_paragraph('DETALLE MATERIALES:')
    materiales_title.runs[0].font.bold = True
    
    materiales_table = doc.add_table(rows=5, cols=2)
    materiales_table.style = 'Table Grid'
    
    # Encabezado
    materiales_table.cell(0, 0).text = ''
    materiales_table.cell(0, 1).text = 'CANTIDAD'
    materiales_table.cell(0, 1).paragraphs[0].runs[0].font.bold = True
    materiales_table.cell(0, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER


def generar_documento_pdf(guia):
    """Genera un documento PDF con el formato oficial de la EMI"""
    if not REPORTLAB_AVAILABLE:
        return None
        
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        # Estilos personalizados
        styles = getSampleStyleSheet()
        
        # Estilo para el título EMI
        emi_title_style = ParagraphStyle(
            'EMITitle',
            parent=styles['Normal'],
            fontSize=36,
            textColor=colors.Color(41/255, 84/255, 144/255),  # Azul EMI
            alignment=1,  # Centrado
            fontName='Helvetica-Bold',
            spaceAfter=10
        )
        
        # Estilo para subtítulo EMI
        emi_subtitle_style = ParagraphStyle(
            'EMISubtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.Color(41/255, 84/255, 144/255),
            alignment=1,
            fontName='Helvetica-Bold',
            spaceAfter=5
        )
        
        # Estilo para nombre del mariscal
        mariscal_style = ParagraphStyle(
            'MariscalStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.Color(41/255, 84/255, 144/255),
            alignment=1,
            fontName='Helvetica',
            spaceAfter=20
        )
        
        # Estilo para título principal
        main_title_style = ParagraphStyle(
            'MainTitle',
            parent=styles['Heading1'],
            fontSize=24,
            alignment=1,
            fontName='Helvetica-Bold',
            spaceAfter=20
        )
        
        # Estilo para nombre de asignatura
        subject_style = ParagraphStyle(
            'SubjectStyle',
            parent=styles['Normal'],
            fontSize=16,
            alignment=1,
            fontName='Helvetica-Bold',
            spaceAfter=10
        )
        
        # Contenido del documento
        story = []
        
        # ========== PÁGINA DE CARÁTULA ==========
        
        # Logo y título EMI
        story.append(Paragraph("EMI", emi_title_style))
        story.append(Paragraph("ESCUELA MILITAR DE INGENIERÍA", emi_subtitle_style))
        story.append(Paragraph("Mcal. Antonio José de Sucre", mariscal_style))
        
        # Espacios
        story.append(Spacer(1, 50))
        
        # Título principal
        story.append(Paragraph("GUÍA DE LABORATORIO", main_title_style))
        story.append(Spacer(1, 30))
        
        # Nombre de asignatura
        story.append(Paragraph(f"NOMBRE DE LA ASIGNATURA: {guia.asignatura.nombre.upper()}", subject_style))
        
        # Línea decorativa
        story.append(Spacer(1, 10))
        story.append(Paragraph("_" * 50, ParagraphStyle('Line', alignment=1, textColor=colors.Color(255/255, 193/255, 7/255))))
        
        story.append(PageBreak())
        
        # ========== PÁGINA DE CONTENIDO ==========
        
        # Encabezado
        crear_encabezado_pdf(story, "GUÍA DE LABORATORIO")
        
        story.append(Paragraph("GUÍA DE LABORATORIO", styles['Heading1']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("CONTENIDO", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Tabla de contenido
        contenido_data = [['PRÁCTICA', 'PÁGINA']]
        for i in range(1, 11):
            contenido_data.append([f'PL {i}.', 'Pág. 1'])
        
        contenido_table = Table(contenido_data, colWidths=[4*inch, 2*inch])
        contenido_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(contenido_table)
        story.append(PageBreak())
        
        # ========== PÁGINA PRINCIPAL ==========
        
        # Encabezado
        crear_encabezado_pdf(story, "GUÍA DE LABORATORIO")
        
        # Datos generales
        story.append(Paragraph("1. DATOS GENERALES", styles['Heading2']))
        
        datos_data = [
            ['CARRERA:', guia.carrera.get_nombre_display()],
            ['SEMESTRE:', str(guia.semestre)],
            ['ASIGNATURA:', guia.asignatura.nombre],
            ['CONTENIDO ANALÍTICO:', guia.contenido_analitico],
            ['UNIDAD DIDÁCTICA:', guia.unidad_didactica],
            ['DOCENTE:', f'{guia.usuario_creador.first_name} {guia.usuario_creador.last_name}'],
            ['Correo Institucional:', ''],
            ['BIBLIOGRAFÍA DE REFERENCIA:', '-\n-\n-\n-']
        ]
        
        datos_table = Table(datos_data, colWidths=[2.5*inch, 4*inch])
        datos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(datos_table)
        story.append(Spacer(1, 12))
        
        # Práctica de laboratorio
        practica_data = [[f'PRÁCTICA DE LABORATORIO N°: ...... TÍTULO: {guia.titulo}']]
        practica_table = Table(practica_data, colWidths=[6.5*inch])
        practica_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(practica_table)
        story.append(Spacer(1, 20))
        
        # Secciones principales
        secciones = [
            '2. COMPETENCIAS',
            '3. CRITERIOS DE DESEMPEÑO',
            '4. OBJETIVO DE LA PRÁCTICA DE LABORATORIO',
            '5. MATERIALES, HERRAMIENTAS Y EQUIPOS'
        ]
        
        for seccion in secciones:
            story.append(Paragraph(seccion, styles['Heading2']))
            
            if seccion == '5. MATERIALES, HERRAMIENTAS Y EQUIPOS':
                # Tablas de materiales
                crear_tablas_materiales_pdf(story)
            else:
                story.append(Spacer(1, 30))
        
        story.append(PageBreak())
        
        # ========== PÁGINA DE CONTINUACIÓN ==========
        crear_encabezado_pdf(story, "GUÍA DE LABORATORIO")
        
        # Continuación de materiales y secciones finales
        story.append(Paragraph("DETALLE REACTIVOS:", ParagraphStyle('Bold', fontName='Helvetica-Bold')))
        
        reactivos_data = [['', 'CANTIDAD']] + [['', ''] for _ in range(4)]
        reactivos_table = Table(reactivos_data, colWidths=[4*inch, 2*inch])
        reactivos_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(reactivos_table)
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("DETALLE HERRAMIENTAS", ParagraphStyle('Bold', fontName='Helvetica-Bold')))
        
        herramientas_data = [['', 'CANTIDAD']] + [['', ''] for _ in range(7)]
        herramientas_table = Table(herramientas_data, colWidths=[4*inch, 2*inch])
        herramientas_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(herramientas_table)
        story.append(Spacer(1, 20))
        
        # Secciones finales
        story.append(Paragraph("6. PROCEDIMIENTO", styles['Heading2']))
        story.append(Spacer(1, 40))
        
        story.append(Paragraph("7. CUESTIONARIO", styles['Heading2']))
        story.append(Spacer(1, 60))
        
        # Firma
        story.append(Paragraph(f'{guia.usuario_creador.first_name} {guia.usuario_creador.last_name}'.upper(),
                              ParagraphStyle('signature', alignment=1, fontSize=12, fontName='Helvetica-Bold')))
        story.append(Paragraph(f'DOCENTE DE LABORATORIO DE LA ASIGNATURA ({guia.asignatura.nombre.upper()})',
                              ParagraphStyle('cargo', alignment=1, fontSize=10)))
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        print(f"Error generando documento PDF: {e}")
        return None


def crear_encabezado_pdf(story, titulo_documento):
    """Crea el encabezado estándar EMI para PDF"""
    header_data = [
        [
            Paragraph("EMI<br/>ESCUELA MILITAR DE INGENIERÍA<br/>Mcal. Antonio José de Sucre", 
                     ParagraphStyle('HeaderLogo', fontSize=8, textColor=colors.Color(41/255, 84/255, 144/255))),
            Paragraph(titulo_documento, 
                     ParagraphStyle('HeaderTitle', fontSize=12, fontName='Helvetica-Bold', alignment=1)),
            Paragraph("Código:<br/>Versión: 1", 
                     ParagraphStyle('HeaderCode', fontSize=9))
        ]
    ]
    
    header_table = Table(header_data, colWidths=[2.5*inch, 3.5*inch, 1.5*inch])
    header_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 20))


def crear_tablas_materiales_pdf(story):
    """Crea las tablas de materiales para PDF"""
    
    # Tabla de equipos
    story.append(Paragraph("DETALLE EQUIPOS:", ParagraphStyle('Bold', fontName='Helvetica-Bold')))
    
    equipos_data = [['', 'CANTIDAD']] + [['', ''] for _ in range(4)]
    equipos_table = Table(equipos_data, colWidths=[4*inch, 2*inch])
    equipos_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(equipos_table)
    story.append(Spacer(1, 15))
    
    # Tabla de materiales
    story.append(Paragraph("DETALLE MATERIALES:", ParagraphStyle('Bold', fontName='Helvetica-Bold')))
    
    materiales_data = [['', 'CANTIDAD']] + [['', ''] for _ in range(4)]
    materiales_table = Table(materiales_data, colWidths=[4*inch, 2*inch])
    materiales_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(materiales_table)
    story.append(Spacer(1, 15))
