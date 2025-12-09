"""
Script temporal para probar generación LaTeX de prácticas
Luego se integra en views.py
"""

import os
import sys

# Configurar Django PRIMERO
sys.path.insert(0, '/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')

import django
django.setup()

# Ahora importar modelos Django
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from core.models import (
    PracticaLaboratorio, FundamentoTeorico, Procedimientos, 
    CalculosResultados, Cuestionario, Competencias, ObjetivoPractica
)
import subprocess
import tempfile
import shutil
from pathlib import Path


def html_to_latex(html_content):
    """Convierte HTML de CKEditor a LaTeX"""
    if not html_content:
        return ""
    
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    
    # Escapar caracteres especiales de LaTeX
    replacements = {
        '\\': '\\textbackslash{}',
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '~': '\\textasciitilde{}',
        '^': '\\textasciicircum{}',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Convertir saltos de línea
    text = text.replace('\n\n', '\n\n\\par ')
    
    return text


def generar_latex_practica(practica_id):
    """Genera PDF con LaTeX de una práctica - VERSIÓN COMPLETA CON TODAS LAS SECCIONES"""
    
    # Obtener la práctica y modelos relacionados
    from core.models import MaterialesHerramientasEquipos, Bibliografia
    
    practica = get_object_or_404(PracticaLaboratorio, id=practica_id)
    asignatura = practica.contenido_analitico.unidad_didactica.asignatura
    unidad = practica.contenido_analitico.unidad_didactica
    contenido = practica.contenido_analitico
    
    print(f"📄 Generando PDF LaTeX para práctica: {practica.nombre}")
    print(f"   Contenido Analítico: {contenido.nombre}")
    print(f"   Unidad Didáctica: {unidad.nombre if unidad else 'N/A'}")
    
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    tex_file = os.path.join(temp_dir, 'practica.tex')
    
    # Generar contenido LaTeX
    latex_content = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{array}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{tcolorbox}

% Configuración de página
\geometry{a4paper, left=2.5cm, right=2.5cm, top=2.5cm, bottom=2.5cm}

% Colores EMI
\definecolor{emiazul}{RGB}{0,46,93}
\definecolor{emidorado}{RGB}{255,215,0}
\definecolor{emigris}{RGB}{245,245,245}

% Formato de secciones
\titleformat{\section}
  {\normalfont\Large\bfseries\color{emiazul}}{\thesection}{1em}{}
  [\titlerule]
  
\titleformat{\subsection}
  {\normalfont\large\bfseries\color{emiazul}}{\thesubsection}{1em}{}

% Encabezado y pie de página
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\textbf{EMI - """ + (asignatura.carrera.nombre if (asignatura and asignatura.carrera) else 'N/A') + r"""}}
\fancyhead[R]{\small\textbf{Práctica """ + str(practica.orden if practica.orden else 1) + r"""}}
\fancyfoot[C]{\thepage}

\begin{document}

% ============================================================
% PORTADA Y ENCABEZADO EMI
% ============================================================
\begin{tcolorbox}[colback=emiazul,colframe=emiazul,arc=0mm,boxrule=0pt]
\begin{center}
\color{white}
\Large\textbf{ESCUELA MILITAR DE INGENIERÍA}\\[0.3cm]
\normalsize\textit{"Mcal. Antonio José de Sucre"}
\end{center}
\end{tcolorbox}

\begin{tcolorbox}[colback=emidorado,colframe=emidorado,arc=0mm,boxrule=0pt]
\begin{center}
\large\textbf{GUÍA DE LABORATORIO}
\end{center}
\end{tcolorbox}

\begin{tcolorbox}[colback=white,colframe=emiazul,arc=0mm,boxrule=1pt]
\textbf{ASIGNATURA:} """ + (asignatura.nombre if asignatura else 'N/A') + r"""
\end{tcolorbox}

\vspace{1cm}

% ============================================================
% 1. DATOS GENERALES
% ============================================================
\section{DATOS GENERALES}

