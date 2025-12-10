# MAPEO COMPLETO: FORMULARIO → BASE DE DATOS → PDF

## TODOS LOS CAMPOS DEL FORMULARIO AGREGAR_DATOS_MALLA.HTML

### ✅ DATOS CAPTURADOS Y REFLEJADOS EN EL PDF:

| # | Campo del Formulario | Modelo | Campo DB | Sección en PDF | Estado |
|---|---------------------|--------|----------|----------------|--------|
| 1 | **Bibliografia** | `Bibliografia` | `titulo`, `autor` | Datos Generales (tabla) | ✅ FUNCIONA |
| 2 | **Práctica de Laboratorio** | `PracticaLaboratorio` | `nombre` | Encabezado EMI (dorado) | ✅ FUNCIONA |
| 3 | **Título** | `Titulo` | `texto` | Encabezado EMI (reemplaza nombre si existe) | ✅ AGREGADO |
| 4 | **Competencias** | `Competencias` | `descripcion`, `tipo_competencia` | Sección 2: COMPETENCIAS | ✅ FUNCIONA |
| 5 | **Objetivo de la Práctica** | `ObjetivoPractica` | `descripcion`, `tipo_objetivo='desempeno'` | Sección 3: CRITERIOS DE DESEMPEÑO | ✅ FUNCIONA |
| 6 | **Fundamento Teórico** | `FundamentoTeorico` | `titulo`, `contenido` | Sección 5: FUNDAMENTO TEÓRICO | ✅ FUNCIONA |
| 7 | **Equipos** (selección múltiple) | `MaterialesHerramientasEquipos` | `nombre`, `tipo_elemento='equipo'` | Sección 6.1: Equipos | ✅ FUNCIONA |
| 8 | **Materiales** (selección múltiple) | `MaterialesHerramientasEquipos` | `nombre`, `tipo_elemento='material'` | Sección 6.2: Materiales | ✅ FUNCIONA |
| 9 | **Herramientas** (selección múltiple) | `MaterialesHerramientasEquipos` | `nombre`, `tipo_elemento='herramienta'` | Sección 6.3: Herramientas | ✅ FUNCIONA |
| 10 | **Reactivos** (selección múltiple) | `MaterialesHerramientasEquipos` | `nombre`, `tipo_elemento='reactivo'` | Sección 6.4: Reactivos | ✅ FUNCIONA |
| 11 | **Procedimientos** | `Procedimientos` | `numero_paso`, `titulo_paso`, `descripcion` | Sección 7: PROCEDIMIENTO | ✅ FUNCIONA |
| 12 | **Cálculos y Resultados** | `CalculosResultados` | `titulo`, `formula`, `procedimiento_calculo` | Sección 8: CÁLCULOS Y RESULTADOS | ✅ FUNCIONA |
| 13 | **Cuestionario** | `Cuestionario` | `numero_pregunta`, `pregunta` | Sección 9: CUESTIONARIO | ✅ FUNCIONA |

---

## ESTRUCTURA COMPLETA DEL PDF GENERADO

### Encabezado EMI (Color Dorado)
```
PRÁCTICA DE LABORATORIO N° [orden]
TÍTULO: [Titulo.texto SI EXISTE, sino PracticaLaboratorio.nombre]
```

### Sección 1: DATOS GENERALES
**Tabla con:**
- Carrera
- Semestre
- Asignatura
- Contenido Analítico
- Unidad Didáctica
- Docente (línea en blanco)
- Correo Institucional (línea en blanco)
- **Bibliografía de Referencia** ← Usa `Bibliografia.titulo`

### Sección 2: COMPETENCIAS
**Lista con viñetas:**
- Tipo de competencia (Conceptual, Procedimental, Actitudinal, Mixta)
- Descripción

### Sección 3: CRITERIOS DE DESEMPEÑO
**Lista numerada:**
- Solo objetivos con `tipo_objetivo='desempeno'`
- Corresponde al campo "Objetivo de la Práctica" del formulario

