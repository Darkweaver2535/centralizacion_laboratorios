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
    from htmldocx import HtmlToDocx  # Para convertir HTML de CKEditor a Word
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

from core.models import Carrera, Asignatura, ContenidoAnalitico, FundamentoTeorico, Procedimientos, CalculosResultados, Cuestionario
from .models import GuiaGenerada
from .forms import GuiaLaboratorioForm, GuiaFilterForm


# ============================================================
# FUNCIÓN HELPER PARA CONVERTIR HTML DE CKEDITOR A WORD
# ============================================================

def limpiar_html_para_word(html_content):
    """
    Limpia el HTML de CKEditor para evitar problemas al convertir a Word.
    Elimina scripts, estilos problemáticos y normaliza el contenido.
    Mantiene imágenes base64 para que funcionen en Word.
    """
    if not html_content or not html_content.strip():
        return ""
    
    from bs4 import BeautifulSoup
    import re
    
    try:
        # Parsear el HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Eliminar scripts y estilos que pueden causar problemas
        for tag in soup.find_all(['script', 'style']):
            tag.decompose()
        
        # Procesar imágenes para asegurar compatibilidad con Word
        for img in soup.find_all('img'):
            # Mantener atributos esenciales
            attrs_to_keep = {}
            
            if img.get('src'):
                src = img['src']
                attrs_to_keep['src'] = src
                
                # Para imágenes base64, asegurar que estén correctamente formateadas
                if src.startswith('data:image'):
                    img_size_mb = len(src) / (1024 * 1024)
                    
                    # Limitar tamaño a 10MB (antes era 50MB, muy grande para Word)
                    if len(src) > 10000000:  # 10MB
                        img.replace_with(soup.new_string(f'[Imagen muy grande ({img_size_mb:.1f} MB) - omitida]'))
                        continue
            
            if img.get('alt'):
                attrs_to_keep['alt'] = img['alt']
            
            # Manejar dimensiones de imagen
            if img.get('width'):
                attrs_to_keep['width'] = img['width']
            if img.get('height'):
                attrs_to_keep['height'] = img['height']
            
            # Si no tiene dimensiones, agregar un ancho por defecto razonable
            if 'width' not in attrs_to_keep and 'height' not in attrs_to_keep:
                attrs_to_keep['width'] = '400'  # Ancho por defecto en píxeles
            
            img.attrs = attrs_to_keep
        
        # Convertir de vuelta a string HTML limpio
        clean_html = str(soup)
        
        # Eliminar entidades HTML problemáticas
        clean_html = clean_html.replace('&nbsp;', ' ')
        
        return clean_html
        
    except Exception as e:
        # Si falla la limpieza, devolver el HTML original
        return html_content


