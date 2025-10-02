from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import (
    Asignatura, Carrera, UnidadAcademica, CriterioDesempeno, UnidadDidactica, 
    ContenidoAnalitico, Bibliografia, PracticaLaboratorio, Titulo, Competencias,
    ObjetivoPractica, FundamentoTeorico, MaterialesHerramientasEquipos, 
    Procedimientos, CalculosResultados, Cuestionario
)


class AsignaturaCompletaForm(forms.ModelForm):
    """Formulario completo para crear/editar asignaturas con todos los campos"""
    
    class Meta:
        model = Asignatura
        fields = [
            'nombre', 'carrera', 'semestre', 'codigo_competencia', 
            'sigla_curricular', 'carga_horaria_semanal', 'carga_horaria_semestral'
        ]
        widgets = {
            'nombre': forms.Select(attrs={'class': 'form-control'}),
            'carrera': forms.Select(attrs={'class': 'form-control'}),
            'semestre': forms.Select(attrs={'class': 'form-control'}),
            'codigo_competencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código de competencia de la materia'
            }),
            'sigla_curricular': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sigla curricular de la asignatura'
            }),
            'carga_horaria_semanal': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '20'
            }),
            'carga_horaria_semestral': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '200'
            }),
        }
        labels = {
            'nombre': 'Asignatura',
            'carrera': 'Carrera',
            'semestre': 'Semestre',
            'codigo_competencia': 'Código de Competencia',
            'sigla_curricular': 'Sigla Curricular',
            'carga_horaria_semanal': 'Carga Horaria Semanal',
            'carga_horaria_semestral': 'Carga Horaria Semestral',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrado jerárquico de carreras por unidad académica
        if 'unidad_academica' in self.data:
            try:
                unidad_id = int(self.data.get('unidad_academica'))
                self.fields['carrera'].queryset = Carrera.objects.filter(unidad_academica_id=unidad_id)
            except (ValueError, TypeError):
                pass


class CriterioDesempenoForm(forms.ModelForm):
    """Formulario para criterios de desempeño"""
    
    class Meta:
        model = CriterioDesempeno
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del criterio de desempeño'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada del criterio'
            }),
        }


class UnidadDidacticaForm(forms.ModelForm):
    """Formulario para unidades didácticas"""
    
    class Meta:
        model = UnidadDidactica
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la unidad didáctica'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la unidad didáctica'
            }),
        }


class ContenidoAnaliticoForm(forms.ModelForm):
    """Formulario para contenidos analíticos"""
    
    class Meta:
        model = ContenidoAnalitico
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del contenido analítico'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del contenido analítico'
            }),
        }


# =====================================
# FORMULARIOS PARA COMPONENTES DETALLADOS
# =====================================

class BibliografiaForm(forms.ModelForm):
    """Formulario para bibliografía"""
    
    class Meta:
        model = Bibliografia
        fields = [
            'titulo', 'autor', 'editorial', 'año_publicacion', 
            'paginas', 'isbn', 'tipo_referencia', 'orden'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la bibliografía'}),
            'autor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Autor'}),
            'editorial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Editorial'}),
            'año_publicacion': forms.NumberInput(attrs={'class': 'form-control', 'min': '1900', 'max': '2050'}),
            'paginas': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 45-67'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ISBN'}),
            'tipo_referencia': forms.Select(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }


class PracticaLaboratorioForm(forms.ModelForm):
    """Formulario para prácticas de laboratorio"""
    
    class Meta:
        model = PracticaLaboratorio
        fields = ['nombre', 'duracion_horas', 'tipo_practica', 'numero_estudiantes', 'orden']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la práctica'}),
            'duracion_horas': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.5', 'step': '0.5'}),
            'tipo_practica': forms.Select(attrs={'class': 'form-control'}),
            'numero_estudiantes': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }


class TituloForm(forms.ModelForm):
    """Formulario para títulos"""
    
    class Meta:
        model = Titulo
        fields = ['texto', 'nivel', 'orden']
        widgets = {
            'texto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Texto del título'}),
            'nivel': forms.Select(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }


class CompetenciasForm(forms.ModelForm):
    """Formulario para competencias"""
    
    class Meta:
        model = Competencias
        fields = ['descripcion', 'tipo_competencia', 'nivel_desarrollo', 'orden']
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción de la competencia'}),
            'tipo_competencia': forms.Select(attrs={'class': 'form-control'}),
            'nivel_desarrollo': forms.Select(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }


class ObjetivoPracticaForm(forms.ModelForm):
    """Formulario para objetivos de práctica"""
    
    class Meta:
        model = ObjetivoPractica
        fields = ['descripcion', 'tipo_objetivo', 'orden']
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del objetivo'}),
            'tipo_objetivo': forms.Select(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }


class FundamentoTeoricoForm(forms.ModelForm):
    """Formulario para fundamentos teóricos"""
    
    class Meta:
        model = FundamentoTeorico
        fields = ['titulo', 'contenido', 'referencias', 'orden']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del fundamento'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Contenido teórico'}),
            'referencias': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Referencias adicionales'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }


class MaterialesHerramientasEquiposForm(forms.ModelForm):
    """Formulario para materiales, herramientas y equipos"""
    
    class Meta:
        model = MaterialesHerramientasEquipos
        fields = ['nombre', 'tipo_elemento', 'cantidad', 'especificaciones', 'es_obligatorio', 'orden']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del material/herramienta/equipo'}),
            'tipo_elemento': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2 unidades, 500ml, etc.'}),
            'especificaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Especificaciones técnicas'}),
            'es_obligatorio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }


class ProcedimientosForm(forms.ModelForm):
    """Formulario para procedimientos"""
    
    class Meta:
        model = Procedimientos
        fields = ['numero_paso', 'titulo_paso', 'descripcion', 'tiempo_estimado', 'precauciones', 'observaciones', 'orden']
        widgets = {
            'numero_paso': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'titulo_paso': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del paso'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción detallada del paso'}),
            'tiempo_estimado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 15 minutos'}),
            'precauciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Precauciones especiales'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observaciones'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }


class CalculosResultadosForm(forms.ModelForm):
    """Formulario para cálculos y resultados"""
    
    class Meta:
        model = CalculosResultados
        fields = ['titulo', 'formula', 'procedimiento_calculo', 'resultado_esperado', 'unidades', 'margen_error', 'orden']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del cálculo/resultado'}),
            'formula': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Fórmula utilizada'}),
            'procedimiento_calculo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Procedimiento de cálculo'}),
            'resultado_esperado': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Resultado esperado'}),
            'unidades': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: kg, m/s, etc.'}),
            'margen_error': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: ±5%'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }


class CuestionarioForm(forms.ModelForm):
    """Formulario para cuestionarios"""
    
    class Meta:
        model = Cuestionario
        fields = ['numero_pregunta', 'pregunta', 'tipo_pregunta', 'respuesta_esperada', 'puntuacion', 'orden']
        widgets = {
            'numero_pregunta': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'pregunta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Texto de la pregunta'}),
            'tipo_pregunta': forms.Select(attrs={'class': 'form-control'}),
            'respuesta_esperada': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Respuesta esperada o criterios'}),
            'puntuacion': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }


# =====================================
# FORMSETS PARA MÚLTIPLES INSTANCIAS
# =====================================

# Formsets para permitir múltiples instancias de cada componente
BibliografiaFormSet = inlineformset_factory(
    ContenidoAnalitico, Bibliografia, form=BibliografiaForm, extra=1, can_delete=True
)

PracticaLaboratorioFormSet = inlineformset_factory(
    ContenidoAnalitico, PracticaLaboratorio, form=PracticaLaboratorioForm, extra=1, can_delete=True
)

TituloFormSet = inlineformset_factory(
    ContenidoAnalitico, Titulo, form=TituloForm, extra=1, can_delete=True
)

CompetenciasFormSet = inlineformset_factory(
    ContenidoAnalitico, Competencias, form=CompetenciasForm, extra=1, can_delete=True
)

ObjetivoPracticaFormSet = inlineformset_factory(
    ContenidoAnalitico, ObjetivoPractica, form=ObjetivoPracticaForm, extra=1, can_delete=True
)

FundamentoTeoricoFormSet = inlineformset_factory(
    ContenidoAnalitico, FundamentoTeorico, form=FundamentoTeoricoForm, extra=1, can_delete=True
)

MaterialesHerramientasEquiposFormSet = inlineformset_factory(
    ContenidoAnalitico, MaterialesHerramientasEquipos, form=MaterialesHerramientasEquiposForm, extra=1, can_delete=True
)

ProcedimientosFormSet = inlineformset_factory(
    ContenidoAnalitico, Procedimientos, form=ProcedimientosForm, extra=1, can_delete=True
)

CalculosResultadosFormSet = inlineformset_factory(
    ContenidoAnalitico, CalculosResultados, form=CalculosResultadosForm, extra=1, can_delete=True
)

CuestionarioFormSet = inlineformset_factory(
    ContenidoAnalitico, Cuestionario, form=CuestionarioForm, extra=1, can_delete=True
)


# =====================================
# FORMULARIO JERÁRQUICO PRINCIPAL
# =====================================

class UnidadAcademicaCarreraForm(forms.Form):
    """Formulario auxiliar para selección jerárquica"""
    
    unidad_academica = forms.ModelChoiceField(
        queryset=UnidadAcademica.objects.all(),
        empty_label="Selecciona una unidad académica",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Unidad Académica"
    )
    
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.none(),
        empty_label="Primero selecciona una unidad académica",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Carrera"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'unidad_academica' in self.data:
            try:
                unidad_id = int(self.data.get('unidad_academica'))
                self.fields['carrera'].queryset = Carrera.objects.filter(unidad_academica_id=unidad_id)
                self.fields['carrera'].empty_label = "Selecciona una carrera"
            except (ValueError, TypeError):
                pass

# Formulario de prueba para CKEditor 5
class FundamentoTeoricoForm(forms.ModelForm):
    """Formulario para probar CKEditor 5"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contenido"].required = False
        self.fields["referencias"].required = False

    class Meta:
        model = FundamentoTeorico
        fields = ('contenido', 'referencias')
        widgets = {
            'contenido': CKEditor5Widget(
                attrs={'class': 'django_ckeditor_5'},
                config_name='extends'
            ),
            'referencias': CKEditor5Widget(
                attrs={'class': 'django_ckeditor_5'},
                config_name='default'
            )
        }