### Sección 4: OBJETIVO DE LA PRÁCTICA DE LABORATORIO
**Lista con viñetas:**
- Objetivos con tipo: General, Específico, Aprendizaje
- Excluye los de tipo 'desempeno'

### Sección 5: FUNDAMENTO TEÓRICO
**Subsecciones:**
- Cada `FundamentoTeorico` con su título
- Contenido completo

### Sección 6: MATERIALES, HERRAMIENTAS Y EQUIPOS
**Tablas separadas:**
- 6.1 Equipos (`tipo_elemento='equipo'`)
- 6.2 Materiales (`tipo_elemento='material'`)
- 6.3 Herramientas (`tipo_elemento='herramienta'`)
- 6.4 Reactivos (`tipo_elemento='reactivo'`)

### Sección 7: PROCEDIMIENTO
**Lista numerada:**
- Cada paso con su título y descripción
- Ordenado por `numero_paso`

### Sección 8: CÁLCULOS Y RESULTADOS
**Subsecciones:**
- Título del cálculo
- Fórmula (si existe)
- Procedimiento de cálculo

### Sección 9: CUESTIONARIO
**Lista numerada:**
- Preguntas ordenadas por `numero_pregunta`

---

## ARCHIVOS MODIFICADOS EN ESTA CORRECCIÓN

### 1. `guias/views.py`
- **Línea 40**: Agregado import de `Titulo`
- **Líneas 1858-1868**: Usar `Titulo.texto` si existe, sino usar `practica.nombre`
- **Líneas 1891-1897**: Criterios de Desempeño filtrados por `tipo_objetivo='desempeno'`
- **Líneas 1909-1921**: Objetivos excluyen `tipo_objetivo='desempeno'`

### 2. `core/views.py`
- **Línea 880**: Campo "objetivo_practica" crea con `tipo_objetivo='desempeno'`

---

## VERIFICACIÓN COMPLETA

### ✅ Datos que SÍ se capturan y muestran:
1. ✅ Bibliografía → Tabla Datos Generales
2. ✅ Práctica/Título → Encabezado EMI
3. ✅ Competencias → Sección 2
4. ✅ Objetivo Práctica → Sección 3 (Criterios)
5. ✅ Fundamento Teórico → Sección 5
6. ✅ Equipos → Sección 6.1
7. ✅ Materiales → Sección 6.2
8. ✅ Herramientas → Sección 6.3
9. ✅ Reactivos → Sección 6.4
10. ✅ Procedimientos → Sección 7
11. ✅ Cálculos → Sección 8
12. ✅ Cuestionario → Sección 9

### 📊 RESUMEN:
- **Total de campos del formulario**: 13
- **Campos que se reflejan en el PDF**: 13 (100%)
- **Estado del sistema**: ✅ COMPLETAMENTE FUNCIONAL

---

## FLUJO DE DATOS COMPLETO

```
FORMULARIO (agregar_datos_malla.html)
    ↓
VISTA (core/views.py - agregar_datos_malla_view)
    ↓
MODELOS (core/models.py)
    ├── Bibliografia
    ├── PracticaLaboratorio
    ├── Titulo
    ├── Competencias
    ├── ObjetivoPractica (tipo_objetivo='desempeno')
    ├── FundamentoTeorico
    ├── MaterialesHerramientasEquipos (4 tipos)
    ├── Procedimientos
    ├── CalculosResultados
    └── Cuestionario
    ↓
GENERACIÓN PDF (guias/views.py - generar_practica_word)
    ↓
PDF CON 9 SECCIONES COMPLETAS
```

---

## CONCLUSIÓN

✅ **TODOS LOS CAMPOS** del formulario `agregar_datos_malla.html` ahora se reflejan correctamente en el PDF generado.

✅ **El backend funciona correctamente** - Guarda todos los datos en los modelos apropiados.

✅ **La generación de guías funciona perfectamente** - Extrae todos los datos y los muestra en el PDF con formato profesional EMI.

**No hay campos faltantes ni datos perdidos.**
