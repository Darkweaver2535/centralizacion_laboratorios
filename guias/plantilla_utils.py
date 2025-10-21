"""
Utilidad para generar documentos PDF usando python-docx-template con la plantilla oficial de EMI
"""
import os
import io
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from docxtpl import DocxTemplate
from io import BytesIO

# Para conversión de Word a PDF
try:
    from docx2pdf import convert
    DOCX2PDF_AVAILABLE = True
except ImportError:
    DOCX2PDF_AVAILABLE = False


def generar_guia_word_desde_plantilla(guia):
    """
    Genera un documento Word usando la plantilla EMI (sin conversión a PDF)
    """
    try:
        # Generar documento Word directamente
        buffer_word = generar_guia_con_plantilla(guia)
        
        if buffer_word:
            print(f"✅ Documento Word generado exitosamente")
            return buffer_word
        else:
            print(f"❌ Error generando documento Word")
            return None
            
    except Exception as e:
        print(f"❌ Error en generar_guia_word_desde_plantilla: {e}")
        import traceback
        traceback.print_exc()
        return None


def generar_guia_pdf_desde_plantilla(guia):
    """
    Genera un documento PDF usando la plantilla EMI y convirtiendo de Word a PDF
    """
    import tempfile
    import os
    
    try:
        # Primero generar el documento Word
        buffer_word = generar_guia_con_plantilla(guia)
        
        if not buffer_word:
            return None, 'error'
            
        if not DOCX2PDF_AVAILABLE:
            print("⚠️ docx2pdf no disponible, retornando Word")
            return buffer_word, 'docx'
            
        # Crear archivos temporales
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_docx:
            temp_docx.write(buffer_word.getvalue())
            temp_docx_path = temp_docx.name
            
        temp_pdf_path = temp_docx_path.replace('.docx', '.pdf')
        
        try:
            # Convertir Word a PDF
            print(f"🔄 Convirtiendo Word a PDF...")
            convert(temp_docx_path, temp_pdf_path)
            
            # Verificar que el PDF se creó y tiene contenido
            if os.path.exists(temp_pdf_path) and os.path.getsize(temp_pdf_path) > 0:
                # Leer el PDF generado
                with open(temp_pdf_path, 'rb') as pdf_file:
                    pdf_buffer = BytesIO(pdf_file.read())
                    
                print(f"✅ PDF generado exitosamente")
                
                # Limpiar archivos temporales
                try:
                    os.unlink(temp_docx_path)
                    os.unlink(temp_pdf_path)
                except:
                    pass
                    
                return pdf_buffer, 'pdf'
            else:
                print(f"❌ PDF no se generó correctamente, retornando Word")
                # Limpiar archivos temporales
                try:
                    os.unlink(temp_docx_path)
                    if os.path.exists(temp_pdf_path):
                        os.unlink(temp_pdf_path)
                except:
                    pass
                return buffer_word, 'docx'
                
        except Exception as e:
            print(f"❌ Error convirtiendo a PDF: {e}")
            print(f"🔄 Retornando documento Word")
            # Limpiar archivos temporales
            try:
                os.unlink(temp_docx_path)
                if os.path.exists(temp_pdf_path):
                    os.unlink(temp_pdf_path)
            except:
                pass
            return buffer_word, 'docx'
            
    except Exception as e:
        print(f"❌ Error en generar_guia_pdf_desde_plantilla: {e}")
        return None, 'error'


def crear_guia_temporal_desde_practica(practica, usuario=None):
    """
    Crea una GuiaGenerada temporal a partir de una PracticaLaboratorio
    para usar con la plantilla EMI
    """
    from .models import GuiaGenerada
    from core.models import CriterioDesempeno
    from django.contrib.auth import get_user_model
    from equipos.models import Equipo
    from insumos.models import Insumo
    
    User = get_user_model()
    
    # Obtener datos de la práctica
    asignatura = practica.contenido_analitico.unidad_didactica.asignatura
    unidad = practica.contenido_analitico.unidad_didactica
    contenido = practica.contenido_analitico
    
    # Crear GuiaGenerada temporal (no guardar en BD)
    guia_temporal = GuiaGenerada()
    
    # Información básica
    guia_temporal.titulo = practica.nombre
    guia_temporal.asignatura = asignatura
    guia_temporal.carrera = asignatura.carrera
    guia_temporal.codigo_asignatura = getattr(asignatura, 'codigo', f"FIS-{asignatura.semestre}01")  # Generar código si no existe
    guia_temporal.numero_practica = 1
    guia_temporal.duracion_minutos = int(practica.duracion_horas * 60) if practica.duracion_horas else 120
    guia_temporal.numero_estudiantes = practica.numero_estudiantes or 20
    guia_temporal.semestre = asignatura.semestre
    guia_temporal.gestion = 2025
    
    # Mapear campos adicionales
    guia_temporal.unidad_didactica = unidad.nombre
    guia_temporal.contenido_analitico = contenido.descripcion
    
    # Usuario creador con datos mejorados
    if usuario:
        guia_temporal.usuario_creador = usuario
    else:
        try:
            usuario_existente = User.objects.first()
            if usuario_existente:
                guia_temporal.usuario_creador = usuario_existente
            else:
                # Crear usuario temporal con datos por defecto
                temp_user = User()
                temp_user.username = "docente_temporal"
                temp_user.first_name = "Dr./Ing."
                temp_user.last_name = "Docente EMI"
                temp_user.email = "docente@emi.edu.bo"
                guia_temporal.usuario_creador = temp_user
        except:
            temp_user = User()
            temp_user.username = "docente_temporal"
            temp_user.first_name = "Dr./Ing."
            temp_user.last_name = "Docente EMI"
            temp_user.email = "docente@emi.edu.bo"
            guia_temporal.usuario_creador = temp_user
    
    # Competencias y objetivos
    competencias_list = list(contenido.competencias.all())
    if competencias_list:
        guia_temporal.competencias = '\n'.join([f"• {comp.descripcion}" for comp in competencias_list])
    else:
        guia_temporal.competencias = "• Desarrollar habilidades prácticas en laboratorio\n• Aplicar conceptos teóricos en situaciones reales"
    
    objetivos_list = list(contenido.objetivos_practica.all())
    if objetivos_list:
        guia_temporal.objetivo_general = objetivos_list[0].descripcion if objetivos_list else "Aplicar los conceptos teóricos de la asignatura en práctica de laboratorio"
        if len(objetivos_list) > 1:
            guia_temporal.objetivos_especificos = '\n'.join([f"• {obj.descripcion}" for obj in objetivos_list[1:]])
        else:
            guia_temporal.objetivos_especificos = "• Familiarizarse con el equipo de laboratorio\n• Realizar mediciones precisas\n• Analizar resultados obtenidos"
    else:
        guia_temporal.objetivo_general = "Aplicar los conceptos teóricos de la asignatura en práctica de laboratorio"
        guia_temporal.objetivos_especificos = "• Familiarizarse con el equipo de laboratorio\n• Realizar mediciones precisas\n• Analizar resultados obtenidos"
    
    # Contenido académico mejorado
    guia_temporal.fundamentacion_teorica = contenido.descripcion or f"Fundamentos teóricos de {asignatura.get_nombre_display()}. Base conceptual necesaria para el desarrollo de la práctica de laboratorio."
    
    # Procedimiento desde el contenido disponible
    procedimiento_base = f"""
PROCEDIMIENTO DE LA PRÁCTICA: {practica.nombre}

1. PREPARACIÓN
   - Verificar que todos los equipos estén en buen estado
   - Revisar la disponibilidad de materiales e insumos
   - Organizar el espacio de trabajo

2. DESARROLLO
   - Seguir las instrucciones específicas de la práctica
   - Realizar las mediciones correspondientes
   - Registrar todos los datos obtenidos

3. FINALIZACIÓN
   - Limpiar y ordenar el área de trabajo
   - Entregar equipos en buen estado
   - Elaborar el informe correspondiente

Descripción específica: {contenido.descripcion}
"""
    guia_temporal.procedimiento = procedimiento_base.strip()
    
    # Parte experimental
    guia_temporal.parte_experimental = f"Desarrollo experimental de la práctica {practica.nombre} aplicando los conceptos de {unidad.nombre}."
    
    # Cálculos y resultados
    guia_temporal.resultados_esperados = "Se espera obtener mediciones precisas que permitan validar los conceptos teóricos estudiados. Los resultados deben ser analizados estadísticamente y comparados con valores teóricos."
    
    # Cuestionario
    cuestionario_base = f"""
CUESTIONARIO - {practica.nombre}

1. ¿Cuáles son los fundamentos teóricos que sustentan esta práctica?
2. ¿Qué equipos e instrumentos son necesarios para el desarrollo de la práctica?
3. ¿Cuáles son las principales fuentes de error en las mediciones realizadas?
4. ¿Cómo se pueden mejorar la precisión de los resultados obtenidos?
5. ¿Qué aplicaciones prácticas tienen los conceptos desarrollados en esta práctica?
"""
    guia_temporal.cuestionario = cuestionario_base.strip()
    
    # Conclusiones
    guia_temporal.conclusiones = f"La práctica de {practica.nombre} permite consolidar los conocimientos teóricos mediante la experimentación práctica, desarrollando habilidades de observación, medición y análisis de resultados."
    
    # Referencias bibliográficas
    bibliografia_default = f"""
REFERENCIAS BIBLIOGRÁFICAS

1. {asignatura.get_nombre_display()} - Manual de Laboratorio, EMI 2025
2. Textos especializados en {asignatura.get_nombre_display()}
3. Manuales de equipos de laboratorio
4. Normas de seguridad en laboratorio EMI
"""
    guia_temporal.referencias_bibliograficas = bibliografia_default.strip()
    
    # Criterios de desempeño
    try:
        criterios = CriterioDesempeno.objects.filter(
            content_type__model='practicalaboratorio',
            object_id=practica.id
        )
        if criterios.exists():
            guia_temporal.criterios_desempeno = '\n'.join([f"• {criterio.descripcion}" for criterio in criterios])
        else:
            criterios_default = """• Manejo adecuado de equipos e instrumentos de laboratorio
• Aplicación correcta de procedimientos experimentales
• Precisión en la toma de mediciones y datos
• Análisis crítico de resultados obtenidos
• Cumplimiento de normas de seguridad"""
            guia_temporal.criterios_desempeno = criterios_default
    except:
        criterios_default = """• Manejo adecuado de equipos e instrumentos de laboratorio
• Aplicación correcta de procedimientos experimentales
• Precisión en la toma de mediciones y datos
• Análisis crítico de resultados obtenidos
• Cumplimiento de normas de seguridad"""
        guia_temporal.criterios_desempeno = criterios_default
    
    # Asignar equipos e insumos específicos seleccionados por el usuario
    try:
        # Obtener equipos e insumos específicos del ContenidoAnalitico
        # Estos son los que el usuario seleccionó al crear la práctica
        from core.models import MaterialesHerramientasEquipos
        
        equipos_seleccionados = list(MaterialesHerramientasEquipos.objects.filter(
            contenido_analitico=contenido,
            tipo_elemento='equipo'
        ).order_by('orden'))
        
        materiales_seleccionados = list(MaterialesHerramientasEquipos.objects.filter(
            contenido_analitico=contenido,
            tipo_elemento='material'
        ).order_by('orden'))
        
        herramientas_seleccionadas = list(MaterialesHerramientasEquipos.objects.filter(
            contenido_analitico=contenido,
            tipo_elemento='herramienta'
        ).order_by('orden'))
        
        # Asignar a la guía temporal
        guia_temporal._equipos_temp = equipos_seleccionados
        guia_temporal._materiales_temp = materiales_seleccionados
        guia_temporal._herramientas_temp = herramientas_seleccionadas
        
        # También crear una lista combinada de insumos (para compatibilidad)
        guia_temporal._insumos_temp = materiales_seleccionados + herramientas_seleccionadas
        
        print(f"✅ Recursos específicos encontrados:")
        print(f"   - Equipos: {len(equipos_seleccionados)}")
        print(f"   - Materiales: {len(materiales_seleccionados)}")
        print(f"   - Herramientas: {len(herramientas_seleccionadas)}")
        
    except Exception as e:
        print(f"Warning: No se pudieron obtener equipos/insumos específicos: {e}")
        guia_temporal._equipos_temp = []
        guia_temporal._materiales_temp = []
        guia_temporal._herramientas_temp = []
        guia_temporal._insumos_temp = []
    
    return guia_temporal

def generar_guia_con_plantilla(guia):
    """
    Genera un documento Word usando la plantilla EMI manual corregida por el usuario
    """
    try:
        # Ruta de la plantilla EMI manual corregida por el usuario
        plantilla_path = os.path.join(
            settings.BASE_DIR, 
            'templates', 'core', 'plantilla_emi_manual_corregida.docx'
        )
        
        if not os.path.exists(plantilla_path):
            print(f"❌ Error: No se encontró la plantilla en {plantilla_path}")
            return None
            
        # Cargar plantilla
        doc = DocxTemplate(plantilla_path)
        
        # Preparar contexto
        contexto = preparar_contexto_plantilla(guia)
        
        # Renderizar con el contexto
        doc.render(contexto)
        
        # Crear buffer en memoria
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        print(f"❌ Error generando documento con plantilla: {e}")
        import traceback
        traceback.print_exc()
        return None

def preparar_contexto_plantilla(guia):
    """
    Prepara el contexto con todas las variables necesarias para la plantilla
    """
    # Datos básicos
    contexto = {
        'nombre_de_la_asignatura': guia.asignatura.get_nombre_display(),
        'carrera': guia.carrera.get_nombre_display(),
        'semestre': guia.semestre,
        'unidad_didactica': guia.unidad_didactica if hasattr(guia, 'unidad_didactica') and guia.unidad_didactica else '',
        'contenido_analitico': guia.contenido_analitico if hasattr(guia, 'contenido_analitico') and guia.contenido_analitico else '',
        'docente': f"{guia.usuario_creador.first_name} {guia.usuario_creador.last_name}".strip(),
        'correo_institucional_de_docente': guia.usuario_creador.email or 'docente@emi.edu.bo',
        'grado_y_nombre_de_docente': f"{guia.usuario_creador.first_name} {guia.usuario_creador.last_name}".strip(),
        'titulo': guia.titulo,
        'numero_de_practica': str(guia.numero_practica),
        'pagina': '1',
        'parte_indice': guia.titulo[:50],  # Título truncado para índice
        'bibliografía': guia.referencias_bibliograficas if guia.referencias_bibliograficas else obtener_bibliografia_default(),
        
        # Campos adicionales que estaban faltando
        'codigo': guia.codigo_asignatura if hasattr(guia, 'codigo_asignatura') and guia.codigo_asignatura else f"{guia.asignatura.get_nombre_display()[:3].upper()}-{guia.semestre}01",
        'version': '1.0',  # Versión del documento
    }
    
    # Datos específicos de la guía (usando los campos del modelo GuiaGenerada)
    contexto.update({
        'competencias': guia.competencias if guia.competencias else '',
        'criterios_de_desempeno': guia.criterios_desempeno if hasattr(guia, 'criterios_desempeno') and guia.criterios_desempeno else '',
        'objetivo_de_la_practica': guia.objetivo_general if guia.objetivo_general else '',
        'fundamento_teorico': guia.fundamentacion_teorica if guia.fundamentacion_teorica else '',
        'procedimiento': guia.procedimiento if guia.procedimiento else '',
        'calculos_resultados': guia.resultados_esperados if hasattr(guia, 'resultados_esperados') and guia.resultados_esperados else '',
        'cuestionario': guia.cuestionario if guia.cuestionario else '',
    })
    
    # Equipos, materiales, reactivos y herramientas
    equipos, materiales, reactivos, herramientas = obtener_recursos_guia(guia)
    
    # Añadir equipos (hasta 3)
    for i in range(1, 4):
        if i <= len(equipos):
            equipo = equipos[i-1]
            # Para MaterialesHerramientasEquipos el campo se llama 'nombre'
            nombre_equipo = getattr(equipo, 'nombre', getattr(equipo, 'equipo_existente', 'Equipo no especificado'))
            contexto[f'equipo{i}'] = nombre_equipo
            contexto[f'cantidad_equipo{i}'] = str(getattr(equipo, 'cantidad', getattr(equipo, 'numero_unidades', '1')))
        else:
            contexto[f'equipo{i}'] = ''
            contexto[f'cantidad_equipo{i}'] = ''
    
    # Añadir materiales (hasta 3)
    for i in range(1, 4):
        if i <= len(materiales):
            material = materiales[i-1]
            # Para MaterialesHerramientasEquipos el campo se llama 'nombre'
            nombre_material = getattr(material, 'nombre', getattr(material, 'nombre_elemento', 'Material no especificado'))
            contexto[f'material{i}'] = nombre_material
            contexto[f'cantidad_material{i}'] = str(getattr(material, 'cantidad', '1'))
        else:
            contexto[f'material{i}'] = ''
            contexto[f'cantidad_material{i}'] = ''
    
    # Añadir reactivos (hasta 4)
    for i in range(1, 5):
        if i <= len(reactivos):
            reactivo = reactivos[i-1]
            # Para MaterialesHerramientasEquipos el campo se llama 'nombre'
            nombre_reactivo = getattr(reactivo, 'nombre', getattr(reactivo, 'nombre_elemento', 'Reactivo no especificado'))
            contexto[f'reactivo{i}'] = nombre_reactivo
            # Manejar las inconsistencias en los nombres de variables de la plantilla
            if i == 1:
                contexto['cantidad_ reactivo1'] = str(getattr(reactivo, 'cantidad', '1'))
            else:
                contexto[f'cantidad_reactivo{i}'] = str(getattr(reactivo, 'cantidad', '1'))
        else:
            contexto[f'reactivo{i}'] = ''
            if i == 1:
                contexto['cantidad_ reactivo1'] = ''
            else:
                contexto[f'cantidad_reactivo{i}'] = ''
    
    # Añadir herramientas (hasta 6)
    for i in range(1, 7):
        if i <= len(herramientas):
            herramienta = herramientas[i-1]
            # Para MaterialesHerramientasEquipos el campo se llama 'nombre'
            nombre_herramienta = getattr(herramienta, 'nombre', getattr(herramienta, 'nombre_elemento', 'Herramienta no especificada'))
            contexto[f'herramienta{i}'] = nombre_herramienta
            contexto[f'cantidad_herramienta{i}'] = str(getattr(herramienta, 'cantidad', '1'))
        else:
            contexto[f'herramienta{i}'] = ''
            contexto[f'cantidad_herramienta{i}'] = ''
    
    return contexto

