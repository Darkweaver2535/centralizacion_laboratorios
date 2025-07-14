from django import forms
from .models import *

class UnidadAcademicaForm(forms.Form):
    unidad_academica = forms.ChoiceField(
        choices=[
            ('', 'Seleccione una unidad académica'),
            ('la_paz', 'La Paz'),
            ('cochabamba', 'Cochabamba'),
            ('santa_cruz', 'Santa Cruz'),
            ('riberalta', 'Riberalta'),
            ('tropico', 'Trópico'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class InformacionAcademicaForm(forms.Form):
    semestre = forms.ChoiceField(
        choices=[('', 'Seleccione un semestre')] + [(str(i), f"{i}° Semestre") for i in range(1, 11)],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'updateMaterias()'
        })
    )
    
    carrera = forms.ChoiceField(
        choices=[
            ('', 'Seleccione una carrera'),
            ('ingenieria_sistemas', 'Ingeniería de Sistemas'),
            ('ingenieria_civil', 'Ingeniería Civil'),
            ('ingenieria_industrial', 'Ingeniería Industrial'),
            ('ingenieria_electronica', 'Ingeniería Electrónica'),
            ('ingenieria_mecanica', 'Ingeniería Mecánica'),
            ('ingenieria_quimica', 'Ingeniería Química'),
            ('ingenieria_petrolera', 'Ingeniería Petrolera'),
            ('ingenieria_ambiental', 'Ingeniería Ambiental'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    materia = forms.ChoiceField(
        choices=[('', 'Seleccione primero el semestre')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si se proporciona un semestre, actualizar las opciones de materia
        if self.data.get('semestre'):
            try:
                semestre = int(self.data.get('semestre'))
                materias = Materia.get_materias_por_semestre(semestre)
                self.fields['materia'].choices = [('', 'Seleccione una materia')] + materias
            except (ValueError, TypeError):
                pass

class LaboratorioForm(forms.Form):
    laboratorio = forms.ChoiceField(
        choices=[
            ('', 'Seleccione un laboratorio'),
            ('lab_fisica_mecanica', 'Laboratorio de Física Mecánica'),
            ('lab_quimica_general', 'Laboratorio de Química General'),
            ('lab_electronica_basica', 'Laboratorio de Electrónica Básica'),
            ('lab_programacion', 'Laboratorio de Programación'),
            ('lab_circuitos_electricos', 'Laboratorio de Circuitos Eléctricos'),
            ('lab_materiales_resistencia', 'Laboratorio de Materiales y Resistencia'),
            ('lab_fluidos_termodinamica', 'Laboratorio de Fluidos y Termodinámica'),
            ('lab_sistemas_control', 'Laboratorio de Sistemas de Control'),
            ('lab_redes_computadoras', 'Laboratorio de Redes de Computadoras'),
            ('lab_automatizacion', 'Laboratorio de Automatización Industrial'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class EnsayoEquipoForm(forms.Form):
    ensayos = forms.ChoiceField(
        choices=[
            ('', 'Seleccione un ensayo'),
            ('ensayo_traccion', 'Ensayo de Tracción'),
            ('ensayo_compresion', 'Ensayo de Compresión'),
            ('ensayo_dureza', 'Ensayo de Dureza'),
            ('ensayo_impacto', 'Ensayo de Impacto'),
            ('ensayo_ph', 'Ensayo de pH'),
            ('ensayo_conductividad', 'Ensayo de Conductividad Eléctrica'),
            ('ensayo_densidad', 'Ensayo de Densidad'),
            ('ensayo_viscosidad', 'Ensayo de Viscosidad'),
            ('ensayo_microscopia', 'Ensayo de Microscopía'),
            ('ensayo_espectroscopia', 'Ensayo de Espectroscopía'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )