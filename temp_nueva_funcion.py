# NOTA: Este es el código de reemplazo para generar_practica_word en guias/views.py
# Copiar todo esto DESPUÉS de la línea "@login_required" y "def generar_practica_word(request, practica_id):"

    """Generar PDF con LaTeX de una práctica de laboratorio - VERSIÓN COMPLETA EMI"""
    
    try:
        # Obtener la práctica y modelos relacionados  
        practica = get_object_or_404(PracticaLaboratorio, id=practica_id)
        asignatura = practica.contenido_analitico.unidad_didactica.asignatura
        unidad = practica.contenido_analitico.unidad_didactica
        contenido = practica.contenido_analitico
        
        print(f"📄 Generando PDF LaTeX para práctica: {practica.nombre}")
        
        # Crear directorio temporal
        temp_dir = tempfile.mkdtemp()
        tex_file = os.path.join(temp_dir, 'practica.tex')
        
        # Generar contenido LaTeX COMPLETO (ver archivo generar_latex.py para la versión completa)
        # Por brevedad, aquí está resumido. COPIAR LA VERSIÓN COMPLETA DEL ARCHIVO generar_latex.py
        
        latex_content = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage{geometry}
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{array}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{tcolorbox}

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

% PORTADA
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
        contenido_analitico_text = contenido.nombre
        if contenido.descripcion and not contenido.descripcion.startswith("Práctica de laboratorio:"):
            contenido_analitico_text = contenido.descripcion
        elif contenido.nombre == practica.nombre or contenido.nombre in ['TITULOOOO', 'titulo', 'Título']:
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
        
        # Bibliografía
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

\section{COMPETENCIAS}

"""
        
        # 2. COMPETENCIAS
        competencias = Competencias.objects.filter(contenido_analitico=contenido).order_by('orden')
        if competencias.exists():
            latex_content += r"\begin{itemize}[leftmargin=*]" + "\n"
            for comp in competencias:
                tipo_comp = comp.get_tipo_competencia_display() if hasattr(comp, 'tipo_competencia') else "Competencia"
                latex_content += f"\\item \\textbf{{{tipo_comp}}}: {html_to_latex(comp.descripcion)}\n"
            latex_content += r"\end{itemize}" + "\n\n"
        else:
            latex_content += "No hay competencias definidas.\n\n"
        
        # 3. CRITERIOS DE DESEMPEÑO
        latex_content += r"""\section{CRITERIOS DE DESEMPEÑO}

"""
        criterios = ObjetivoPractica.objects.filter(contenido_analitico=contenido).order_by('orden')
        if criterios.exists():
            latex_content += r"\begin{enumerate}[leftmargin=*]" + "\n"
            for criterio in criterios:
                latex_content += f"\\item {html_to_latex(criterio.descripcion)}\n"
            latex_content += r"\end{enumerate}" + "\n\n"
        else:
            latex_content += "No hay criterios de desempeño definidos.\n\n"
        
        # 4. OBJETIVOS
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
        
        # 5. FUNDAMENTO TEÓRICO
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
        
        # 6. MATERIALES, EQUIPOS, HERRAMIENTAS
        latex_content += r"""\section{MATERIALES, HERRAMIENTAS Y EQUIPOS}

"""
        equipos = MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido, tipo_elemento='equipo').order_by('orden')
        materiales = MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido, tipo_elemento='material').order_by('orden')
        herramientas = MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido, tipo_elemento='herramienta').order_by('orden')
        reactivos = MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido, tipo_elemento='reactivo').order_by('orden')
        
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
        
        # 7. PROCEDIMIENTO
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
        
        # 8. CÁLCULOS Y RESULTADOS
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
        
        # 9. CUESTIONARIO
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
        
        # FIRMA
        latex_content += r"""
\vspace{2cm}

\noindent\rule{10cm}{0.4pt}\\
\textbf{DOCENTE DE LABORATORIO DE LA ASIGNATURA """ + (asignatura.nombre if asignatura else 'N/A') + r"""} (firma)

\end{document}"""
        
        # Escribir archivo .tex
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        print(f"✅ Archivo LaTeX generado: {tex_file}")
        
        # Compilar con pdflatex
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', temp_dir, tex_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        pdf_file = os.path.join(temp_dir, 'practica.pdf')
        
        if not os.path.exists(pdf_file):
            print(f"❌ Error: PDF no generado")
            print(f"Log: {result.stdout[-1000:]}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return JsonResponse({'error': 'No se pudo generar el PDF'}, status=500)
        
        print(f"✅ PDF generado: {pdf_file}")
        
        # Leer el PDF generado
        with open(pdf_file, 'rb') as f:
            pdf_data = f.read()
        
        # Limpiar directorio temporal
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Preparar respuesta HTTP
        filename = f"Practica_{practica.orden if practica.orden else 'N'}_{practica.nombre[:30]}.pdf"
        filename = filename.replace(' ', '_').replace('/', '_')
        
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
