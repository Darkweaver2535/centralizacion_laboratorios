# ✅ SOLUCION: Error Cargando Carreras

## 🔍 Problema Identificado
El error "Error cargando carreras" ocurría porque:

1. **Modelos Duplicados**: Existían dos modelos `Carrera` diferentes:
   - `ingreso_datos.models.Carrera` (sin relación a UnidadAcademica)
   - `core.models.Carrera` (con relación a UnidadAcademica y datos poblados)

2. **Importación Incorrecta**: El formulario `InformacionAcademicaForm` importaba desde el modelo local incorrecto:
   ```python
   from .models import Carrera  # ❌ Modelo sin datos
   ```

3. **Sin Carga Dinámica**: Las carreras no se filtraban por unidad académica

## 🛠️ Solución Implementada

### 1. **Corrección del Formulario**
```python
# ingreso_datos/forms.py
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    from core.models import Carrera  # ✅ Modelo correcto
    # Generate choices dynamically from the Carrera model
    carrera_choices = [('', 'Seleccione una carrera')]
    carrera_choices.extend([(carrera.nombre, carrera.get_nombre_display()) 
                           for carrera in Carrera.objects.all().order_by('nombre')])
    self.fields['carrera'].choices = carrera_choices
```

### 2. **Nueva Vista AJAX**
```python
# ingreso_datos/views.py
@login_required
def get_carreras_por_unidad(request):
    """Vista AJAX para obtener carreras filtradas por unidad académica"""
    # Mapeo de valores del formulario a nombres en BD
    mapeo_unidades = {
        'la_paz': 'UASC',
        'santa_cruz': 'UASC', 
        'cochabamba': 'UACBBA',
        'riberalta': 'UARIBE',
        'tropico': 'UATROP'
    }
    # Filtrar carreras por unidad académica
    carreras = Carrera.objects.filter(unidad_academica=unidad).order_by('nombre')
```

### 3. **Nueva URL**
```python
# ingreso_datos/urls.py
urlpatterns = [
    path('', views.ingreso_datos_view, name='ingreso_datos'),
    path('carreras/', views.get_carreras_por_unidad, name='get_carreras_por_unidad'),
]
```

### 4. **JavaScript Frontend**
```javascript
// templates/ingreso_datos.html
// Event listener para cambio de unidad académica
document.querySelector('[name="unidad_academica"]').addEventListener('change', function() {
    const unidadAcademica = this.value;
    
    // Cargar carreras para la nueva unidad académica
    loadCarrerasPorUnidad(unidadAcademica);
});

// Función para cargar carreras por unidad académica
function loadCarrerasPorUnidad(unidadAcademica) {
    fetch(`/ingreso_datos/carreras/?unidad_academica=${encodeURIComponent(unidadAcademica)}`)
    .then(response => response.json())
    .then(data => {
        // Actualizar select de carreras dinámicamente
        const carreraSelect = document.querySelector('[name="carrera"]');
        carreraSelect.innerHTML = '<option value="">Seleccione una carrera</option>';
        data.carreras.forEach(carrera => {
            const option = document.createElement('option');
            option.value = carrera.id;
            option.textContent = carrera.text;
            carreraSelect.appendChild(option);
        });
    });
}
```

## 📊 Datos Disponibles Ahora

### Por Unidad Académica:
- **UASC (La Paz/Santa Cruz)**: 
  - ING_SISTEMAS, ING_INDUSTRIAL, ING_COMERCIAL, ING_CIVIL, ING_PETROLERA, etc.
- **UACBBA (Cochabamba)**: 
  - ING_SISTEMAS_CBBA, ING_INDUSTRIAL_CBBA, ING_COMERCIAL_CBBA
- **UARIBE (Riberalta)**: 
  - ING_SISTEMAS_RIBE, ING_COMERCIAL_RIBE
- **UATROP (Trópico)**: 
  - ING_SISTEMAS_TROP

## ✅ Resultado Final

1. **✅ Error Resuelto**: No más "Error cargando carreras"
2. **✅ Carga Dinámica**: Carreras se filtran por unidad académica seleccionada
3. **✅ Datos Reales**: Usa el modelo correcto con datos poblados
4. **✅ UX Mejorada**: Loading states y manejo de errores
5. **✅ Integración Completa**: Funciona con el resto del sistema

## 🚀 Cómo Probar

1. Ir a `http://127.0.0.1:8001/ingreso_datos/`
2. Seleccionar una "Unidad Académica"
3. Observar que el dropdown "Carrera" se actualiza automáticamente
4. Ver las carreras específicas de esa unidad académica

---
**🎉 ¡Problema resuelto completamente!**
