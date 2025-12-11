# Sistema de Centralización de Laboratorios - EMI

## "TRANSFORMANDO EL EJERCITO RUMBO AL BICENTENARIO"

**EMI-DNICYT-INF Nº 001/2025**

---

## 📋 Descripción del Proyecto

El Sistema de Centralización de Laboratorios es una solución integral desarrollada por la Dirección Nacional de Investigación, Ciencia y Tecnología (DNICYT) de la Escuela Militar de Ingeniería (EMI), diseñada para centralizar, gestionar y optimizar la información sobre laboratorios, equipos e insumos académicos a nivel nacional.

### 🎯 Objetivo Principal
Centralizar la información de los laboratorios a nivel nacional, permitiendo una visión completa y actualizada del equipamiento e insumos disponibles, su estado, ubicación y utilización, para tomar decisiones basadas en datos reales y garantizar la asignación eficiente de recursos institucionales.

---

## 🚀 Funcionalidades Principales

### 📊 **Dashboard Ejecutivo**
- Visualización de estadísticas en tiempo real
- Indicadores clave de rendimiento (KPIs)
- Distribución geográfica de recursos
- Actividad reciente del sistema

### 📝 **Ingreso Estructurado de Datos**
- Registro de laboratorios por unidad académica
- Catalogación de ensayos y prácticas
- Inventario detallado de equipos individuales
- Vinculación con materias y carreras

### 📈 **Visualización y Análisis**
- Filtros dinámicos por múltiples criterios
- Reportes automatizados en formato Excel
- Gráficos estadísticos interactivos
- Análisis comparativo entre unidades

### ⚙️ **Gestión de Información**
- Edición de registros existentes
- Control de permisos por usuario
- Eliminación controlada de información
- Trazabilidad de modificaciones

---

## 🏗️ Arquitectura Técnica

### **Framework y Lenguaje de Desarrollo**
```python
# Tecnología Principal
Django 5.2.4          # Framework web robusto y escalable
Python 3.11+          # Lenguaje de programación
```

### **Base de Datos**
```sql
-- Motor de Base de Datos
SQLite 3              # Desarrollo y pruebas
PostgreSQL/MySQL      # Producción (recomendado)
```

### **Frontend y UI/UX**
```css
/* Tecnologías de Frontend */
HTML5 + CSS3          # Estructura y estilos responsivos
JavaScript ES6+       # Interactividad dinámica
Font Awesome 6.0      # Iconografía profesional
Bootstrap Grid        # Sistema de grillas responsive
```

---

## 📦 Dependencias del Sistema

### **Librerías Core**
```requirements
Django==5.2.4                    # Framework web principal
djangorestframework==3.16.0      # API REST para servicios
django-cors-headers==4.7.0       # Manejo de CORS
django-extensions==4.1           # Extensiones adicionales
```

### **Procesamiento de Datos**
```requirements
pandas==2.3.1                    # Análisis y manipulación de datos
numpy==2.3.1                     # Operaciones numéricas avanzadas
openpyxl==3.1.5                  # Exportación a Excel
xlsxwriter==3.2.5                # Generación de reportes Excel
```

### **Manejo de Archivos y Multimedia**
```requirements
pillow==11.3.0                   # Procesamiento de imágenes
python-decouple==3.8             # Gestión de configuraciones
```

### **Comunicaciones HTTP**
```requirements
requests==2.32.4                 # Cliente HTTP para APIs externas
urllib3==2.5.0                   # Utilidades HTTP de bajo nivel
certifi==2025.7.14               # Certificados SSL/TLS
```

### **Internacionalización y Zona Horaria**
```requirements
pytz==2025.2                     # Manejo de zonas horarias
tzdata==2025.2                   # Datos de zona horaria
python-dateutil==2.9.0.post0     # Utilidades de fecha avanzadas
```

---

## 🔧 Especificaciones Técnicas del Sistema

### **Requerimientos del Servidor**

#### **Especificaciones Mínimas**
- **CPU**: 2 cores x 2.4 GHz
- **RAM**: 4 GB mínimo (8 GB recomendado)
- **Almacenamiento**: 20 GB SSD
- **Sistema Operativo**: Linux Ubuntu 20.04 LTS / CentOS 8+

#### **Servidor Web**
- **Apache HTTP Server 2.4+** con mod_wsgi
- **Nginx 1.18+** como proxy reverso (opcional)
- **Gunicorn** como servidor WSGI

#### **Base de Datos en Producción**
- **PostgreSQL 13+** (recomendado)
- **MySQL 8.0+** (alternativa)
- **Conexiones concurrentes**: 100+

### **Seguridad y Protocolos**

#### **Protocolos de Seguridad**
```python
# Configuraciones de Seguridad
SECURE_SSL_REDIRECT = True       # Redirección HTTPS forzada
SECURE_HSTS_SECONDS = 31536000   # HTTP Strict Transport Security
CSRF_COOKIE_SECURE = True       # Cookies CSRF seguras
SESSION_COOKIE_SECURE = True     # Cookies de sesión seguras
```

#### **Autenticación y Autorización**
- Sistema de usuarios integrado de Django
- Control de permisos por roles
- Autenticación basada en sesiones
- Protección CSRF incorporada

### **APIs y Servicios**

#### **Endpoints Principales**
```python
# APIs REST Disponibles
/api/laboratorios/               # CRUD de laboratorios
/api/equipos/                    # Gestión de equipos
/api/ensayos/                    # Administración de ensayos
/api/reportes/excel/             # Exportación de datos
```

---

## 🌐 Integración con Portal Institucional

### **Dominio y Subdominio**
- **URL Principal**: `https://laboratorios.emi.edu.bo`
- **Subdominio Alternativo**: `https://emi.edu.bo/laboratorios`

### **Identidad Gráfica Institucional**
```css
/* Colores Institucionales EMI */
--primary-color: #1e3a8a;        /* Azul EMI */
--secondary-color: #059669;      /* Verde militar */
--accent-color: #dc2626;         /* Rojo de alerta */
--gold-color: #fbbf24;           /* Dorado institucional */
```

### **Responsive Design**
- **Mobile First**: Optimizado para dispositivos móviles
- **Breakpoints**: 320px, 768px, 1024px, 1440px
- **Cross-browser**: Compatible con Chrome, Firefox, Safari, Edge

---

## 📊 Métricas y Monitoreo

### **Indicadores de Rendimiento**
- **Tiempo de respuesta**: < 2 segundos
- **Disponibilidad**: 99.5% uptime
- **Usuarios concurrentes**: Hasta 50 usuarios simultáneos
- **Capacidad de datos**: 10,000+ registros de laboratorios

### **Logs y Auditoría**
```python
# Sistema de Logging
import logging

# Configuración de logs para producción
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/emi/laboratorios.log',
        }
    }
}
```

---

## 🔄 Procedimientos de Despliegue

### **Migración de Base de Datos**
```bash
# Comandos de migración
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```

### **Variables de Entorno**
```bash
# Configuraciones de producción
DJANGO_SETTINGS_MODULE=centralizacion.settings.production
DATABASE_URL=postgresql://user:pass@localhost/emi_labs
SECRET_KEY=***SEGURO_Y_UNICO***
DEBUG=False
ALLOWED_HOSTS=laboratorios.emi.edu.bo,emi.edu.bo
```

---

## 📁 Estructura del Proyecto

```
centralizacion_laboratorios/
├── centralizacion/          # Configuración principal
│   ├── settings.py         # Configuraciones
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # Servidor WSGI
├── login/                  # Autenticación
├── ingreso_datos/          # Módulo de ingreso
├── visualizacion/          # Módulo de reportes
├── gestion_info/           # Gestión de datos
├── templates/              # Templates HTML
├── static/                 # Archivos estáticos
├── requirements.txt        # Dependencias
└── manage.py              # CLI de Django
```

---

## 🚀 Beneficios Esperados

### **Optimización Institucional**
- ✅ **Reducción de duplicidad** en adquisiciones de equipos
- ✅ **Mejor distribución** de recursos entre unidades
- ✅ **Transparencia total** en la gestión de laboratorios
- ✅ **Planificación académica** basada en datos reales

### **Eficiencia Operativa**
- ✅ **Automatización** de reportes y estadísticas
- ✅ **Centralización** de información nacional
- ✅ **Trazabilidad completa** de recursos y equipos
- ✅ **Soporte para decisiones** estratégicas institucionales

---

## �️ Instalación y Configuración

### 📋 Requisitos del Sistema
- Python 3.13.5+
- Django 5.2.4
- SQLite3
- Navegador web moderno

### 🚀 Instalación Rápida

#### 1. Clonar el repositorio
```bash
git clone https://github.com/Darkweaver2535/centralizacion_laboratorios.git
cd centralizacion_laboratorios
```

#### 2. Configurar entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

#### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 4. Configurar base de datos
```bash
# Aplicar migraciones
python manage.py migrate

# Crear datos básicos
python manage.py shell
```

