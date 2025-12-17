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
            'required': True,
            'data-api-url': '/insumos/api/guias-laboratorio/'
        })
    )
    
    guia_laboratorio = forms.ModelChoiceField(
        queryset=GuiaLaboratorio.objects.none(),
        empty_label="Seleccione una guía de laboratorio",
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'data-api-url': '/insumos/api/practicas/'
        })
    )
    
    practica = forms.ModelChoiceField(
        queryset=Practica.objects.none(),
        empty_label="Seleccione una práctica",
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
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
        
        # Cargar guías de laboratorio basándose en la unidad temática
        if 'unidad_tematica' in self.data:
            try:
                unidad_tematica_id = int(self.data.get('unidad_tematica'))
                self.fields['guia_laboratorio'].queryset = GuiaLaboratorio.objects.filter(
                    unidad_tematica_id=unidad_tematica_id
                ).order_by('numero', 'nombre')
            except (ValueError, TypeError):
                self.fields['guia_laboratorio'].queryset = GuiaLaboratorio.objects.none()
        elif self.instance.pk and self.instance.unidad_tematica:
            # Para edición, cargar las guías de la unidad temática del objeto
            self.fields['guia_laboratorio'].queryset = GuiaLaboratorio.objects.filter(
                unidad_tematica=self.instance.unidad_tematica
            ).order_by('numero', 'nombre')
        
        # Cargar prácticas basándose en la guía de laboratorio
        if 'guia_laboratorio' in self.data:
            try:
                guia_laboratorio_id = int(self.data.get('guia_laboratorio'))
                self.fields['practica'].queryset = Practica.objects.filter(
                    guia_laboratorio_id=guia_laboratorio_id
                ).order_by('numero', 'nombre')
            except (ValueError, TypeError):
                self.fields['practica'].queryset = Practica.objects.none()
        elif self.instance.pk and self.instance.guia_laboratorio:
            # Para edición, cargar las prácticas de la guía del objeto
            self.fields['practica'].queryset = Practica.objects.filter(
                guia_laboratorio=self.instance.guia_laboratorio
            ).order_by('numero', 'nombre')
    
    def clean_carrera(self):
        """Validación personalizada para carrera"""
        carrera = self.cleaned_data.get('carrera')
        unidad_academica = self.cleaned_data.get('unidad_academica')
        
        if carrera and unidad_academica:
            # Verificar que la carrera pertenezca a la unidad académica seleccionada
            if not Carrera.objects.filter(id=carrera.id, unidad_academica=unidad_academica).exists():
                raise forms.ValidationError("La carrera seleccionada no pertenece a la unidad académica.")
        
        return carrera
    
    def clean_asignatura(self):
        """Validación personalizada para asignatura"""
        asignatura = self.cleaned_data.get('asignatura')
        carrera = self.cleaned_data.get('carrera')
        
        if asignatura and carrera:
            # Verificar que la asignatura pertenezca a la carrera seleccionada
            if not Asignatura.objects.filter(id=asignatura.id, carrera=carrera).exists():
                raise forms.ValidationError("La asignatura seleccionada no pertenece a la carrera.")
        
        return asignatura
    
    def clean_unidad_tematica(self):
        """Validación personalizada para unidad temática"""
        unidad_tematica = self.cleaned_data.get('unidad_tematica')
        asignatura = self.cleaned_data.get('asignatura')
        
        if unidad_tematica and asignatura:
            # Verificar que la unidad temática pertenezca a la asignatura seleccionada
            if not UnidadTematica.objects.filter(id=unidad_tematica.id, asignatura=asignatura).exists():
                raise forms.ValidationError("La unidad temática seleccionada no pertenece a la asignatura.")
        
        return unidad_tematica
    
    def clean_guia_laboratorio(self):
        """Validación personalizada para guía de laboratorio"""
        guia_laboratorio = self.cleaned_data.get('guia_laboratorio')
        unidad_tematica = self.cleaned_data.get('unidad_tematica')
        
        # Si no se selecciona guía, está bien (campo opcional)
        if not guia_laboratorio:
            return None
            
        # Validar solo si se proporcionó una guía
        if guia_laboratorio:
            # Verificar que existe en la base de datos
            if not GuiaLaboratorio.objects.filter(id=guia_laboratorio.id).exists():
                raise forms.ValidationError("La guía de laboratorio seleccionada no es válida.")
            
            # Si también hay unidad temática, verificar relación
            if unidad_tematica:
                if not GuiaLaboratorio.objects.filter(id=guia_laboratorio.id, unidad_tematica=unidad_tematica).exists():
                    raise forms.ValidationError("La guía de laboratorio seleccionada no pertenece a la unidad temática.")
        
        return guia_laboratorio
    
    def clean_practica(self):
        """Validación personalizada para práctica"""
        practica = self.cleaned_data.get('practica')
        guia_laboratorio = self.cleaned_data.get('guia_laboratorio')
        
        # Si no se selecciona práctica, está bien (campo opcional)
        if not practica:
            return None
            
        # Validar solo si se proporcionó una práctica
        if practica:
            # Verificar que existe en la base de datos
            if not Practica.objects.filter(id=practica.id).exists():
                raise forms.ValidationError("La práctica seleccionada no es válida.")
            
            # Si también hay guía, verificar relación
            if guia_laboratorio:
                if not Practica.objects.filter(id=practica.id, guia_laboratorio=guia_laboratorio).exists():
                    raise forms.ValidationError("La práctica seleccionada no pertenece a la guía de laboratorio.")
        
        return practica
    
    def clean_codigo_inventario(self):
        """Convert empty string to None to avoid unique constraint issues"""
        codigo = self.cleaned_data.get('codigo_inventario')
        if codigo == '':
            return None
        return codigo

    class Meta:
        model = Insumo
        fields = [
            # Las 21 columnas oficiales (agregamos Guía y Práctica)
            'seccion',                    # Sección a la que pertenece el insumo
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
            'guia_laboratorio',           # 17. GUÍA DE LABORATORIO
            'practica',                   # 18. PRÁCTICA
            'condiciones_almacenamiento', # 19. CONDICIONES DE ALMACENAMIENTO
            'observaciones',              # 20. OBSERVACIONES
            'link_fotografia',            # 21. LINK DE LA FOTOGRAFÍA
        ]
        
        widgets = {
            # Sección
            'seccion': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
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
            'seccion': 'Sección *',
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
        choices=[('', 'Todas las categorías')] + Insumo.CATEGORIAS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Insumo.ESTADOS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all(),
        empty_label="Todas las carreras",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