def agregar_html_a_documento(doc, html_content, parser=None):
    """
    Convierte contenido HTML de CKEditor a formato Word y lo agrega al documento.
    Maneja correctamente imágenes base64, negritas, cursivas, tablas, etc.
    
    Args:
        doc: Documento de python-docx
        html_content: String con HTML generado por CKEditor
        parser: Instancia de HtmlToDocx (opcional, se crea si no se proporciona)
    
    Returns:
        El documento actualizado
    """
    if not html_content or not html_content.strip():
        return doc
    
    try:
        # Limpiar el HTML antes de convertir
        html_limpio = limpiar_html_para_word(html_content)
        
        if not html_limpio or not html_limpio.strip():
            return doc
        
        # Procesamiento especial para imágenes base64
        from bs4 import BeautifulSoup
        import base64
        import io
        from docx.shared import Inches
        import re
        
        soup = BeautifulSoup(html_limpio, 'html.parser')
        imagenes_encontradas = soup.find_all('img')
        
        # Convertir imágenes base64 a placeholders únicos
        image_map = {}
        contador_imagenes = 0
        
        for img in soup.find_all('img'):
            src = img.get('src', '')
            
            if src.startswith('data:image'):
                try:
                    # Extraer datos base64
                    if ',' in src:
                        header, encoded = src.split(',', 1)
                    else:
                        continue
                    
                    image_data = base64.b64decode(encoded)
                    
                    # Verificar tamaño de imagen
                    if len(image_data) > 10 * 1024 * 1024:  # 10 MB
                        continue
                    
                    # Crear stream de imagen
                    image_stream = io.BytesIO(image_data)
                    
                    # Determinar ancho
                    width_str = img.get('width', img.get('style', ''))
                    try:
                        # Intentar extraer ancho del atributo width o style
                        if 'width:' in width_str:
                            match = re.search(r'width:\s*(\d+)', width_str)
                            if match:
                                width_pixels = int(match.group(1))
                            else:
                                width_pixels = 400
                        elif width_str.endswith('px'):
                            width_pixels = int(width_str[:-2])
                        elif width_str.isdigit():
                            width_pixels = int(width_str)
                        else:
                            width_pixels = 400
                        
                        # Convertir píxeles a pulgadas (96 DPI)
                        width_inches = width_pixels / 96.0
                        
                        # Limitar ancho máximo a 6 pulgadas
                        if width_inches > 6:
                            width_inches = 6
                        if width_inches < 1:
                            width_inches = 4
                    except:
                        width_inches = 4  # Valor por defecto
                    
                    # Guardar datos de imagen con placeholder único
                    contador_imagenes += 1
                    placeholder = f"___IMAGE_PLACEHOLDER_{contador_imagenes}___"
                    image_map[placeholder] = {
                        'data': image_stream,
                        'width': width_inches
                    }
                    
                    # Reemplazar img con placeholder en un párrafo
                    new_tag = soup.new_tag('p')
                    new_tag.string = placeholder
                    img.replace_with(new_tag)
                    
                except Exception as e:
                    continue
        
        # Convertir el HTML con placeholders usando htmldocx
        html_con_placeholders = str(soup)
        
        # Crear parser si no se proporciona
        if parser is None:
            parser = HtmlToDocx()
        
        # Agregar el HTML al documento (con placeholders)
        parser.add_html_to_document(html_con_placeholders, doc)
        
        # Reemplazar placeholders con imágenes reales
        for paragraph in doc.paragraphs:
            for placeholder, img_data in image_map.items():
                if placeholder in paragraph.text:
                    # Limpiar el texto del placeholder
                    paragraph.text = ''
                    # Agregar la imagen en su lugar
                    run = paragraph.add_run()
                    run.add_picture(img_data['data'], width=Inches(img_data['width']))
        
    except Exception as e:
        # Si falla la conversión HTML, agregar como texto plano
        from bs4 import BeautifulSoup
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            texto_plano = soup.get_text(separator='\n')
            if texto_plano.strip():
                doc.add_paragraph(texto_plano)
        except:
            # Último recurso: agregar el HTML como está (truncado)
            doc.add_paragraph(str(html_content)[:500] + '...')
    
    return doc


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
                    from django.core.files.base import ContentFile
                    # Convertir BytesIO a ContentFile para Django
                    guia.archivo_word.save(
                        f'guia_{guia.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx',
                        ContentFile(word_file.getvalue()),
                        save=True
                    )
                
                if pdf_file:
                    from django.core.files.base import ContentFile
                    # Convertir BytesIO a ContentFile para Django
                    guia.archivo_pdf.save(
                        f'guia_{guia.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
                        ContentFile(pdf_file.getvalue()),
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
def editar_guia(request, guia_id):
    """Vista para editar una guía de laboratorio existente"""
    
    guia = get_object_or_404(GuiaGenerada, id=guia_id)
    
    # Verificar permisos: solo el creador o admin puede editar
    if not request.user.is_staff and guia.usuario_creador != request.user:
        messages.error(request, 'No tiene permisos para editar esta guía.')
        return redirect('guias:lista')
    
    if request.method == 'POST':
        form = GuiaLaboratorioForm(request.POST, instance=guia)
        if form.is_valid():
            try:
                guia = form.save(commit=False)
                # Mantener el usuario creador original
                guia.save()
                form.save_m2m()  # Guardar relaciones ManyToMany
                
                # Regenerar documentos Word y PDF
                word_file = None
                pdf_file = None
                
                if DOCX_AVAILABLE:
                    word_file = generar_documento_word(guia)
                else:
                    messages.warning(request, 'No se pudo regenerar el archivo Word.')
                
                if REPORTLAB_AVAILABLE:
                    pdf_file = generar_documento_pdf(guia)
                else:
                    messages.warning(request, 'No se pudo regenerar el archivo PDF.')
                
                # Actualizar archivos
                if word_file:
                    from django.core.files.base import ContentFile
                    guia.archivo_word.save(
                        f'guia_{guia.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx',
                        ContentFile(word_file.getvalue()),
                        save=True
                    )
                
                if pdf_file:
                    from django.core.files.base import ContentFile
                    guia.archivo_pdf.save(
                        f'guia_{guia.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
                        ContentFile(pdf_file.getvalue()),
                        save=True
                    )
                
                messages.success(request, 'Guía actualizada correctamente.')
                return redirect('guias:lista')
                
            except Exception as e:
                messages.error(request, f'Error al actualizar la guía: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = GuiaLaboratorioForm(instance=guia)
    
    context = {
        'form': form,
        'guia': guia,
        'title': f'Editar Guía: {guia.titulo}',
        'is_edit': True
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
        # Limpiar el título para el nombre del archivo (quitar caracteres especiales)
        import re
        titulo_limpio = re.sub(r'[^\w\s-]', '', guia.titulo)
        titulo_limpio = re.sub(r'[-\s]+', '_', titulo_limpio)
        filename = f"Guia_{titulo_limpio[:30]}.docx"
        
        # Leer el archivo
        with open(guia.archivo_word.path, 'rb') as f:
            file_content = f.read()
        
        # Crear respuesta con headers correctos
        response = HttpResponse(
            file_content,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
        # Agregar headers de descarga
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(file_content)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response
        
    except FileNotFoundError:
        raise Http404("El archivo no se encontró en el servidor")
    except Exception as e:
        raise Http404(f"Error al procesar el archivo: {str(e)}")


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
        
        # ========== SECCIONES CON CONTENIDO HTML DE CKEDITOR ==========
        
        try:
            # Crear parser HTML una sola vez para reutilizar
            html_parser = HtmlToDocx()
        except Exception as parser_error:
            html_parser = None
        
        # 6. PROCEDIMIENTO con contenido HTML
        doc.add_paragraph()
        procedimiento_heading = doc.add_heading('6. PROCEDIMIENTO', 2)
        
        # Obtener todos los procedimientos relacionados al contenido analítico de la guía
        if hasattr(guia, 'contenido_analitico_obj'):
            contenido_obj = guia.contenido_analitico_obj
        else:
            # Intentar obtener el contenido analítico por nombre
            try:
                # Buscar por nombre del contenido analítico
                contenido_obj = ContenidoAnalitico.objects.filter(
                    nombre=guia.contenido_analitico
                ).first()
                
                # Si no se encuentra por nombre, intentar por descripción
                if not contenido_obj:
                    contenido_obj = ContenidoAnalitico.objects.filter(
                        descripcion__icontains=guia.contenido_analitico
                    ).first()
                    
            except Exception as search_error:
                contenido_obj = None
        
        if contenido_obj:
            # Obtener y agregar FUNDAMENTOS TEÓRICOS
            fundamentos = FundamentoTeorico.objects.filter(contenido_analitico=contenido_obj).order_by('orden')
            if fundamentos.exists():
                doc.add_heading('Fundamentos Teóricos', 3)
                for fundamento in fundamentos:
                    # Título del fundamento
                    doc.add_heading(fundamento.titulo, 4)
                    # Contenido HTML del fundamento
                    if fundamento.contenido:
                        agregar_html_a_documento(doc, fundamento.contenido, html_parser)
                    # Referencias si existen
                    if fundamento.referencias:
                        doc.add_paragraph('Referencias:', style='Heading 5')
                        agregar_html_a_documento(doc, fundamento.referencias, html_parser)
                doc.add_paragraph()  # Espaciado
            
            # Obtener y agregar PROCEDIMIENTOS
            procedimientos = Procedimientos.objects.filter(contenido_analitico=contenido_obj).order_by('orden', 'numero_paso')
            if procedimientos.exists():
                for proc in procedimientos:
                    # Paso numerado
                    paso_titulo = doc.add_paragraph()
                    paso_run = paso_titulo.add_run(f"Paso {proc.numero_paso}: {proc.titulo_paso}")
                    paso_run.bold = True
                    paso_run.font.size = Pt(12)
                    
                    # Descripción HTML del procedimiento
                    if proc.descripcion:
                        agregar_html_a_documento(doc, proc.descripcion, html_parser)
                    
                    # Tiempo estimado si existe
                    if proc.tiempo_estimado:
                        tiempo_para = doc.add_paragraph()
                        tiempo_run = tiempo_para.add_run(f"⏱ Tiempo estimado: {proc.tiempo_estimado}")
                        tiempo_run.italic = True
                    
                    # Precauciones si existen
                    if proc.precauciones:
                        doc.add_paragraph('⚠️ Precauciones:', style='Heading 5')
                        agregar_html_a_documento(doc, proc.precauciones, html_parser)
                    
                    # Observaciones si existen
                    if proc.observaciones:
                        doc.add_paragraph('📝 Observaciones:', style='Heading 5')
                        agregar_html_a_documento(doc, proc.observaciones, html_parser)
                    
                    doc.add_paragraph()  # Espaciado entre pasos
            else:
                doc.add_paragraph("No se han definido procedimientos específicos para esta práctica.")
            
            # Obtener y agregar CÁLCULOS Y RESULTADOS
            calculos = CalculosResultados.objects.filter(contenido_analitico=contenido_obj).order_by('orden')
            if calculos.exists():
                doc.add_page_break()
                crear_encabezado_pagina(doc, "GUÍA DE LABORATORIO")
                doc.add_heading('CÁLCULOS Y RESULTADOS', 2)
                
                for calculo in calculos:
                    # Título del cálculo
                    doc.add_heading(calculo.titulo, 3)
                    
                    # Fórmula si existe
                    if calculo.formula:
                        formula_para = doc.add_paragraph()
                        formula_run = formula_para.add_run(f"📐 Fórmula: {calculo.formula}")
                        formula_run.font.name = 'Courier New'
                    
                    # Procedimiento de cálculo (HTML)
                    if calculo.procedimiento_calculo:
                        doc.add_paragraph('Procedimiento:', style='Heading 4')
                        agregar_html_a_documento(doc, calculo.procedimiento_calculo, html_parser)
                    
                    # Resultado esperado
                    if calculo.resultado_esperado:
                        resultado_para = doc.add_paragraph()
                        resultado_run = resultado_para.add_run(f"✓ Resultado esperado: {calculo.resultado_esperado}")
                        resultado_run.bold = True
                    
                    # Unidades
                    if calculo.unidades:
                        unidades_para = doc.add_paragraph(f"Unidades: {calculo.unidades}")
                    
                    # Margen de error
                    if calculo.margen_error:
                        margen_para = doc.add_paragraph(f"±Margen de error: {calculo.margen_error}")
                        margen_para.runs[0].italic = True
                    
                    doc.add_paragraph()  # Espaciado
        else:
            # Si no hay contenido analítico, dejar espacio en blanco
            doc.add_paragraph()
            doc.add_paragraph()
        
        # 7. CUESTIONARIO con contenido HTML
        doc.add_page_break()
        crear_encabezado_pagina(doc, "GUÍA DE LABORATORIO")
        cuestionario_heading = doc.add_heading('7. CUESTIONARIO', 2)
        
        if contenido_obj:
            # Obtener y agregar CUESTIONARIO
            preguntas = Cuestionario.objects.filter(contenido_analitico=contenido_obj).order_by('orden', 'numero_pregunta')
            if preguntas.exists():
                for pregunta in preguntas:
                    # Número y pregunta
                    pregunta_para = doc.add_paragraph()
                    numero_run = pregunta_para.add_run(f"{pregunta.numero_pregunta}. ")
                    numero_run.bold = True
                    
                    # Pregunta HTML
                    if pregunta.pregunta:
                        agregar_html_a_documento(doc, pregunta.pregunta, html_parser)
                    
                    # Tipo de pregunta
                    tipo_para = doc.add_paragraph(f"[{pregunta.get_tipo_pregunta_display()}]")
                    tipo_para.runs[0].italic = True
                    tipo_para.runs[0].font.size = Pt(9)
                    
                    # Respuesta esperada (si existe - para el docente)
                    if pregunta.respuesta_esperada:
                        doc.add_paragraph('💡 Respuesta esperada (guía docente):', style='Heading 5')
                        agregar_html_a_documento(doc, pregunta.respuesta_esperada, html_parser)
                    
                    # Puntuación
                    if pregunta.puntuacion:
                        puntos_para = doc.add_paragraph(f"Puntuación: {pregunta.puntuacion} pts")
                        puntos_para.runs[0].font.size = Pt(9)
                    
                    doc.add_paragraph()  # Espaciado entre preguntas
            else:
                doc.add_paragraph("No se han definido preguntas de cuestionario para esta práctica.")
        else:
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
        
        # ========== GUARDAR DOCUMENTO CON VALIDACIÓN ==========
        try:
            # Guardar en memoria
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            # Validar que el buffer tiene contenido
            buffer_size = buffer.getbuffer().nbytes
            if buffer_size == 0:
                print("❌ Error: El documento generado está vacío")
                return None
            
            print(f"✅ Documento Word generado exitosamente: {buffer_size} bytes")
            return buffer
            
        except Exception as save_error:
            print(f"❌ Error al guardar documento Word: {save_error}")
            import traceback
            traceback.print_exc()
            return None
        
    except Exception as e:
        print(f"❌ Error general generando documento Word: {e}")
        import traceback
        traceback.print_exc()
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


# === NUEVAS VISTAS PARA FUNCIONALIDAD AVANZADA DE GUÍAS ===

@login_required
def generar_guia_pdf_completa(request, guia_id):
    """Genera PDF completo con todos los datos de la guía de laboratorio"""
    
    if not REPORTLAB_AVAILABLE:
        return JsonResponse({'error': 'ReportLab no está disponible'}, status=500)
    
    guia = get_object_or_404(GuiaGenerada, id=guia_id)
    
    # Crear el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=1,  # Centrado
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=12,
        textColor=colors.darkgreen
    )
    
    normal_style = styles['Normal']
    
    story = []
    
    # === TÍTULO PRINCIPAL ===
    story.append(Paragraph("GUÍA DE LABORATORIO", title_style))
    story.append(Paragraph(f"<b>{guia.titulo}</b>", title_style))
    story.append(Spacer(1, 20))
    
    # === INFORMACIÓN INSTITUCIONAL ===
    story.append(Paragraph("DATOS INSTITUCIONALES", heading_style))
    
    # Información básica en tabla
    datos_institucionales = [
        ['Unidad Académica:', guia.carrera.unidad_academica.get_nombre_display()],
        ['Carrera:', guia.carrera.get_nombre_display()],
        ['Asignatura:', guia.asignatura.get_nombre_display()],
        ['Semestre:', f"{guia.semestre}° Semestre"],
        ['Tipo de Práctica:', guia.get_tipo_practica_display()],
        ['Duración:', f"{guia.duracion_horas} horas"],
        ['Número de Práctica:', str(guia.numero_practica)],
    ]
    
    datos_table = Table(datos_institucionales, colWidths=[2*inch, 4*inch])
    datos_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    story.append(datos_table)
    story.append(Spacer(1, 20))
    
    # === DATOS DE LA ASIGNATURA ===
    story.append(Paragraph("DATOS DE LA ASIGNATURA", heading_style))
    
    # Información curricular
    if hasattr(guia, 'codigo_competencia') and guia.codigo_competencia:
        story.append(Paragraph(f"<b>Código de Competencia:</b> {guia.codigo_competencia}", normal_style))
    if hasattr(guia, 'sigla_curricular') and guia.sigla_curricular:
        story.append(Paragraph(f"<b>Sigla Curricular:</b> {guia.sigla_curricular}", normal_style))
    if hasattr(guia, 'carga_horaria_semestral') and guia.carga_horaria_semestral:
        story.append(Paragraph(f"<b>Carga Horaria Semestral:</b> {guia.carga_horaria_semestral} horas", normal_style))
    if hasattr(guia, 'carga_horaria_semanal') and guia.carga_horaria_semanal:
        story.append(Paragraph(f"<b>Carga Horaria Semanal:</b> {guia.carga_horaria_semanal} horas", normal_style))
    
    story.append(Spacer(1, 15))
    
    # === UNIDAD DIDÁCTICA ===
    story.append(Paragraph("UNIDAD DIDÁCTICA", heading_style))
    story.append(Paragraph(guia.unidad_didactica or "No especificada", normal_style))
    story.append(Spacer(1, 15))
    
    # === CONTENIDO ANALÍTICO ===
    story.append(Paragraph("CONTENIDO ANALÍTICO", heading_style))
    story.append(Paragraph(guia.contenido_analitico or "No especificado", normal_style))
    story.append(Spacer(1, 15))
    
    # === BIBLIOGRAFÍA ===
    if guia.referencia_bibliografica:
        story.append(Paragraph("BIBLIOGRAFÍA", heading_style))
        story.append(Paragraph(guia.referencia_bibliografica, normal_style))
        story.append(Spacer(1, 15))
    
    # === PRÁCTICA DE LABORATORIO ===
    story.append(Paragraph("PRÁCTICA DE LABORATORIO", heading_style))
    
    # === COMPETENCIAS ===
    story.append(Paragraph("COMPETENCIAS", ParagraphStyle('SubHeading', parent=heading_style, fontSize=11)))
    story.append(Paragraph(guia.competencias or "No especificadas", normal_style))
    story.append(Spacer(1, 10))
    
    # === OBJETIVO ===
    story.append(Paragraph("OBJETIVO DE LA PRÁCTICA", ParagraphStyle('SubHeading', parent=heading_style, fontSize=11)))
    story.append(Paragraph("<b>Objetivo General:</b>", normal_style))
    story.append(Paragraph(guia.objetivo_general or "No especificado", normal_style))
    
    if guia.objetivos_especificos:
        story.append(Paragraph("<b>Objetivos Específicos:</b>", normal_style))
        story.append(Paragraph(guia.objetivos_especificos, normal_style))
    story.append(Spacer(1, 10))
    
    # === FUNDAMENTO TEÓRICO ===
    if hasattr(guia, 'fundamento_teorico') and guia.fundamento_teorico:
        story.append(Paragraph("FUNDAMENTO TEÓRICO", ParagraphStyle('SubHeading', parent=heading_style, fontSize=11)))
        story.append(Paragraph(guia.fundamento_teorico, normal_style))
        story.append(Spacer(1, 10))
    
    # === PROCEDIMIENTOS ===
    story.append(Paragraph("PROCEDIMIENTOS", ParagraphStyle('SubHeading', parent=heading_style, fontSize=11)))
    
    if guia.preparacion_previa:
        story.append(Paragraph("<b>Preparación Previa:</b>", normal_style))
        story.append(Paragraph(guia.preparacion_previa, normal_style))
        story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Procedimiento de la Práctica:</b>", normal_style))
    story.append(Paragraph(guia.procedimientos or "No especificado", normal_style))
    story.append(Spacer(1, 15))
    
    # === EQUIPOS ===
    story.append(Paragraph("EQUIPOS", ParagraphStyle('SubHeading', parent=heading_style, fontSize=11)))
    
    if guia.equipos_requeridos.exists():
        equipos_data = [['Equipo', 'Cantidad', 'Estado']]
        for equipo in guia.equipos_requeridos.all()[:10]:  # Limitar a 10 equipos
            equipos_data.append([
                equipo.equipo_existente or 'Sin nombre',
                str(equipo.numero_unidades) if hasattr(equipo, 'numero_unidades') else '1',
                equipo.get_estado_display() if equipo.estado else 'N/A'
            ])
        
        equipos_table = Table(equipos_data, colWidths=[3*inch, 1*inch, 1.5*inch])
        equipos_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ]))
        story.append(equipos_table)
    else:
        story.append(Paragraph("No se han especificado equipos para esta práctica.", normal_style))
    
    story.append(Spacer(1, 15))
    
    # === MATERIALES ===
    story.append(Paragraph("MATERIALES", ParagraphStyle('SubHeading', parent=heading_style, fontSize=11)))
    
    if guia.insumos_requeridos.exists():
        materiales_data = [['Material', 'Cantidad', 'Unidad']]
        for insumo in guia.insumos_requeridos.all()[:10]:  # Limitar a 10 materiales
            materiales_data.append([
                insumo.nombre_elemento or 'Sin nombre',
                str(insumo.cantidad),
                insumo.get_unidad_medida_display() if insumo.unidad_medida else 'unidades'
            ])
        
        materiales_table = Table(materiales_data, colWidths=[3*inch, 1*inch, 1.5*inch])
        materiales_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ]))
        story.append(materiales_table)
    else:
        story.append(Paragraph("No se han especificado materiales para esta práctica.", normal_style))
    
    story.append(Spacer(1, 15))
    
    # === HERRAMIENTAS ===
    story.append(Paragraph("HERRAMIENTAS", ParagraphStyle('SubHeading', parent=heading_style, fontSize=11)))
    
    # Filtrar herramientas de los insumos
    herramientas = guia.insumos_requeridos.filter(categoria='herramientas')
    if herramientas.exists():
        herramientas_data = [['Herramienta', 'Cantidad', 'Estado']]
        for herramienta in herramientas[:10]:
            herramientas_data.append([
                herramienta.nombre_elemento or 'Sin nombre',
                str(herramienta.cantidad),
                herramienta.get_estado_display() if herramienta.estado else 'N/A'
            ])
        
        herramientas_table = Table(herramientas_data, colWidths=[3*inch, 1*inch, 1.5*inch])
        herramientas_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightyellow),
        ]))
        story.append(herramientas_table)
    else:
        story.append(Paragraph("No se han especificado herramientas para esta práctica.", normal_style))
    
    story.append(Spacer(1, 20))
    
    # === CÁLCULOS Y RESULTADOS ===
    story.append(Paragraph("CÁLCULOS Y RESULTADOS", ParagraphStyle('SubHeading', parent=heading_style, fontSize=11)))
    
    # Espacio para completar
    calculo_data = [
        ['Descripción del Cálculo', 'Fórmula', 'Resultado'],
        ['', '', ''],
        ['', '', ''],
        ['', '', ''],
    ]
    
    calculo_table = Table(calculo_data, colWidths=[2*inch, 2*inch, 1.5*inch])
    calculo_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightcoral),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    story.append(calculo_table)
    story.append(Spacer(1, 20))
    
    # === CUESTIONARIO ===
    story.append(Paragraph("CUESTIONARIO", ParagraphStyle('SubHeading', parent=heading_style, fontSize=11)))
    story.append(Paragraph(guia.cuestionario or "No se ha definido cuestionario para esta práctica.", normal_style))
    
    # Generar PDF
    doc.build(story)
    
    # Preparar respuesta
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    filename = f"Guia_Laboratorio_{guia.titulo.replace(' ', '_')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required 
def detalle_guia_completa(request, guia_id):
    """Vista de detalle completa de la guía con todos los campos"""
    
    guia = get_object_or_404(GuiaGenerada, id=guia_id)
    
    context = {
        'guia': guia,
        'equipos': guia.equipos_requeridos.all()[:20],  # Limitar para rendimiento
        'materiales': guia.insumos_requeridos.filter(categoria__in=['materiales', 'reactivos'])[:20],
        'herramientas': guia.insumos_requeridos.filter(categoria='herramientas')[:20],
        'puede_editar': request.user == guia.usuario_creador or request.user.is_staff,
    }
    
    return render(request, 'guias/detalle_completa.html', context)


