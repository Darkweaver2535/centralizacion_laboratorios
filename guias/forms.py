from django import forms
from django.contrib.auth.models import User
from core.models import Carrera, Asignatura
from .models import GuiaGenerada


class GuiaLaboratorioForm(forms.ModelForm):
    """Formulario para generar una nueva guía de laboratorio"""
    
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si hay datos en el request, cargar las opciones correspondientes
        if 'carrera' in self.data:
            try:
                carrera_id = int(self.data.get('carrera'))
                self.fields['asignatura'].queryset = Asignatura.objects.filter(
                    carrera_id=carrera_id
                ).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['asignatura'].queryset = Asignatura.objects.none()
        elif self.instance.pk and self.instance.carrera:
            # Para edición
            self.fields['asignatura'].queryset = Asignatura.objects.filter(
                carrera=self.instance.carrera
            ).order_by('nombre')
    
    class Meta:
        model = GuiaGenerada
        fields = [
            'carrera',
            'semestre', 
            'asignatura',
            'contenido_analitico',
            'unidad_didactica',
            'titulo'
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
        }
        
        labels = {
            'carrera': 'Carrera *',
            'semestre': 'Semestre *',
            'asignatura': 'Asignatura *',
            'contenido_analitico': 'Contenido Analítico *',
            'unidad_didactica': 'Unidad Didáctica *',
            'titulo': 'Título de la Práctica *',
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