\begin{tabular}{|>{\columncolor{emigris}}p{5cm}|p{10cm}|}
\hline
\textbf{CARRERA} & """ + (asignatura.carrera.get_nombre_display() if (asignatura and asignatura.carrera) else 'N/A') + r""" \\
\hline
\textbf{SEMESTRE} & """ + str(asignatura.semestre if (asignatura and asignatura.semestre) else 'N/A') + r""" \\
\hline
\textbf{ASIGNATURA} & """ + (asignatura.nombre if asignatura else 'N/A') + r""" \\
\hline
"""
    
    # Determinar qué mostrar como "Contenido Analítico"
    # Usar la descripción del contenido si es útil, sino usar el nombre de la unidad didáctica
    contenido_analitico_text = contenido.nombre
    if contenido.descripcion and not contenido.descripcion.startswith("Práctica de laboratorio:"):
        contenido_analitico_text = contenido.descripcion
    elif contenido.nombre == practica.nombre or (contenido.nombre in ['TITULOOOO', 'titulo', 'Título']):
        # Si el contenido tiene el mismo nombre que la práctica, mostrar la unidad didáctica
        contenido_analitico_text = f"{unidad.nombre}" if unidad else contenido.nombre
    
    latex_content += r"""\textbf{CONTENIDO ANALÍTICO} & """ + html_to_latex(contenido_analitico_text) + r""" \\
\hline
\textbf{UNIDAD DIDÁCTICA} & """ + html_to_latex(unidad.nombre if unidad else 'N/A') + r""" \\
\hline
\textbf{DOCENTE} & \rule{8cm}{0.4pt} \\
\hline
\textbf{Correo Institucional} & \rule{8cm}{0.4pt} \\
\hline
"""
    
    # Agregar bibliografía
    bibliografias = Bibliografia.objects.filter(contenido_analitico=contenido).order_by('orden')
    biblio_text = ""
    if bibliografias.exists():
        biblio_items = [html_to_latex(b.titulo) for b in bibliografias[:3]]
        biblio_text = ", ".join(biblio_items)
    else:
        biblio_text = "N/A"
    
    latex_content += r"""\textbf{BIBLIOGRAFÍA DE REFERENCIA} & """ + biblio_text + r""" \\
\hline
\end{tabular}

\vspace{0.5cm}

\begin{tcolorbox}[colback=emidorado,colframe=emiazul,arc=0mm,boxrule=1pt]
\begin{center}
\large\textbf{PRÁCTICA DE LABORATORIO N° """ + str(practica.orden if practica.orden else 1) + r"""}\\[0.3cm]
\Large\textbf{TÍTULO: """ + html_to_latex(practica.nombre.upper()) + r"""}
\end{center}
\end{tcolorbox}

\vspace{0.5cm}

"""
    
    # ============================================================
    # 2. COMPETENCIAS
    # ============================================================
    latex_content += r"""\section{COMPETENCIAS}

"""
    
    competencias = Competencias.objects.filter(contenido_analitico=contenido).order_by('orden')
    if competencias.exists():
        latex_content += r"\begin{itemize}[leftmargin=*]" + "\n"
        for comp in competencias:
            tipo_comp = comp.get_tipo_competencia_display() if hasattr(comp, 'tipo_competencia') else "Competencia"
            latex_content += f"\\item \\textbf{{{tipo_comp}}}: {html_to_latex(comp.descripcion)}\n"
        latex_content += r"\end{itemize}" + "\n\n"
    else:
        latex_content += "No hay competencias definidas para esta práctica.\n\n"
    
    # ============================================================
    # 3. CRITERIOS DE DESEMPEÑO
    # ============================================================
    latex_content += r"""\section{CRITERIOS DE DESEMPEÑO}

"""
    
    # Buscar criterios de desempeño - pueden estar como objetivos tipo 'desempeno'
    # O como todos los objetivos si no hay tipo específico
    criterios = ObjetivoPractica.objects.filter(contenido_analitico=contenido).order_by('orden')
    
    if criterios.exists():
        latex_content += r"\begin{enumerate}[leftmargin=*]" + "\n"
        for criterio in criterios:
            latex_content += f"\\item {html_to_latex(criterio.descripcion)}\n"
        latex_content += r"\end{enumerate}" + "\n\n"
    else:
        latex_content += "No hay criterios de desempeño definidos.\n\n"
    
    # ============================================================
    # 4. OBJETIVO DE LA PRÁCTICA DE LABORATORIO
    # ============================================================
    latex_content += r"""\section{OBJETIVO DE LA PRÁCTICA DE LABORATORIO}

"""
    
    objetivos = ObjetivoPractica.objects.filter(contenido_analitico=contenido).order_by('orden')
    
    if objetivos.exists():
        latex_content += r"\begin{itemize}[leftmargin=*]" + "\n"
        for obj in objetivos:
            tipo_display = obj.get_tipo_objetivo_display() if hasattr(obj, 'tipo_objetivo') else ""
            if tipo_display:
                latex_content += f"\\item \\textbf{{{tipo_display}}}: {html_to_latex(obj.descripcion)}\n"
            else:
                latex_content += f"\\item {html_to_latex(obj.descripcion)}\n"
        latex_content += r"\end{itemize}" + "\n\n"
    else:
        latex_content += "No hay objetivos definidos.\n\n"
    
    # ============================================================
    # 5. FUNDAMENTO TEÓRICO
    # ============================================================
    latex_content += r"""\section{FUNDAMENTO TEÓRICO}

"""
    
    fundamentos = FundamentoTeorico.objects.filter(contenido_analitico=contenido).order_by('orden')
    
    if fundamentos.exists():
        for fund in fundamentos:
            if fund.titulo:
                latex_content += f"\\subsection{{{html_to_latex(fund.titulo)}}}\n\n"
            latex_content += html_to_latex(fund.contenido) + "\n\n"
    else:
        latex_content += "No hay fundamento teórico definido.\n\n"
    
    # ============================================================
    # 6. MATERIALES, HERRAMIENTAS Y EQUIPOS
    # ============================================================
    latex_content += r"""\section{MATERIALES, HERRAMIENTAS Y EQUIPOS}

"""
    
    # Obtener todos los elementos agrupados por tipo
    equipos = MaterialesHerramientasEquipos.objects.filter(
        contenido_analitico=contenido, 
        tipo_elemento='equipo'
    ).order_by('orden')
    
    materiales = MaterialesHerramientasEquipos.objects.filter(
        contenido_analitico=contenido, 
        tipo_elemento='material'
    ).order_by('orden')
    
    herramientas = MaterialesHerramientasEquipos.objects.filter(
        contenido_analitico=contenido, 
        tipo_elemento='herramienta'
    ).order_by('orden')
    
    reactivos = MaterialesHerramientasEquipos.objects.filter(
        contenido_analitico=contenido, 
        tipo_elemento='reactivo'
    ).order_by('orden')
    
    # 6.1 Equipos
    if equipos.exists():
        latex_content += r"""\subsection{Equipos}

\begin{longtable}{|p{10cm}|p{3cm}|}
\hline
\textbf{Equipo} & \textbf{Cantidad} \\
\hline
"""
        for equipo in equipos:
            latex_content += f"{html_to_latex(equipo.nombre)} & {equipo.cantidad if equipo.cantidad else '1'} \\\\\n\\hline\n"
        
        latex_content += r"""\end{longtable}

"""
    
    # 6.2 Materiales
    if materiales.exists():
        latex_content += r"""\subsection{Materiales}

\begin{longtable}{|p{10cm}|p{3cm}|}
\hline
\textbf{Material} & \textbf{Cantidad} \\
\hline
"""
        for material in materiales:
            latex_content += f"{html_to_latex(material.nombre)} & {material.cantidad if material.cantidad else '1'} \\\\\n\\hline\n"
        
        latex_content += r"""\end{longtable}

"""
    
    # 6.3 Herramientas
    if herramientas.exists():
        latex_content += r"""\subsection{Herramientas}

\begin{longtable}{|p{10cm}|p{3cm}|}
\hline
\textbf{Herramienta} & \textbf{Cantidad} \\
\hline
"""
        for herramienta in herramientas:
            latex_content += f"{html_to_latex(herramienta.nombre)} & {herramienta.cantidad if herramienta.cantidad else '1'} \\\\\n\\hline\n"
        
        latex_content += r"""\end{longtable}

"""
    
    # 6.4 Reactivos
    if reactivos.exists():
        latex_content += r"""\subsection{Reactivos}

\begin{longtable}{|p{10cm}|p{3cm}|}
\hline
\textbf{Reactivo} & \textbf{Cantidad} \\
\hline
"""
        for reactivo in reactivos:
            latex_content += f"{html_to_latex(reactivo.nombre)} & {reactivo.cantidad if reactivo.cantidad else '1'} \\\\\n\\hline\n"
        
        latex_content += r"""\end{longtable}

"""
    
    if not (equipos.exists() or materiales.exists() or herramientas.exists() or reactivos.exists()):
        latex_content += "No hay materiales, equipos ni herramientas definidos.\n\n"
    
    # ============================================================
    # 7. PROCEDIMIENTO
    # ============================================================
    latex_content += r"""\section{PROCEDIMIENTO}

"""
    
    procedimientos = Procedimientos.objects.filter(contenido_analitico=contenido).order_by('numero_paso', 'orden')
    
    if procedimientos.exists():
        latex_content += r"\begin{enumerate}[leftmargin=*]" + "\n"
        for proc in procedimientos:
            if proc.titulo_paso:
                latex_content += f"\\item \\textbf{{{html_to_latex(proc.titulo_paso)}}}\n\n"
            latex_content += f"{html_to_latex(proc.descripcion)}\n\n"
        latex_content += r"\end{enumerate}" + "\n\n"
    else:
        latex_content += "No hay procedimiento definido.\n\n"
    
    # ============================================================
    # 8. CÁLCULOS Y RESULTADOS
    # ============================================================
    latex_content += r"""\section{CÁLCULOS Y RESULTADOS}

"""
    
    calculos = CalculosResultados.objects.filter(contenido_analitico=contenido).order_by('orden')
    
    if calculos.exists():
        for calc in calculos:
            if calc.titulo:
                latex_content += f"\\subsection{{{html_to_latex(calc.titulo)}}}\n\n"
            
            if calc.formula:
                latex_content += f"\\textbf{{Fórmula:}} {html_to_latex(calc.formula)}\n\n"
            
            if calc.procedimiento_calculo:
                latex_content += html_to_latex(calc.procedimiento_calculo) + "\n\n"
    else:
        latex_content += "No hay cálculos y resultados definidos.\n\n"
    
    # ============================================================
    # 9. CUESTIONARIO
    # ============================================================
    latex_content += r"""\section{CUESTIONARIO}

"""
    
    cuestionario = Cuestionario.objects.filter(contenido_analitico=contenido).order_by('numero_pregunta', 'orden')
    
    if cuestionario.exists():
        latex_content += r"\begin{enumerate}[leftmargin=*]" + "\n"
        for pregunta in cuestionario:
            latex_content += f"\\item {html_to_latex(pregunta.pregunta)}\n\n"
        latex_content += r"\end{enumerate}" + "\n\n"
    else:
        latex_content += "No hay cuestionario definido.\n\n"
    
    # ============================================================
    # FIRMA DEL DOCENTE
    # ============================================================
    latex_content += r"""
\vspace{2cm}

\noindent\rule{10cm}{0.4pt}\\
\textbf{DOCENTE DE LABORATORIO DE LA ASIGNATURA """ + (asignatura.nombre if asignatura else 'N/A') + r"""} (firma)

\end{document}"""
    
    # Escribir archivo .tex
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"✅ Archivo LaTeX generado: {tex_file}")
    print(f"📝 Longitud total: {len(latex_content)} caracteres")
    
    # Compilar con pdflatex
    try:
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', temp_dir, tex_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        pdf_file = os.path.join(temp_dir, 'practica.pdf')
        
        if os.path.exists(pdf_file):
            print(f"✅ PDF generado: {pdf_file}")
            return pdf_file, temp_dir
        else:
            print(f"❌ Error: PDF no generado")
            print(f"Log stdout: {result.stdout[-1000:]}")
            print(f"Log stderr: {result.stderr[-1000:]}")
            return None, temp_dir
            
    except Exception as e:
        print(f"❌ Error al compilar: {e}")
        return None, temp_dir


if __name__ == "__main__":
    # Probar con práctica 38
    pdf, temp_dir = generar_latex_practica(38)
    if pdf:
        print(f"\n✅ PDF generado exitosamente: {pdf}")
        print(f"📂 Abriendo PDF...")
        os.system(f"open '{pdf}'")
    else:
        print(f"\n❌ No se pudo generar el PDF")
        print(f"Revisa los archivos en: {temp_dir}")