def obtener_bibliografia_default():
    """
    Obtiene la bibliografía por defecto para la guía
    """
    return """- Manual de Laboratorio de la Asignatura
- Bibliografía especializada según contenido
- Normas de seguridad del laboratorio
- Guías técnicas oficiales"""

def obtener_criterios_desempeno(guia):
    """
    Obtiene los criterios de desempeño relacionados con la asignatura
    """
    try:
        # Obtener criterios de desempeño de la asignatura
        from core.models import CriterioDesempeno
        criterios = CriterioDesempeno.objects.filter(asignatura=guia.asignatura)
        
        if criterios.exists():
            # Tomar los primeros criterios y formatearlos
            criterios_texto = []
            for criterio in criterios[:3]:  # Máximo 3 criterios
                criterios_texto.append(f"• {criterio.descripcion}")
            return "\n".join(criterios_texto)
        else:
            return "Criterios de desempeño específicos según contenido analítico de la asignatura."
            
    except Exception as e:
        print(f"Error obteniendo criterios: {e}")
        return "Criterios de desempeño según plan curricular."

def obtener_fundamento_teorico(guia):
    """
    Obtiene el fundamento teórico básico para la práctica
    """
    # Por ahora generamos un fundamento básico basado en la asignatura
    asignatura_nombre = guia.asignatura.get_nombre_display().lower()
    
    if 'fisica' in asignatura_nombre:
        return """Fundamentos de física aplicada a laboratorio. Conceptos teóricos esenciales para la comprensión de fenómenos físicos mediante experimentación práctica."""
    elif 'quimica' in asignatura_nombre:
        return """Fundamentos de química experimental. Principios teóricos de reacciones químicas, propiedades de la materia y métodos analíticos."""
    elif 'materiales' in asignatura_nombre:
        return """Fundamentos de ciencia de materiales. Propiedades mecánicas, térmicas y estructurales de materiales de ingeniería."""
    elif 'termodinamica' in asignatura_nombre:
        return """Fundamentos de termodinámica. Leyes termodinámicas, procesos térmicos y aplicaciones en ingeniería."""
    else:
        return f"""Fundamentos teóricos de {guia.asignatura.get_nombre_display()}. Base conceptual necesaria para el desarrollo de la práctica de laboratorio."""