# ===== NUEVAS VISTAS PARA PRÁCTICAS DE LABORATORIO =====

@login_required
def generar_practica_word(request, practica_id):
    """Generar Word de una práctica usando plantilla con marcadores {{ variable }}"""
    
    if not DOCX_AVAILABLE:
        return JsonResponse({'error': 'python-docx no está disponible'}, status=500)
    
    from core.models import PracticaLaboratorio, FundamentoTeorico, Procedimientos, CalculosResultados, Cuestionario
    import os
    
    try:
        # Obtener la práctica
        practica = get_object_or_404(PracticaLaboratorio, id=practica_id)
        asignatura = practica.contenido_analitico.unidad_didactica.asignatura
        unidad = practica.contenido_analitico.unidad_didactica
        contenido = practica.contenido_analitico
        
        print(f"📄 Generando Word para práctica: {practica.nombre}")
        
        # Cargar plantilla
        plantilla_path = os.path.join(settings.BASE_DIR, 'pruebas', 'FORMATO GUÍA DE LABORATORIO.docx')
        
        if not os.path.exists(plantilla_path):
            return JsonResponse({'error': f'Plantilla no encontrada en {plantilla_path}'}, status=500)
        
        print(f"✅ Cargando plantilla: {plantilla_path}")
        doc = Document(plantilla_path)
        
        # === DATOS PARA REEMPLAZAR ===
        # NOTA: Los marcadores deben coincidir EXACTAMENTE con los de la plantilla
        
        # Obtener datos relacionados
        contenido = practica.contenido_analitico
        unidad = contenido.unidad_didactica if contenido else None
        
        replacements = {
            # Datos básicos
            '{{ nombre_de_la_asignatura }}': asignatura.nombre if asignatura else 'N/A',
            '{{ parte_indice }}': f"PL {practica.orden if practica.orden else 1}",
            '{{ pagina }}': '1',
            '{{ titulo }}': practica.nombre,
            '{{ numero_de_practica }}': str(practica.orden) if practica.orden else '1',
            
            # Asignatura y carrera
            '{{ carrera }}': asignatura.carrera.nombre if (asignatura and asignatura.carrera) else 'N/A',
            '{{ semestre }}': str(asignatura.semestre) if (asignatura and asignatura.semestre) else 'N/A',
            
            # Unidad didáctica
            '{{ unidad_didactica }}': unidad.nombre if unidad else 'N/A',
            
            # Contenido analítico
            '{{ contenido_analitico }}': contenido.nombre if contenido else 'N/A',
            
            # Práctica
            '{{ objetivo_de_la_practica }}': '',  # Se llenará en la tabla correspondiente
            '{{ competencias }}': '',  # Se llenará en la tabla correspondiente
            '{{ criterios_de_desempeno }}': '',  # Se llenará en la tabla correspondiente
            
            # Duración y estudiantes
            '{{ duracion }}': f"{practica.duracion_horas} horas" if practica.duracion_horas else 'N/A',
            '{{ numero_estudiantes }}': str(practica.numero_estudiantes) if practica.numero_estudiantes else 'Según capacidad',
            
            # Docente (si existe)
            '{{ docente }}': '',
            '{{ grado_y_nombre_de_docente }}': '',
            '{{correo_institucional_de_docente }}': '',
            
            # Contenido de las secciones (se llenan en las tablas)
            '{{ fundamento_teorico }}': '',
            '{{ procedimiento }}': '',
            '{{ calculos_resultados }}': '',
            '{{ cuestionario }}': '',
            '{{ bibliografía }}': '',
            
            # Equipos, materiales, herramientas (se llenan en tablas)
            '{{ equipo1 }}': '',
            '{{ equipo2 }}': '',
            '{{ equipo3 }}': '',
            '{{ cantidad_equipo1 }}': '',
            '{{ cantidad_equipo2 }}': '',
            '{{ cantidad_equipo3 }}': '',
            
            '{{ material1 }}': '',
            '{{ material2 }}': '',
            '{{ material3 }}': '',
            '{{ cantidad_material1 }}': '',
            '{{ cantidad_material2 }}': '',
            '{{ cantidad_material3 }}': '',
            
            '{{ herramienta1 }}': '',
            '{{ herramienta2}}': '',  # Nota: hay un espacio faltante en la plantilla
            '{{ herramienta3 }}': '',
            '{{ herramienta4 }}': '',
            '{{ herramienta5 }}': '',
            '{{ cantidad_herramienta1 }}': '',
            '{{ cantidad_herramienta2 }}': '',
            '{{ cantidad_herramienta3 }}': '',
            '{{ cantidad_herramienta4 }}': '',
            '{{ cantidad_herramienta5 }}': '',
            '{{ cantidad_herramienta6 }}': '',
            
            '{{ reactivo1 }}': '',
            '{{ reactivo2 }}': '',
            '{{ reactivo3 }}': '',
            '{{ reactivo4 }}': '',
            '{{ cantidad_ reactivo1 }}': '',  # Nota: hay un espacio en la plantilla
            '{{ cantidad_reactivo2 }}': '',
            '{{ cantidad_reactivo3 }}': '',
            '{{ cantidad_reactivo4 }}': '',
        }
        
        # Función mejorada para reemplazar texto en párrafos
        def reemplazar_en_parrafo(paragraph, replacements):
            """Reemplaza marcadores en un párrafo, manejando runs fragmentados"""
            texto_completo = paragraph.text
            
            # Verificar si hay algún marcador
            for key in replacements.keys():
                if key in texto_completo:
                    # Obtener el texto con reemplazos
                    nuevo_texto = texto_completo
                    for k, v in replacements.items():
                        nuevo_texto = nuevo_texto.replace(k, v)
                    
                    # Limpiar runs existentes
                    for run in paragraph.runs:
                        run.text = ''
                    
                    # Agregar el nuevo texto en el primer run
                    if paragraph.runs:
                        paragraph.runs[0].text = nuevo_texto
                    else:
                        paragraph.add_run(nuevo_texto)
                    
                    break  # Ya reemplazamos, no seguir iterando
        
        # Reemplazar en párrafos
        for paragraph in doc.paragraphs:
            reemplazar_en_parrafo(paragraph, replacements)
        
        # Reemplazar en tablas
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        reemplazar_en_parrafo(paragraph, replacements)
        
        # === RELLENAR SECCIONES ESPECÍFICAS ===
        
        # Inicializar parser HTML
        html_parser = None
        try:
            html_parser = HtmlToDocx()
            print("✅ Parser HTML creado")
        except Exception as e:
            print(f"⚠️ Error creando parser HTML: {e}")
        
        # Función auxiliar para agregar contenido HTML
        def agregar_html_a_celda(cell, html_content, limpiar=False):
            """Agrega contenido HTML a una celda de tabla con soporte completo de imágenes"""
            if not html_content:
                print("⚠️ Contenido HTML vacío")
                return
            
            print(f"📝 Procesando HTML ({len(html_content)} caracteres)")
            
            # Limpiar párrafos existentes si se solicita
            if limpiar:
                for p in cell.paragraphs:
                    p.clear()
            
            try:
                from bs4 import BeautifulSoup
                import base64
                import io
                from docx.shared import Inches
                import re
                
                # Limpiar HTML primero
                html_limpio = limpiar_html_para_word(html_content)
                soup = BeautifulSoup(html_limpio, 'html.parser')
                
                # Buscar todas las imágenes
                imagenes = soup.find_all('img')
                print(f"🖼️  Encontradas {len(imagenes)} imágenes")
                
                # Reemplazar cada imagen con un marcador único y guardar los datos
                image_data_map = {}
                for idx, img in enumerate(imagenes):
                    src = img.get('src', '')
                    if src.startswith('data:image'):
                        try:
                            # Extraer datos base64
                            if ',' in src:
                                header, encoded = src.split(',', 1)
                            else:
                                continue
                            
                            image_bytes = base64.b64decode(encoded)
                            print(f"📏 Imagen {idx+1}: {len(image_bytes)} bytes")
                            
                            if len(image_bytes) > 10 * 1024 * 1024:  # 10 MB
                                print(f"⚠️ Imagen {idx+1} demasiado grande, saltando")
                                continue
                            
                            # Determinar ancho
                            width_str = img.get('width', img.get('style', ''))
                            width_inches = 4  # Default
                            
                            try:
                                if 'width:' in str(width_str):
                                    match = re.search(r'width:\s*(\d+)', str(width_str))
                                    if match:
                                        width_pixels = int(match.group(1))
                                        width_inches = width_pixels / 96.0
                                elif str(width_str).replace('px', '').isdigit():
                                    width_pixels = int(str(width_str).replace('px', ''))
                                    width_inches = width_pixels / 96.0
                                
                                # Limitar ancho
                                width_inches = max(1, min(6, width_inches))
                            except:
                                pass
                            
                            # Crear marcador único
                            marker = f"___IMG_{idx}___"
                            
                            # Guardar datos de la imagen
                            image_data_map[marker] = {
                                'bytes': image_bytes,
                                'width': width_inches
                            }
                            
                            # Reemplazar imagen con marcador en un párrafo
                            new_p = soup.new_tag('p')
                            new_p.string = marker
                            img.replace_with(new_p)
                            
                            print(f"✅ Imagen {idx+1} marcada como {marker}")
                            
                        except Exception as e:
                            print(f"⚠️ Error procesando imagen {idx+1}: {e}")
                            continue
                
                # Convertir HTML modificado a string
                html_con_marcadores = str(soup)
                
                # Usar htmldocx para procesar el HTML (sin imágenes base64)
                if html_parser:
                    try:
                        # Crear documento temporal
                        from docx import Document
                        temp_doc = Document()
                        html_parser.add_html_to_document(html_con_marcadores, temp_doc)
                        
                        # Copiar párrafos al cell, reemplazando marcadores con imágenes
                        for para in temp_doc.paragraphs:
                            texto = para.text
                            
                            # Verificar si contiene un marcador de imagen
                            marcador_encontrado = None
                            for marker in image_data_map.keys():
                                if marker in texto:
                                    marcador_encontrado = marker
                                    break
                            
                            if marcador_encontrado:
                                # Crear párrafo con imagen
                                new_p = cell.add_paragraph()
                                img_data = image_data_map[marcador_encontrado]
                                
                                # Insertar imagen
                                run = new_p.add_run()
                                image_stream = io.BytesIO(img_data['bytes'])
                                run.add_picture(image_stream, width=Inches(img_data['width']))
                                print(f"✅ Imagen insertada en celda (marcador: {marcador_encontrado})")
                            else:
                                # Copiar párrafo normal
                                new_p = cell.add_paragraph()
                                new_p.alignment = para.alignment
                                
                                for run in para.runs:
                                    new_run = new_p.add_run(run.text)
                                    new_run.bold = run.bold
                                    new_run.italic = run.italic
                                    new_run.underline = run.underline
                        
                        print(f"✅ HTML procesado exitosamente")
                        
                    except Exception as e:
                        print(f"⚠️ Error procesando HTML con htmldocx: {e}")
                        import traceback
                        traceback.print_exc()
                        # Fallback a texto plano
                        p = cell.add_paragraph()
                        p.add_run(soup.get_text())
                else:
                    # Sin parser, usar texto plano
                    p = cell.add_paragraph()
                    p.add_run(soup.get_text())
                    
            except Exception as e:
                print(f"⚠️ Error general en agregar_html_a_celda: {e}")
                import traceback
                traceback.print_exc()
        
        # TABLA 2: COMPETENCIAS
        if len(doc.tables) > 2:
            competencias_cell = doc.tables[2].rows[1].cells[0]
            competencias = contenido.competencias.all() if hasattr(contenido, 'competencias') else []
            if competencias:
                texto_competencias = '\n'.join([f"• {comp.descripcion}" for comp in competencias])
                competencias_cell.text = texto_competencias
        
        # TABLA 3: CRITERIOS DE DESEMPEÑO (puede venir de objetivos)
        if len(doc.tables) > 3:
            criterios_cell = doc.tables[3].rows[1].cells[0]
            objetivos = contenido.objetivos_practica.all() if hasattr(contenido, 'objetivos_practica') else []
            if objetivos:
                texto_objetivos = '\n'.join([f"{i+1}. {obj.descripcion}" for i, obj in enumerate(objetivos)])
                criterios_cell.text = texto_objetivos
        
        # TABLA 4: OBJETIVOS
        if len(doc.tables) > 4:
            objetivos_cell = doc.tables[4].rows[1].cells[0]
            if objetivos:
                texto_objetivos = '\n'.join([f"• {obj.descripcion}" for obj in objetivos])
                objetivos_cell.text = texto_objetivos
        
        # TABLA 5: FUNDAMENTOS TEÓRICOS
        if len(doc.tables) > 5:
            fundamentos_cell = doc.tables[5].rows[1].cells[0]
            fundamentos = FundamentoTeorico.objects.filter(contenido_analitico=contenido).order_by('orden')
            if fundamentos.exists():
                # Limpiar celda primero
                for p in fundamentos_cell.paragraphs:
                    p.clear()
                
                for fund in fundamentos:
                    # Agregar título
                    p_titulo = fundamentos_cell.add_paragraph()
                    run_titulo = p_titulo.add_run(fund.titulo)
                    run_titulo.bold = True
                    run_titulo.font.size = Pt(12)
                    
                    # DEBUG: Verificar contenido antes de agregar
                    print(f"🔍 fund.titulo: {fund.titulo}, contenido length: {len(fund.contenido) if fund.contenido else 0}")
                    
                    # Agregar contenido HTML sin limpiar
                    if fund.contenido:
                        agregar_html_a_celda(fundamentos_cell, fund.contenido, limpiar=False)
                    
                    # Agregar referencias si existen
                    if fund.referencias:
                        p_ref = fundamentos_cell.add_paragraph()
                        run_ref = p_ref.add_run('Referencias:')
                        run_ref.bold = True
                        agregar_html_a_celda(fundamentos_cell, fund.referencias, limpiar=False)
        
        # TABLA 6: MATERIALES, HERRAMIENTAS Y EQUIPOS
        if len(doc.tables) > 6:
            materiales_table = doc.tables[6]
            materiales_equipos = contenido.materiales_herramientas_equipos.all() if hasattr(contenido, 'materiales_herramientas_equipos') else []
            
            # Limpiar filas existentes (excepto encabezado)
            for _ in range(len(materiales_table.rows) - 1):
                materiales_table._element.remove(materiales_table.rows[-1]._element)
            
            # Agregar datos
            if materiales_equipos:
                for item in materiales_equipos:
                    row = materiales_table.add_row()
                    row.cells[0].text = item.nombre
                    row.cells[1].text = item.cantidad or '1'
        
        # TABLA 7: PROCEDIMIENTO
        if len(doc.tables) > 7:
            procedimiento_cell = doc.tables[7].rows[1].cells[0]
            procedimientos = Procedimientos.objects.filter(contenido_analitico=contenido).order_by('orden', 'numero_paso')
            
            if procedimientos.exists():
                # Limpiar celda
                for p in procedimiento_cell.paragraphs:
                    p.clear()
                
                for proc in procedimientos:
                    # Título del paso
                    p_paso = procedimiento_cell.add_paragraph()
                    run_paso = p_paso.add_run(f"Paso {proc.numero_paso}: {proc.titulo_paso}")
                    run_paso.bold = True
                    run_paso.font.size = Pt(11)
                    
                    # Descripción con HTML
                    if proc.descripcion:
                        agregar_html_a_celda(procedimiento_cell, proc.descripcion, limpiar=False)
                    
                    # Tiempo estimado
                    if proc.tiempo_estimado:
                        p_tiempo = procedimiento_cell.add_paragraph()
                        run_tiempo = p_tiempo.add_run(f"⏱ Tiempo estimado: {proc.tiempo_estimado}")
                        run_tiempo.italic = True
                    
                    # Precauciones
                    if proc.precauciones:
                        p_prec = procedimiento_cell.add_paragraph()
                        run_prec = p_prec.add_run('⚠️ Precauciones:')
                        run_prec.bold = True
                        agregar_html_a_celda(procedimiento_cell, proc.precauciones, limpiar=False)
        
        # TABLA 8: CÁLCULOS Y RESULTADOS
        if len(doc.tables) > 8:
            calculos_cell = doc.tables[8].rows[1].cells[0]
            calculos = CalculosResultados.objects.filter(contenido_analitico=contenido).order_by('orden')
            
            if calculos.exists():
                # Limpiar celda
                for p in calculos_cell.paragraphs:
                    p.clear()
                
                for calc in calculos:
                    # Título
                    p_titulo = calculos_cell.add_paragraph()
                    run_titulo = p_titulo.add_run(calc.titulo)
                    run_titulo.bold = True
                    run_titulo.font.size = Pt(11)
                    
                    # Fórmula
                    if calc.formula:
                        p_formula = calculos_cell.add_paragraph()
                        run_formula = p_formula.add_run(f"📐 Fórmula: {calc.formula}")
                        run_formula.font.name = 'Courier New'
                    
                    # Procedimiento de cálculo con HTML
                    if calc.procedimiento_calculo:
                        agregar_html_a_celda(calculos_cell, calc.procedimiento_calculo, limpiar=False)
                    
                    # Resultado esperado
                    if calc.resultado_esperado:
                        p_resultado = calculos_cell.add_paragraph()
                        run_resultado = p_resultado.add_run(f"✓ Resultado esperado: {calc.resultado_esperado}")
                        run_resultado.bold = True
        
        # TABLA 9: CUESTIONARIO
        if len(doc.tables) > 9:
            cuestionario_cell = doc.tables[9].rows[1].cells[0]
            cuestionarios = Cuestionario.objects.filter(contenido_analitico=contenido).order_by('orden', 'numero_pregunta')
            
            if cuestionarios.exists():
                # Limpiar celda
                for p in cuestionario_cell.paragraphs:
                    p.clear()
                
                for preg in cuestionarios:
                    # Número de pregunta
                    p_num = cuestionario_cell.add_paragraph()
                    run_num = p_num.add_run(f"{preg.numero_pregunta}. ")
                    run_num.bold = True
                    
                    # Pregunta con HTML
                    if preg.pregunta:
                        agregar_html_a_celda(cuestionario_cell, preg.pregunta, limpiar=False)
                    
                    # Tipo de pregunta
                    p_tipo = cuestionario_cell.add_paragraph()
                    run_tipo = p_tipo.add_run(f"[{preg.get_tipo_pregunta_display()}]")
                    run_tipo.italic = True
                    run_tipo.font.size = Pt(9)
                    
                    # Respuesta esperada (para guía docente)
                    if preg.respuesta_esperada:
                        p_resp = cuestionario_cell.add_paragraph()
                        run_resp = p_resp.add_run('💡 Respuesta esperada (guía docente):')
                        run_resp.bold = True
                        run_resp.font.size = Pt(9)
                        agregar_html_a_celda(cuestionario_cell, preg.respuesta_esperada)
        
        # === GUARDAR DOCUMENTO ===
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        # Validar tamaño
        buffer_size = buffer.getbuffer().nbytes
        if buffer_size == 0:
            print("❌ Documento vacío")
            return JsonResponse({'error': 'El documento está vacío'}, status=500)
        
        print(f"✅ Documento generado: {buffer_size} bytes")
        
        # Crear respuesta HTTP
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
        # Nombre de archivo
        import re
        titulo_limpio = re.sub(r'[^\w\s-]', '', practica.nombre)
        titulo_limpio = re.sub(r'[-\s]+', '_', titulo_limpio)
        filename = f"Guia_Lab_{titulo_limpio[:40]}.docx"
        
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = buffer_size
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def generar_practica_pdf(request, practica_id):
    """Generar PDF de una práctica de laboratorio (guía basada en práctica real)"""
    
    if not REPORTLAB_AVAILABLE:
        return JsonResponse({'error': 'ReportLab no está disponible'}, status=500)
    
    from core.models import PracticaLaboratorio
    
    # Obtener la práctica
    practica = get_object_or_404(PracticaLaboratorio, id=practica_id)
    asignatura = practica.contenido_analitico.unidad_didactica.asignatura
    unidad = practica.contenido_analitico.unidad_didactica
    contenido = practica.contenido_analitico
    
    # Crear respuesta HTTP con PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Guia_{practica.nombre.replace(" ", "_")}.pdf"'
    
    # Crear documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.darkblue,
        alignment=1  # Centrado
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkgreen
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6
    )
    
    # ===== CONTENIDO DEL PDF =====
    
    # Título principal
    story.append(Paragraph(f"GUÍA DE LABORATORIO", title_style))
    story.append(Paragraph(f"{practica.nombre.upper()}", title_style))
    story.append(Spacer(1, 20))
    
    # Información académica
    story.append(Paragraph("INFORMACIÓN ACADÉMICA", subtitle_style))
    
    data_academica = [
        ['Carrera:', asignatura.carrera],
        ['Asignatura:', asignatura.nombre],
        ['Semestre:', f"{asignatura.semestre}°"],
        ['Unidad Didáctica:', unidad.nombre],
        ['Duración:', f"{practica.duracion_horas} horas"],
        ['Tipo de Práctica:', practica.get_tipo_practica_display()],
        ['Número de Estudiantes:', str(practica.numero_estudiantes)],
    ]
    
    tabla_academica = Table(data_academica, colWidths=[2*inch, 4*inch])
    tabla_academica.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(tabla_academica)
    story.append(Spacer(1, 20))
    
    # Competencias
    competencias = contenido.competencias.all()
    if competencias.exists():
        story.append(Paragraph("COMPETENCIAS", subtitle_style))
        for i, competencia in enumerate(competencias, 1):
            story.append(Paragraph(f"{i}. {competencia.descripcion}", normal_style))
        story.append(Spacer(1, 15))
    
    # Objetivos de la práctica
    objetivos = contenido.objetivos_practica.all()
    if objetivos.exists():
        story.append(Paragraph("OBJETIVOS DE LA PRÁCTICA", subtitle_style))
        for i, objetivo in enumerate(objetivos, 1):
            story.append(Paragraph(f"{i}. {objetivo.descripcion}", normal_style))
        story.append(Spacer(1, 15))
    
    # Descripción del contenido analítico
    story.append(Paragraph("DESCRIPCIÓN", subtitle_style))
    story.append(Paragraph(contenido.descripcion, normal_style))
    story.append(Spacer(1, 20))
    
    # Información adicional
    story.append(Paragraph("INFORMACIÓN ADICIONAL", subtitle_style))
    
    info_adicional = [
        ['Fecha de generación:', timezone.now().strftime('%d/%m/%Y %H:%M')],
        ['Generado por:', request.user.get_full_name() or request.user.username],
        ['Sistema:', 'Centralización de Laboratorios - UMSA'],
    ]
    
    tabla_info = Table(info_adicional, colWidths=[2*inch, 4*inch])
    tabla_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(tabla_info)
    
    # Construir PDF
    doc.build(story)
    
    return response


@login_required
def detalle_practica_completa(request, practica_id):
    """Vista de detalle completa de una práctica de laboratorio"""
    
    from core.models import PracticaLaboratorio
    
    practica = get_object_or_404(PracticaLaboratorio, id=practica_id)
    asignatura = practica.contenido_analitico.unidad_didactica.asignatura
    unidad = practica.contenido_analitico.unidad_didactica
    contenido = practica.contenido_analitico
    
    context = {
        'practica': practica,
        'asignatura': asignatura,
        'unidad': unidad,
        'contenido': contenido,
        'competencias': contenido.competencias.all(),
        'objetivos': contenido.objetivos_practica.all(),
        'puede_editar': request.user.is_staff,  # Solo staff puede editar prácticas del currículo
    }
    
    return render(request, 'guias/detalle_practica_completa.html', context)
