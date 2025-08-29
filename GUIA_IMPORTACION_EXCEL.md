# 📋 Scripts de Importación de Equipos desde Excel

Este documento explica cómo usar los scripts para importar datos de equipos desde archivos Excel al sistema de centralización de laboratorios.

## 📄 Archivos Incluidos

1. **`importar_excel_equipos.py`** - Script completo de importación que guarda datos en la base de datos
2. **`extraer_excel_equipos.py`** - Script de análisis que solo extrae y analiza datos sin modificar la BD
3. **`GUIA_IMPORTACION_EXCEL.md`** - Esta documentación

## 📊 Formato de Excel Requerido

El archivo Excel debe contener exactamente estas columnas en este orden:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| N | Número secuencial | 1, 2, 3... |
| UNIDAD ACADEMICA | Código o nombre de la unidad | UALP, UACB, UASC, UATP, UCRB |
| RESPONSABLE | Nombre completo del responsable | Juan Pérez López |
| C.I. | Cédula de identidad | 12345678 |
| CARGO | Cargo del responsable | Docente, Técnico, Auxiliar |
| OFICINA | Ubicación de oficina | Oficina 201, Lab Química |
| CODIGO | Código del equipo (opcional) | EQ-001, LAB-QUI-001 |
| DESCRIPCION DEL ACTIVO | Descripción completa del equipo | Microscopio Óptico Trinocular |
| ESTADO | Estado actual del equipo | OPERATIVO, REGULAR, MALO |
| FECHA DE ASIGNACION | Fecha de asignación | 15/03/2024 |

## 🚀 Uso de los Scripts

### 1. Script de Análisis (Recomendado primero)

```bash
# Analizar archivo sin modificar la base de datos
python extraer_excel_equipos.py archivo_equipos.xlsx
```

**Qué hace:**
- ✅ Valida el formato del archivo
- ✅ Muestra estadísticas de los datos
- ✅ Identifica posibles problemas
- ✅ Genera resumen exportable
- ❌ NO modifica la base de datos

**Ejemplo de uso:**
```bash
cd /Users/alvaroencinas/Desktop/centralizacion_laboratorios
python extraer_excel_equipos.py "Actas UICYT UALP/1 ACTAS UNIDAD DE INVESTIGACION CIENCIA Y TECNOLOGIA OFICINAS.xlsx"
```

### 2. Script de Importación Completa

```bash
# Importar datos a la base de datos
python importar_excel_equipos.py archivo_equipos.xlsx

# Modo de prueba (validar sin guardar)
python importar_excel_equipos.py archivo_equipos.xlsx --test
```

**Qué hace:**
- ✅ Valida y limpia los datos
- ✅ Crea usuarios responsables automáticamente
- ✅ Mapea unidades académicas existentes
- ✅ Normaliza estados de equipos
- ✅ Genera códigos de inventario únicos
- ✅ Guarda equipos en la base de datos
- ✅ Crea laboratorios por defecto si es necesario

**Parámetros disponibles:**
- `--test` : Modo de prueba, no guarda cambios

## 🗺️ Mapeo de Datos

### Estados de Equipos
El script mapea automáticamente los estados del Excel:

| Excel | Sistema |
|-------|---------|
| OPERATIVO | operativo |
| BUENO | operativo |
| REGULAR | necesita_mantenimiento |
| MALO | fuera_servicio |
| FUERA DE SERVICIO | fuera_servicio |
| EN MANTENIMIENTO | necesita_mantenimiento |
| DAÑADO | fuera_servicio |
| OBSOLETO | obsoleto |

### Unidades Académicas
| Excel | Sistema |
|-------|---------|
| UALP, LA PAZ | UALP |
| UACB, COCHABAMBA | UACB |
| UASC, SANTA CRUZ | UASC |
| UATP, TROPICO | UATP |
| UCRB, RIBERALTA | UCRB |

## 🔧 Configuración Previa

### 1. Instalar dependencias
```bash
pip install pandas openpyxl
```

### 2. Verificar configuración Django
```bash
python manage.py check
```

### 3. Verificar datos base del sistema
```bash
python manage.py shell
>>> from core.models import UnidadAcademica
>>> UnidadAcademica.objects.all()
```

## 📋 Proceso Recomendado

1. **Preparar archivo Excel**
   - Verificar que tiene todas las columnas requeridas
   - Limpiar datos duplicados o inconsistentes
   - Verificar formato de fechas

2. **Análisis inicial**
   ```bash
   python extraer_excel_equipos.py mi_archivo.xlsx
   ```

3. **Prueba de importación**
   ```bash
   python importar_excel_equipos.py mi_archivo.xlsx --test
   ```

4. **Importación real**
   ```bash
   python importar_excel_equipos.py mi_archivo.xlsx
   ```

## ⚠️ Consideraciones Importantes

### Datos Requeridos en el Sistema
Antes de importar, asegúrese de que existen:
- ✅ Unidades académicas configuradas
- ✅ Al menos una carrera por unidad académica
- ✅ Al menos una asignatura en el sistema

### Limitaciones Actuales
- Los equipos se asignan a datos por defecto para campos no incluidos en el Excel
- Se crean laboratorios genéricos si no existen
- Los usuarios responsables se crean automáticamente con credenciales temporales

### Datos Creados Automáticamente
- **Usuarios responsables**: Con username basado en el nombre
- **Laboratorios**: "Laboratorio General" por unidad académica
- **Códigos de inventario**: Si no se proporcionan en el Excel
- **Unidades temáticas**: "Equipos Importados" por defecto
- **Guías de laboratorio**: "Guía de Equipos Importados" por defecto

## 🐛 Solución de Problemas

### Error: "Unidad académica no encontrada"
```bash
# Verificar unidades disponibles
python manage.py shell
>>> from core.models import UnidadAcademica
>>> for ua in UnidadAcademica.objects.all():
...     print(f"{ua.nombre}: {ua.get_nombre_display()}")
```

### Error: "No hay carreras configuradas"
```bash
# Crear carreras básicas
python crear_datos_academicos_completos.py
```

### Error: "Archivo no encontrado"
- Verificar la ruta del archivo
- Usar comillas si la ruta tiene espacios
- Usar ruta absoluta si es necesario

### Problemas de codificación
- Asegurarse de que el Excel esté guardado en formato .xlsx
- Verificar que no hay caracteres especiales problemáticos

## 📊 Resultados de Importación

Al completar la importación, obtendrá:

```
📊 RESUMEN DE IMPORTACIÓN:
   ✅ Exitosos: 45
   ❌ Errores: 2
   📋 Total procesados: 47

🔍 DETALLE DE ERRORES:
   - Fila 23: Unidad académica no encontrada: UATF
   - Fila 31: Descripción del activo es requerida
```

## 📂 Archivos de Salida

### Resumen de análisis
- `resumen_equipos_YYYYMMDD_HHMMSS.txt`: Análisis completo de datos

### Logs de importación
- Mensajes en consola con detalles de cada operación
- Errores específicos por fila

## 🔄 Actualizaciones y Mantenimiento

Para actualizar equipos existentes:
1. Exportar datos actuales
2. Modificar Excel con cambios
3. Ejecutar importación (duplicados se detectan por código)

## 📞 Soporte

Si encuentra problemas:
1. Verificar formato del Excel
2. Revisar logs de error específicos
3. Ejecutar en modo `--test` primero
4. Contactar al administrador del sistema

---

**Nota**: Siempre haga respaldo de la base de datos antes de importaciones masivas.
