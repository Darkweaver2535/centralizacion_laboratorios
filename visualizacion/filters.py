import django_filters
from django import forms
from equipos.models import Equipo
from insumos.models import Insumo
from guias.models import GuiaGenerada
from core.models import UnidadAcademica, Carrera, Asignatura


class EquipoFilter(django_filters.FilterSet):
    """Filtros para el modelo Equipo"""
    
    search = django_filters.CharFilter(
        method='filter_search',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar equipos...'
        })
    )
    
    equipo_existente = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre de equipo...'
        })
    )
    
    unidad_academica = django_filters.ModelChoiceFilter(
        queryset=UnidadAcademica.objects.all(),
        empty_label="Todas las unidades académicas",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    carrera = django_filters.ModelChoiceFilter(
        queryset=Carrera.objects.all(),
        empty_label="Todas las carreras",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    semestre = django_filters.ChoiceFilter(
        choices=[
            ('', 'Todos los semestres'),
            (1, '1° Semestre'),
            (2, '2° Semestre'),
            (3, '3° Semestre'),
            (4, '4° Semestre'),
            (5, '5° Semestre'),
            (6, '6° Semestre'),
            (7, '7° Semestre'),
            (8, '8° Semestre'),
            (9, '9° Semestre'),
            (10, '10° Semestre'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    asignatura = django_filters.ModelChoiceFilter(
        queryset=Asignatura.objects.all(),
        empty_label="Todas las asignaturas",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    estado = django_filters.ChoiceFilter(
        choices=[
            ('', 'Todos los estados'),
            ('excelente', 'Excelente'),
            ('bueno', 'Bueno'),
            ('regular', 'Regular'),
            ('malo', 'Malo'),
            ('inservible', 'Inservible'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def filter_search(self, queryset, name, value):
        """Búsqueda general en múltiples campos"""
        if value:
            from django.db.models import Q
            return queryset.filter(
                Q(equipo_existente__icontains=value) |
                Q(marca__icontains=value) |
                Q(modelo__icontains=value) |
                Q(unidad_academica__nombre__icontains=value) |
                Q(carrera__nombre__icontains=value)
            )
        return queryset

    class Meta:
        model = Equipo
        fields = ['search', 'equipo_existente', 'unidad_academica', 'carrera', 'semestre', 'asignatura', 'estado']


class InsumoFilter(django_filters.FilterSet):
    """Filtros para el modelo Insumo"""
    
    search = django_filters.CharFilter(
        method='filter_search',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar insumos...'
        })
    )
    
    nombre_elemento = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre de insumo...'
        })
    )
    
    unidad_academica = django_filters.ModelChoiceFilter(
        queryset=UnidadAcademica.objects.all(),
        empty_label="Todas las unidades académicas",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    carrera = django_filters.ModelChoiceFilter(
        queryset=Carrera.objects.all(),
        empty_label="Todas las carreras",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    asignatura = django_filters.ModelChoiceFilter(
        queryset=Asignatura.objects.all(),
        empty_label="Todas las asignaturas",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    categoria = django_filters.ChoiceFilter(
        choices=[
            ('', 'Todas las categorías'),
            ('reactivos', 'Reactivos'),
            ('materiales', 'Materiales'),
            ('herramientas', 'Herramientas'),
            ('consumibles', 'Consumibles'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    estado = django_filters.ChoiceFilter(
        choices=[
            ('', 'Todos los estados'),
            ('disponible', 'Disponible'),
            ('agotado', 'Agotado'),
            ('vencido', 'Vencido'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def filter_search(self, queryset, name, value):
        """Búsqueda general en múltiples campos"""
        if value:
            from django.db.models import Q
            return queryset.filter(
                Q(nombre_elemento__icontains=value) |
                Q(descripcion_caracteristicas__icontains=value) |
                Q(unidad_academica__nombre__icontains=value) |
                Q(carrera__nombre__icontains=value) |
                Q(categoria__icontains=value)
            )
        return queryset

    class Meta:
        model = Insumo
        fields = ['search', 'nombre_elemento', 'unidad_academica', 'carrera', 'asignatura', 'categoria', 'estado']


class GuiaFilter(django_filters.FilterSet):
    """Filtros para el modelo GuiaGenerada"""
    
    search = django_filters.CharFilter(
        method='filter_search',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar guías...'
        })
    )
    
    titulo = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por título de guía...'
        })
    )
    
    carrera = django_filters.ModelChoiceFilter(
        queryset=Carrera.objects.all(),
        empty_label="Todas las carreras",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    asignatura = django_filters.ModelChoiceFilter(
        queryset=Asignatura.objects.all(),
        empty_label="Todas las asignaturas",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    semestre = django_filters.ChoiceFilter(
        choices=[
            ('', 'Todos los semestres'),
            (1, '1° Semestre'),
            (2, '2° Semestre'),
            (3, '3° Semestre'),
            (4, '4° Semestre'),
            (5, '5° Semestre'),
            (6, '6° Semestre'),
            (7, '7° Semestre'),
            (8, '8° Semestre'),
            (9, '9° Semestre'),
            (10, '10° Semestre'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    tipo_practica = django_filters.ChoiceFilter(
        choices=[
            ('', 'Todos los tipos'),
            ('laboratorio', 'Laboratorio'),
            ('campo', 'Campo'),
            ('taller', 'Taller'),
            ('gabinete', 'Gabinete'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def filter_search(self, queryset, name, value):
        """Búsqueda general en múltiples campos"""
        if value:
            from django.db.models import Q
            return queryset.filter(
                Q(titulo__icontains=value) |
                Q(contenido_analitico__icontains=value) |
                Q(carrera__nombre__icontains=value) |
                Q(asignatura__nombre__icontains=value)
            )
        return queryset

    class Meta:
        model = GuiaGenerada
        fields = ['search', 'titulo', 'carrera', 'asignatura', 'semestre', 'tipo_practica']