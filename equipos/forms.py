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
            'unidad_academica', 'carrera', 'semestre', 'asignatura',
            'carga_horaria_semanal', 'carga_horaria_semestral',
            'criterio_desempeno', 'unidad_didactica', 'contenido_analitico',
            'guia_laboratorio', 'practica', 'equipo_existente',
            'marca', 'modelo', 'estado', 'numero_unidades',
            'es_activo_fijo', 'fotografia_frontal', 'fotografia_placa',
            'laboratorio', 'seccion_area', 'identificador_aula',
            'equipo_requerido', 'numero_equipos_requeridos',
            'responsable_excel', 'observaciones'
        ]
        
        widgets = {
            'unidad_academica': forms.Select(attrs={
                'class': 'form-control',
                'onchange': 'cargarCarreras(this.value)'
            }),
            'carrera': forms.Select(attrs={
                'class': 'form-control',
                'onchange': 'cargarAsignaturas(this.value)'
            }),
            'semestre': forms.Select(attrs={'class': 'form-control'}),
            'asignatura': forms.Select(attrs={
                'class': 'form-control',
                'onchange': 'cargarDatosCurriculares(this.value)'
            }),
            'carga_horaria_semanal': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'carga_horaria_semestral': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'criterio_desempeno': forms.Select(attrs={
                'class': 'form-control',
                'data-live-search': 'true'
            }),
            'unidad_didactica': forms.Select(attrs={
                'class': 'form-control',
                'data-live-search': 'true',
                'onchange': 'cargarContenidosAnaliticos(this.value)'
            }),
            'contenido_analitico': forms.Select(attrs={
                'class': 'form-control',
                'data-live-search': 'true'
            }),
            'guia_laboratorio': forms.Select(attrs={'class': 'form-control'}),
            'practica': forms.Select(attrs={'class': 'form-control'}),
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
            'unidad_academica': 'Unidad Académica',
            'carrera': 'Carrera',
            'semestre': 'Semestre',
            'asignatura': 'Asignatura',
            'carga_horaria_semanal': 'Carga Horaria Semanal',
            'carga_horaria_semestral': 'Carga Horaria Semestral',
            'criterio_desempeno': 'Criterio de Desempeño',
            'unidad_didactica': 'Unidad Didáctica',
            'contenido_analitico': 'Contenido Analítico',
            'guia_laboratorio': 'Guía de Laboratorio',
            'practica': 'Práctica',
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
        self.fields['carrera'].queryset = Carrera.objects.all()
        self.fields['laboratorio'].queryset = Laboratorio.objects.all()
        
        # Semestres
        self.fields['semestre'].choices = [(i, f"{i}° Semestre") for i in range(1, 11)]
        
        # Si hay una instancia (estamos editando), cargar datos relacionados
        if self.instance and self.instance.pk:
            equipo = self.instance
            
            # Cargar asignaturas de la carrera seleccionada
            if equipo.carrera:
                self.fields['asignatura'].queryset = Asignatura.objects.filter(
                    carrera=equipo.carrera
                )
            else:
                self.fields['asignatura'].queryset = Asignatura.objects.none()
            
            # Cargar criterios de desempeño de la asignatura seleccionada
            if equipo.asignatura:
                self.fields['criterio_desempeno'].queryset = CriterioDesempeno.objects.filter(
                    asignatura=equipo.asignatura
                )
                
                # Cargar unidades didácticas de la asignatura
                self.fields['unidad_didactica'].queryset = UnidadDidactica.objects.filter(
                    asignatura=equipo.asignatura
                )
                
                # Cargar guías de laboratorio
                self.fields['guia_laboratorio'].queryset = GuiaLaboratorio.objects.filter(
                    unidad_tematica__asignatura=equipo.asignatura
                )
            else:
                self.fields['criterio_desempeno'].queryset = CriterioDesempeno.objects.none()
                self.fields['unidad_didactica'].queryset = UnidadDidactica.objects.none()
                self.fields['guia_laboratorio'].queryset = GuiaLaboratorio.objects.none()
            
            # Cargar contenidos analíticos de la unidad didáctica seleccionada
            if equipo.unidad_didactica:
                self.fields['contenido_analitico'].queryset = ContenidoAnalitico.objects.filter(
                    unidad_didactica=equipo.unidad_didactica
                )
            else:
                self.fields['contenido_analitico'].queryset = ContenidoAnalitico.objects.none()
            
            # Cargar prácticas de la guía seleccionada
            if equipo.guia_laboratorio:
                self.fields['practica'].queryset = Practica.objects.filter(
                    guia_laboratorio=equipo.guia_laboratorio
                )
            else:
                self.fields['practica'].queryset = Practica.objects.none()
        else:
            # Para nuevo equipo, inicializar con querysets vacíos que se llenarán por AJAX
            self.fields['asignatura'].queryset = Asignatura.objects.none()
            self.fields['criterio_desempeno'].queryset = CriterioDesempeno.objects.none()
            self.fields['unidad_didactica'].queryset = UnidadDidactica.objects.none()
            self.fields['contenido_analitico'].queryset = ContenidoAnalitico.objects.none()
            self.fields['guia_laboratorio'].queryset = GuiaLaboratorio.objects.none()
            self.fields['practica'].queryset = Practica.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        
        # Validaciones personalizadas
        carrera = cleaned_data.get('carrera')
        asignatura = cleaned_data.get('asignatura')
        
        if asignatura and carrera:
            if asignatura.carrera != carrera:
                raise forms.ValidationError("La asignatura debe pertenecer a la carrera seleccionada.")
        
        return cleaned_data
