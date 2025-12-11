from django import forms
from .models import ActivoFijo
from core.models import UnidadAcademica, Laboratorio, Carrera

class ActivoFijoForm(forms.ModelForm):
    """Formulario para crear y editar activos fijos"""
    
    class Meta:
        model = ActivoFijo
        fields = [
            'codigo_patrimonial',
            'nombre',
            'categoria',
            'marca',
            'modelo',
            'numero_serie',
            'descripcion',
            'especificaciones_tecnicas',
            'valor_adquisicion',
            'fecha_adquisicion',
            'proveedor',
            'numero_factura',
            'garantia_meses',
            'unidad_academica',
            'laboratorio',
            'carrera',
            'ubicacion_fisica',
            'responsable',
            'estado_fisico',
            'estado_operativo',
            'fecha_ultimo_mantenimiento',
            'frecuencia_mantenimiento_meses',
            'observaciones',
        ]
        
        widgets = {
            # Campos de texto básicos
            'codigo_patrimonial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: EMI-2024-001'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del activo'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marca del activo'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modelo del activo'
            }),
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de serie'
            }),
            'proveedor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del proveedor'
            }),
            'numero_factura': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de factura'
            }),
            'ubicacion_fisica': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Aula 101, Laboratorio A'
            }),
            'responsable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del responsable'
            }),
            
            # Áreas de texto
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada del activo'
            }),
            'especificaciones_tecnicas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Especificaciones técnicas detalladas'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales'
            }),
            
            # Selects
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'estado_fisico': forms.Select(attrs={'class': 'form-control'}),
            'estado_operativo': forms.Select(attrs={'class': 'form-control'}),
            'unidad_academica': forms.Select(attrs={'class': 'form-control'}),
            'laboratorio': forms.Select(attrs={'class': 'form-control'}),
            'carrera': forms.Select(attrs={'class': 'form-control'}),
            
            # Campos numéricos
            'valor_adquisicion': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'garantia_meses': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '12'
            }),
            'frecuencia_mantenimiento_meses': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '6'
            }),
            
            # Campos de fecha
            'fecha_adquisicion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_ultimo_mantenimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        
        labels = {
            'codigo_patrimonial': 'Código Patrimonial',
            'nombre': 'Nombre del Activo',
            'categoria': 'Categoría',
            'marca': 'Marca',
            'modelo': 'Modelo',
            'numero_serie': 'Número de Serie',
            'descripcion': 'Descripción',
            'especificaciones_tecnicas': 'Especificaciones Técnicas',
            'valor_adquisicion': 'Valor de Adquisición (Bs.)',
            'fecha_adquisicion': 'Fecha de Adquisición',
            'proveedor': 'Proveedor',
            'numero_factura': 'Número de Factura',
            'garantia_meses': 'Garantía (meses)',
            'unidad_academica': 'Unidad Académica',
            'laboratorio': 'Laboratorio',
            'carrera': 'Carrera',
            'ubicacion_fisica': 'Ubicación Física',
            'responsable': 'Responsable',
            'estado_fisico': 'Estado Físico',
            'estado_operativo': 'Estado Operativo',
            'fecha_ultimo_mantenimiento': 'Fecha Último Mantenimiento',
            'frecuencia_mantenimiento_meses': 'Frecuencia Mantenimiento (meses)',
            'observaciones': 'Observaciones',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar laboratorio y carrera como opcionales inicialmente
        self.fields['laboratorio'].required = False
        self.fields['carrera'].required = False
        
        # Si estamos editando un activo existente
        if self.instance.pk:
            # Filtrar laboratorios y carreras por unidad académica
            if self.instance.unidad_academica:
                self.fields['laboratorio'].queryset = Laboratorio.objects.filter(
                    unidad_academica=self.instance.unidad_academica
                )
                self.fields['carrera'].queryset = Carrera.objects.filter(
                    unidad_academica=self.instance.unidad_academica
                )
        else:
            # Para nuevos activos, mostrar queryset vacío inicialmente
            self.fields['laboratorio'].queryset = Laboratorio.objects.none()
            self.fields['carrera'].queryset = Carrera.objects.none()
    
    def clean_codigo_patrimonial(self):
        """Validar que el código patrimonial sea único"""
        codigo = self.cleaned_data['codigo_patrimonial']
        
        # Verificar unicidad
        queryset = ActivoFijo.objects.filter(codigo_patrimonial=codigo)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise forms.ValidationError(
                f'Ya existe un activo fijo con el código patrimonial "{codigo}"'
            )
        
        return codigo
    
    def clean_valor_adquisicion(self):
        """Validar que el valor de adquisición sea positivo"""
        valor = self.cleaned_data['valor_adquisicion']
        
        if valor is not None and valor <= 0:
            raise forms.ValidationError(
                'El valor de adquisición debe ser mayor a 0'
            )
        
        return valor
    
    def clean_garantia_meses(self):
        """Validar que la garantía sea un número positivo"""
        garantia = self.cleaned_data.get('garantia_meses')
        
        if garantia is not None and garantia < 0:
            raise forms.ValidationError(
                'La garantía no puede ser negativa'
            )
        
        return garantia
    
    def clean_frecuencia_mantenimiento_meses(self):
        """Validar que la frecuencia de mantenimiento sea positiva"""
        frecuencia = self.cleaned_data.get('frecuencia_mantenimiento_meses')
        
        if frecuencia is not None and frecuencia <= 0:
            raise forms.ValidationError(
                'La frecuencia de mantenimiento debe ser mayor a 0'
            )
        
        return frecuencia
    
    def clean(self):
        """Validaciones a nivel de formulario"""
        cleaned_data = super().clean()
        unidad_academica = cleaned_data.get('unidad_academica')
        laboratorio = cleaned_data.get('laboratorio')
        carrera = cleaned_data.get('carrera')
        fecha_adquisicion = cleaned_data.get('fecha_adquisicion')
        fecha_ultimo_mantenimiento = cleaned_data.get('fecha_ultimo_mantenimiento')
        
        # Validar que laboratorio pertenezca a la unidad académica
        if laboratorio and unidad_academica:
            if laboratorio.unidad_academica != unidad_academica:
                raise forms.ValidationError(
                    'El laboratorio seleccionado no pertenece a la unidad académica elegida'
                )
        
        # Validar que carrera pertenezca a la unidad académica
        if carrera and unidad_academica:
            if carrera.unidad_academica != unidad_academica:
                raise forms.ValidationError(
                    'La carrera seleccionada no pertenece a la unidad académica elegida'
                )
        
        # Validar fechas
        if fecha_ultimo_mantenimiento and fecha_adquisicion:
            if fecha_ultimo_mantenimiento < fecha_adquisicion:
                raise forms.ValidationError(
                    'La fecha del último mantenimiento no puede ser anterior a la fecha de adquisición'
                )
        
        return cleaned_data


class FiltroActivosForm(forms.Form):
    """Formulario para filtrar activos fijos"""
    
    codigo_patrimonial = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por código patrimonial...'
        })
    )
    
    nombre_activo = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar en nombre, marca, modelo...'
        })
    )
    
    categoria = forms.ChoiceField(
        choices=[('', 'Todas las categorías')] + ActivoFijo.CATEGORIAS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    unidad_academica = forms.ModelChoiceField(
        queryset=UnidadAcademica.objects.all(),
        required=False,
        empty_label="Todas las unidades",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    estado_fisico = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + ActivoFijo.ESTADOS_FISICOS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    estado_operativo = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + ActivoFijo.ESTADOS_OPERATIVOS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )