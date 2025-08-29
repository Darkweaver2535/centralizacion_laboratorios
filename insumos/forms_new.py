from django import forms
from django.contrib.auth import get_user_model
from .models import Insumo
from core.models import UnidadAcademica, Carrera, Asignatura, UnidadTematica, GuiaLaboratorio, Practica, Laboratorio

User = get_user_model()

class InsumoForm(forms.ModelForm):
    """Formulario para el registro de insumos con las 19 columnas oficiales"""
    
    # Campos dinámicos como ModelChoiceField para mejor control
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.none(),
        empty_label="Seleccione una carrera",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True,
            'data-api-url': '/insumos/api/asignaturas/'
        })
    )
    
    asignatura = forms.ModelChoiceField(
        queryset=Asignatura.objects.none(),
        empty_label="Seleccione una asignatura", 
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True,
            'data-api-url': '/insumos/api/unidades-tematicas/'
        })
    )
    
    unidad_tematica = forms.ModelChoiceField(
        queryset=UnidadTematica.objects.none(),
        empty_label="Seleccione una unidad temática",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si hay datos en el request, cargar las opciones correspondientes
        if 'unidad_academica' in self.data:
            try:
                unidad_academica_id = int(self.data.get('unidad_academica'))
                self.fields['carrera'].queryset = Carrera.objects.filter(
                    unidad_academica_id=unidad_academica_id
                ).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['carrera'].queryset = Carrera.objects.none()
        elif self.instance.pk and self.instance.unidad_academica:
            # Para edición, cargar las carreras de la unidad académica del objeto
            self.fields['carrera'].queryset = Carrera.objects.filter(
                unidad_academica=self.instance.unidad_academica
            ).order_by('nombre')
        
        if 'carrera' in self.data:
            try:
                carrera_id = int(self.data.get('carrera'))
                self.fields['asignatura'].queryset = Asignatura.objects.filter(
                    carrera_id=carrera_id
                ).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['asignatura'].queryset = Asignatura.objects.none()
        elif self.instance.pk and self.instance.carrera:
            # Para edición, cargar las asignaturas de la carrera del objeto
            self.fields['asignatura'].queryset = Asignatura.objects.filter(
                carrera=self.instance.carrera
            ).order_by('nombre')
        
        if 'asignatura' in self.data:
            try:
                asignatura_id = int(self.data.get('asignatura'))
                self.fields['unidad_tematica'].queryset = UnidadTematica.objects.filter(
                    asignatura_id=asignatura_id
                ).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['unidad_tematica'].queryset = UnidadTematica.objects.none()
        elif self.instance.pk and self.instance.asignatura:
            # Para edición, cargar las unidades temáticas de la asignatura del objeto
            self.fields['unidad_tematica'].queryset = UnidadTematica.objects.filter(
                asignatura=self.instance.asignatura
            ).order_by('nombre')
    
    class Meta:
        model = Insumo
        fields = [
            # Las 19 columnas oficiales
            'unidad_academica',           # 1. UNIDAD ACADÉMICA
            'laboratorio',                # 2. LABORATORIO
            'categoria',                  # 3. CATEGORÍA
            'nombre_elemento',            # 4. NOMBRE DEL ELEMENTO
            'descripcion_caracteristicas', # 5. DESCRIPCIÓN/CARACTERÍSTICAS
            'marca_modelo',               # 6. MARCA / MODELO
            'codigo_inventario',          # 7. CÓDIGO DE INVENTARIO (INTERNO)
            'estado',                     # 8. ESTADO
            'ubicacion_fisica',           # 9. UBICACIÓN FÍSICA
            'cantidad',                   # 10. CANTIDAD
            'unidad_medida',              # 11. UNIDAD DE MEDIDA
            'fecha_ingreso_compra',       # 12. FECHA DE INGRESO/COMPRA
            'uso_principal',              # 13. USO PRINCIPAL
            'carrera',                    # 14. CARRERA
            'asignatura',                 # 15. ASIGNATURA
            'unidad_tematica',            # 16. UNIDAD TEMÁTICA
            'condiciones_almacenamiento', # 17. CONDICIONES DE ALMACENAMIENTO
            'observaciones',              # 18. OBSERVACIONES
            'link_fotografia',            # 19. LINK DE LA FOTOGRAFÍA
        ]
        
        widgets = {
            # Información básica
            'unidad_academica': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
                'data-api-url': '/insumos/api/carreras/'
            }),
            'laboratorio': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'nombre_elemento': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Nombre del elemento'
            }),
            'descripcion_caracteristicas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada del elemento'
            }),
            'marca_modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marca y modelo'
            }),
            'codigo_inventario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Se genera automáticamente'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'ubicacion_fisica': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ubicación física del elemento'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'required': True,
                'min': '0',
                'step': '0.01'
            }),
            'unidad_medida': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'fecha_ingreso_compra': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'uso_principal': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            
            # Almacenamiento y observaciones
            'condiciones_almacenamiento': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales'
            }),
            'link_fotografia': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL de la fotografía del elemento'
            }),
        }
        
        labels = {
            'unidad_academica': 'Unidad Académica *',
            'laboratorio': 'Laboratorio *',
            'categoria': 'Categoría *',
            'nombre_elemento': 'Nombre del Elemento *',
            'descripcion_caracteristicas': 'Descripción/Características',
            'marca_modelo': 'Marca / Modelo',
            'codigo_inventario': 'Código de Inventario (Interno)',
            'estado': 'Estado *',
            'ubicacion_fisica': 'Ubicación Física',
            'cantidad': 'Cantidad *',
            'unidad_medida': 'Unidad de Medida *',
            'fecha_ingreso_compra': 'Fecha de Ingreso/Compra *',
            'uso_principal': 'Uso Principal *',
            'carrera': 'Carrera *',
            'asignatura': 'Asignatura *',
            'unidad_tematica': 'Unidad Temática *',
            'condiciones_almacenamiento': 'Condiciones de Almacenamiento *',
            'observaciones': 'Observaciones',
            'link_fotografia': 'Link de la Fotografía del Elemento',
        }


class InsumoFilterForm(forms.Form):
    """Formulario para filtrar insumos"""
    
    unidad_academica = forms.ModelChoiceField(
        queryset=UnidadAcademica.objects.all(),
        empty_label="Todas las unidades",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    laboratorio = forms.ModelChoiceField(
        queryset=Laboratorio.objects.all(),
        empty_label="Todos los laboratorios",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    categoria = forms.ChoiceField(
        choices=[('', 'Todas las categorías')] + Insumo.CATEGORIA_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Insumo.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all(),
        empty_label="Todas las carreras",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
