import django_filters
from django import forms
from .models import Asignatura, Carrera, UnidadAcademica, CriterioDesempeno, UnidadDidactica, ContenidoAnalitico


class AsignaturaFilter(django_filters.FilterSet):
    """Filtros para el modelo Asignatura en malla curricular"""
    
    search = django_filters.CharFilter(
        method='filter_search',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar asignaturas...'
        })
    )
    
    nombre = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre de asignatura...'
        })
    )
    
    unidad_academica = django_filters.ModelChoiceFilter(
        queryset=UnidadAcademica.objects.all(),
        empty_label="Todas las unidades académicas",
        widget=forms.Select(attrs={'class': 'form-control'}),
        method='filter_unidad_academica'
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
    
    codigo_competencia = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por código de competencia...'
        })
    )
    
    sigla_curricular = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por sigla curricular...'
        })
    )

    def filter_search(self, queryset, name, value):
        """Búsqueda general en múltiples campos"""
        if value:
            from django.db.models import Q
            return queryset.filter(
                Q(nombre__icontains=value) |
                Q(codigo_competencia__icontains=value) |
                Q(sigla_curricular__icontains=value) |
                Q(carrera__nombre__icontains=value) |
                Q(carrera__unidad_academica__nombre__icontains=value)
            )
        return queryset

    def filter_unidad_academica(self, queryset, name, value):
        """Filtrar por unidad académica a través de carrera"""
        if value:
            return queryset.filter(carrera__unidad_academica=value)
        return queryset

    class Meta:
        model = Asignatura
        fields = ['search', 'nombre', 'unidad_academica', 'carrera', 'semestre', 'codigo_competencia', 'sigla_curricular']


class CriterioDesempenoFilter(django_filters.FilterSet):
    """Filtros para criterios de desempeño"""
    
    search = django_filters.CharFilter(
        method='filter_search',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar criterios...'
        })
    )
    
    asignatura = django_filters.ModelChoiceFilter(
        queryset=Asignatura.objects.all(),
        empty_label="Todas las asignaturas",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def filter_search(self, queryset, name, value):
        if value:
            from django.db.models import Q
            return queryset.filter(
                Q(nombre__icontains=value) |
                Q(descripcion__icontains=value) |
                Q(asignatura__nombre__icontains=value)
            )
        return queryset

    class Meta:
        model = CriterioDesempeno
        fields = ['search', 'asignatura']


class UnidadDidacticaFilter(django_filters.FilterSet):
    """Filtros para unidades didácticas"""
    
    search = django_filters.CharFilter(
        method='filter_search',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar unidades didácticas...'
        })
    )
    
    asignatura = django_filters.ModelChoiceFilter(
        queryset=Asignatura.objects.all(),
        empty_label="Todas las asignaturas",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def filter_search(self, queryset, name, value):
        if value:
            from django.db.models import Q
            return queryset.filter(
                Q(nombre__icontains=value) |
                Q(descripcion__icontains=value) |
                Q(asignatura__nombre__icontains=value)
            )
        return queryset

    class Meta:
        model = UnidadDidactica
        fields = ['search', 'asignatura']


class ContenidoAnaliticoFilter(django_filters.FilterSet):
    """Filtros para contenidos analíticos"""
    
    search = django_filters.CharFilter(
        method='filter_search',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar contenidos analíticos...'
        })
    )
    
    unidad_didactica = django_filters.ModelChoiceFilter(
        queryset=UnidadDidactica.objects.all(),
        empty_label="Todas las unidades didácticas",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def filter_search(self, queryset, name, value):
        if value:
            from django.db.models import Q
            return queryset.filter(
                Q(nombre__icontains=value) |
                Q(descripcion__icontains=value) |
                Q(unidad_didactica__nombre__icontains=value) |
                Q(unidad_didactica__asignatura__nombre__icontains=value)
            )
        return queryset

    class Meta:
        model = ContenidoAnalitico
        fields = ['search', 'unidad_didactica']