#### 5. Crear datos iniciales en el shell de Django:
```python
from core.models import UnidadAcademica, Carrera
from insumos.models import TipoInsumo
from django.contrib.auth.models import User

# Unidades académicas
unidades = [
    {'nombre': 'UASC', 'descripcion': 'UASC - Unidad Académica Santa Cruz'},
    {'nombre': 'UCRB', 'descripcion': 'UARIBE - Unidad Académica Riberalta'},
    {'nombre': 'UATP', 'descripcion': 'UATROP - Unidad Académica Trinidad'},
    {'nombre': 'UACB', 'descripcion': 'UACBBA - Unidad Académica Cochabamba'},
    {'nombre': 'UALP', 'descripcion': 'Unidad Académica La Paz'}
]

for unidad_data in unidades:
    UnidadAcademica.objects.get_or_create(**unidad_data)

# Carreras oficiales EMI
carreras_licenciatura = [
    "Ingeniería Civil", "Ingeniería Geográfica", "Ingeniería en Sistemas Electrónicos",
    "Ingeniería Industrial", "Ingeniería Comercial", "Ingeniería de Sistemas",
    "Ingeniería Ambiental", "Ingeniería Petrolera", "Ingeniería Mecatrónica",
    "Ingeniería en Telecomunicaciones", "Ingeniería Financiera", 
    "Ingeniería Agroindustrial", "Ingeniería Agronómica"
]

carreras_tecnicas = [
    "Informática", "Sistemas Electrónicos", "Energías Renovables",
    "Construcción Civil", "Diseño Gráfico y Comunicación Audiovisual"
]

# Obtener unidad académica por defecto
unidad_default = UnidadAcademica.objects.first()

# Crear carreras de licenciatura
for nombre in carreras_licenciatura:
    Carrera.objects.get_or_create(
        nombre=nombre,
        defaults={'descripcion': f'Carrera de {nombre}', 'unidad_academica': unidad_default}
    )

# Crear carreras técnicas
for nombre in carreras_tecnicas:
    Carrera.objects.get_or_create(
        nombre=nombre,
        defaults={'descripcion': f'Carrera técnica de {nombre}', 'unidad_academica': unidad_default}
    )

# Tipos de insumo
tipos = [
    {'nombre': 'Reactivo Químico', 'descripcion': 'Reactivos químicos para laboratorio'},
    {'nombre': 'Material de Vidrio', 'descripcion': 'Materiales de vidrio para laboratorio'},
    {'nombre': 'Instrumental', 'descripcion': 'Instrumentos de laboratorio'},
    {'nombre': 'Equipo de Protección', 'descripcion': 'Equipos de protección personal'},
    {'nombre': 'Consumible', 'descripcion': 'Materiales consumibles'}
]

for tipo_data in tipos:
    TipoInsumo.objects.get_or_create(**tipo_data)

# Usuario administrador
User.objects.create_superuser('admin', 'admin@emi.edu.bo', 'admin123')
exit()
```

#### 6. Ejecutar el servidor
```bash
python manage.py runserver
```

### 🔑 Acceso al Sistema
- **URL**: http://127.0.0.1:8000/
- **Usuario**: admin
- **Contraseña**: admin123

---

## 🔄 Funcionalidades Actualizadas (v2.0.0)

### ✅ **Nuevas Características**
- **Sistema de Reordenamiento de Insumos**: Gestión completa de reorganización de insumos
- **Templates Unificados**: Diseño azul consistente en todo el sistema
- **Seguridad Mejorada**: Mensajes genéricos sin filtrar información sensible
- **Base de Datos Optimizada**: Reducción del 99.3% en tamaño para GitHub
- **Soporte Multi-Unidad**: Gestión simultánea de 5 unidades académicas

### 🔧 **Mejoras Técnicas**
- Eliminación de datos de prueba innecesarios
- Optimización de consultas a BD
- Implementación de .gitignore completo
- Limpieza de historial de Git
- Documentación actualizada

---

## 🚨 Notas Importantes

⚠️ **IMPORTANTE**: La base de datos no está incluida en el repositorio por motivos de seguridad y tamaño. Debe ser recreada siguiendo los pasos de instalación.

📌 **Datos Mantenidos**:
- Unidades Académicas oficiales
- Tipos de Insumo básicos
- Estructura completa de tablas
- Sistema de usuarios y permisos

---

## �📞 Contacto y Soporte

**Desarrollo y Mantenimiento:**
- **DNICYT - EMI**
- **Director**: Tcnl. DIM. Jurgen Alberto Bleichner Benítez
- **Repositorio**: [GitHub](https://github.com/Darkweaver2535/centralizacion_laboratorios)
- **Correo**: dnicyt@emi.edu.bo
- **Teléfono**: +591 (2) 2847474

---

**"2025 BICENTENARIO DE BOLIVIA"**

*Desarrollado por la Dirección Nacional de Investigación, Ciencia y Tecnología (DNICYT)*  
*Escuela Militar de Ingeniería - EMI*