def obtener_recursos_guia(guia):
    """
    Obtiene los equipos, materiales, reactivos y herramientas de la guía
    """
    try:
        # Si es una guía temporal (de PracticaLaboratorio), usar recursos específicos seleccionados
        if hasattr(guia, '_equipos_temp') and hasattr(guia, '_materiales_temp') and hasattr(guia, '_herramientas_temp'):
            equipos = guia._equipos_temp
            materiales = guia._materiales_temp
            herramientas = guia._herramientas_temp
            
            # Para reactivos, buscar entre los materiales (no hay tipo específico)
            reactivos = []  # Por ahora vacío, se puede expandir según necesidades
            
        else:
            # Para guías normales (no temporales), usar relaciones del modelo
            equipos = list(guia.equipos_requeridos.all())
            
            # Obtener todos los insumos y separarlos por categoría
            todos_insumos = list(guia.insumos_requeridos.all())
            materiales = []
            reactivos = []
            herramientas = []
            
            for insumo in todos_insumos:
                categoria = getattr(insumo, 'categoria', 'material').lower()
                if 'materiales' in categoria or 'material' in categoria:
                    materiales.append(insumo)
                elif 'reactivos' in categoria or 'reactivo' in categoria or 'químico' in categoria:
                    reactivos.append(insumo)
                elif 'herramientas' in categoria or 'herramienta' in categoria:
                    herramientas.append(insumo)
                else:
                    # Por defecto agregar a materiales
                    materiales.append(insumo)
        
        return equipos, materiales, reactivos, herramientas
        
    except Exception as e:
        print(f"Error obteniendo recursos: {e}")
        return [], [], [], []

def generar_response_docx(guia, filename=None):
    """
    Genera un HttpResponse con el documento Word para descarga
    """
    buffer = generar_guia_con_plantilla(guia)
    
    if not buffer:
        return None
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Guia_Laboratorio_{guia.asignatura.nombre}_{timestamp}.docx"
    
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response