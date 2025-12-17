from django import forms
from equipos.models import Equipo
from core.models import (
    UnidadAcademica, Carrera, Asignatura, UnidadTematica, 
    GuiaLaboratorio, Practica, Laboratorio, CriterioDesempeno,
    UnidadDidactica, ContenidoAnalitico
)

class EquipoForm(forms.ModelForm):
    """Formulario para editar equipos con datos del Excel de malla curricular"""
    
    class Meta:
        model = Equipo
        fields = [
            'seccion',  # Sección a la que pertenece el equipo
            'unidad_academica', 'carrera', 'semestre', 'asignatura',
            'carga_horaria_semanal', 'carga_horaria_semestral',
            'equipo_existente', 'marca', 'modelo', 'estado', 'numero_unidades',
            'es_activo_fijo', 'fotografia_frontal', 'fotografia_placa',
            'laboratorio', 'seccion_area', 'identificador_aula',
            'equipo_requerido', 'numero_equipos_requeridos',
            'responsable_excel', 'observaciones'
        ]
        
        widgets = {
            'seccion': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'unidad_academica': forms.Select(attrs={
                'class': 'form-control'
            }),
            'carrera': forms.Select(attrs={
                'class': 'form-control'
            }),
            'semestre': forms.Select(attrs={'class': 'form-control'}),
            'asignatura': forms.Select(attrs={
                'class': 'form-control'
            }),
            'carga_horaria_semanal': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'carga_horaria_semestral': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'equipo_existente': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'numero_unidades': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'es_activo_fijo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fotografia_frontal': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'fotografia_placa': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'laboratorio': forms.Select(attrs={'class': 'form-control'}),
            'seccion_area': forms.TextInput(attrs={'class': 'form-control'}),
            'identificador_aula': forms.TextInput(attrs={'class': 'form-control'}),
            'equipo_requerido': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'id_equipo_requerido',
                'list': 'equipos-ualp-list',
                'placeholder': 'Buscar y seleccionar equipo de la UALP...',
                'autocomplete': 'off'
            }),
            'numero_equipos_requeridos': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'responsable_excel': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }
        
        labels = {
            'seccion': 'Sección',
            'unidad_academica': 'Unidad Académica',
            'carrera': 'Carrera',
            'semestre': 'Semestre',
            'asignatura': 'Asignatura',
            'carga_horaria_semanal': 'Carga Horaria Semanal',
            'carga_horaria_semestral': 'Carga Horaria Semestral',
            'equipo_existente': 'Nombre del Equipo',
            'marca': 'Marca',
            'modelo': 'Modelo',
            'estado': 'Estado',
            'numero_unidades': 'Número de Unidades',
            'es_activo_fijo': 'Es Activo Fijo',
            'fotografia_frontal': 'Fotografía Frontal',
            'fotografia_placa': 'Fotografía de Placa',
            'laboratorio': 'Laboratorio',
            'seccion_area': 'Sección/Área',
            'identificador_aula': 'Identificador de Aula',
            'equipo_requerido': 'Equipo Requerido',
            'numero_equipos_requeridos': 'Número de Equipos Requeridos',
            'responsable_excel': 'Responsable',
            'observaciones': 'Observaciones'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cargar todas las opciones dinámicamente
        self.fields['unidad_academica'].queryset = UnidadAcademica.objects.all()
        self.fields['laboratorio'].queryset = Laboratorio.objects.all()
        
        # Semestres
        self.fields['semestre'].choices = [(i, f"{i}° Semestre") for i in range(1, 11)]
        
        # Si hay una instancia (estamos editando), cargar datos relacionados
        if self.instance and self.instance.pk:
            equipo = self.instance
            
            # Cargar carreras de la unidad académica seleccionada
            if equipo.unidad_academica:
                self.fields['carrera'].queryset = Carrera.objects.filter(
                    unidad_academica=equipo.unidad_academica
                )
            else:
                self.fields['carrera'].queryset = Carrera.objects.all()
            
            # Cargar asignaturas de la carrera seleccionada
            if equipo.carrera:
                self.fields['asignatura'].queryset = Asignatura.objects.filter(
                    carrera=equipo.carrera
                )
            else:
                self.fields['asignatura'].queryset = Asignatura.objects.all()
        else:
            # Para nuevos equipos, permitir todas las opciones
            # La validación de relaciones se hará en clean_asignatura
            self.fields['carrera'].queryset = Carrera.objects.all()
            self.fields['asignatura'].queryset = Asignatura.objects.all()

    def clean_asignatura(self):
        """Validación personalizada para asignatura"""
        asignatura = self.cleaned_data.get('asignatura')
        carrera = self.data.get('carrera')
        
        if asignatura and carrera:
            # Verificar que la asignatura pertenezca a la carrera
            if str(asignatura.carrera_id) != str(carrera):
                raise forms.ValidationError("La asignatura debe pertenecer a la carrera seleccionada.")
        
        return asignatura
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
