from django import forms
from django.contrib.auth import get_user_model
from core.models import Carrera, Asignatura
from equipos.models import Equipo
from insumos.models import Insumo
from .models import GuiaGenerada

User = get_user_model()


class GuiaLaboratorioForm(forms.ModelForm):
    """Formulario completo para generar/editar una guía de laboratorio"""
    
    # Campo dinámico para asignatura
    asignatura = forms.ModelChoiceField(
        queryset=Asignatura.objects.none(),
        empty_label="Seleccione una asignatura",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    
    # Campos ManyToMany con widgets mejorados
    equipos_requeridos = forms.ModelMultipleChoiceField(
        queryset=Equipo.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'style': 'width: 100%',
            'data-placeholder': 'Seleccione equipos necesarios'
        }),
        help_text='Seleccione los equipos requeridos para esta práctica'
    )
    
    insumos_requeridos = forms.ModelMultipleChoiceField(
        queryset=Insumo.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'style': 'width: 100%',
            'data-placeholder': 'Seleccione insumos necesarios'
        }),
        help_text='Seleccione los insumos requeridos para esta práctica'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si hay datos en el request, cargar las opciones correspondientes
        if 'carrera' in self.data:
            try:
                carrera_id = int(self.data.get('carrera'))
                self.fields['asignatura'].queryset = Asignatura.objects.filter(
                    carrera_id=carrera_id
                ).order_by('nombre')
                
                # Filtrar equipos e insumos por carrera
                self.fields['equipos_requeridos'].queryset = Equipo.objects.filter(
                    carrera_id=carrera_id,
                    estado__in=['operativo', 'buen_estado']
                ).order_by('equipo_existente')
                
                self.fields['insumos_requeridos'].queryset = Insumo.objects.filter(
                    estado__in=['disponible', 'por_comprar']
                ).order_by('nombre_elemento')
                
            except (ValueError, TypeError):
                self.fields['asignatura'].queryset = Asignatura.objects.none()
        elif self.instance.pk and self.instance.carrera:
            # Para edición
            self.fields['asignatura'].queryset = Asignatura.objects.filter(
                carrera=self.instance.carrera
            ).order_by('nombre')
            
            # Cargar equipos e insumos disponibles
            self.fields['equipos_requeridos'].queryset = Equipo.objects.filter(
                carrera=self.instance.carrera,
                estado__in=['operativo', 'buen_estado']
            ).order_by('equipo_existente')
            
            self.fields['insumos_requeridos'].queryset = Insumo.objects.filter(
                estado__in=['disponible', 'por_comprar']
            ).order_by('nombre_elemento')
    
    class Meta:
        model = GuiaGenerada
        fields = [
            'carrera',
            'semestre', 
            'asignatura',
            'contenido_analitico',
            'unidad_didactica',
            'titulo',
            'tipo_practica',
            'duracion_horas',
            'numero_practica',
            'competencias',
            'criterios_desempeno',
            'equipos_requeridos',
            'insumos_requeridos',
        ]
        
        widgets = {
            'carrera': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
                'data-api-url': '/guias/api/asignaturas/'
            }),
            'semestre': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'contenido_analitico': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'required': True,
                'placeholder': 'Ingrese el contenido analítico de la asignatura'
            }),
            'unidad_didactica': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Ejemplo: Unidad 1 - Fundamentos básicos'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Título de la práctica de laboratorio'
            }),
            'tipo_practica': forms.Select(attrs={
                'class': 'form-control',
            }),
            'duracion_horas': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '8',
                'placeholder': '2'
            }),
            'numero_practica': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': '1'
            }),
            'competencias': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Competencias a desarrollar'
            }),
            'criterios_desempeno': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Criterios de desempeño'
            }),
        }
        
        labels = {
            'carrera': 'Carrera *',
            'semestre': 'Semestre *',
            'asignatura': 'Asignatura *',
            'contenido_analitico': 'Contenido Analítico *',
            'unidad_didactica': 'Unidad Didáctica *',
            'titulo': 'Título de la Práctica *',
            'tipo_practica': 'Tipo de Práctica',
            'duracion_horas': 'Duración (horas)',
            'numero_practica': 'Número de Práctica',
            'competencias': 'Competencias',
            'criterios_desempeno': 'Criterios de Desempeño',
            'equipos_requeridos': 'Equipos Requeridos',
            'insumos_requeridos': 'Insumos Requeridos',
        }
    
    def clean_asignatura(self):
        """Validación personalizada para asignatura"""
        asignatura = self.cleaned_data.get('asignatura')
        carrera = self.cleaned_data.get('carrera')
        
        if asignatura and carrera:
            # Verificar que la asignatura pertenezca a la carrera seleccionada
            if not Asignatura.objects.filter(id=asignatura.id, carrera=carrera).exists():
                raise forms.ValidationError("La asignatura seleccionada no pertenece a la carrera.")
        
        return asignatura


class GuiaFilterForm(forms.Form):
    """Formulario para filtrar guías generadas"""
    
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all(),
        empty_label="Todas las carreras",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    semestre = forms.ChoiceField(
        choices=[('', 'Todos los semestres')] + GuiaGenerada.SEMESTRES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
