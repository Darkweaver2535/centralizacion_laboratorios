import django_filters
from django import forms
from .models import Asignatura, Carrera, UnidadAcademica, CriterioDesempeno, UnidadDidactica, ContenidoAnalitico


class AsignaturaFilter(django_filters.FilterSet):
    """Filtros mejorados para el modelo Asignatura con filtros en cascada"""
    
    unidad_academica = django_filters.ModelChoiceFilter(
        queryset=UnidadAcademica.objects.all(),
        empty_label="Seleccione una Unidad Académica",
        widget=forms.Select(attrs={
            'class': 'form-control', 
            'id': 'id_unidad_academica',
            'onchange': 'actualizarCarrerasPorUnidad()'
        }),
        method='filter_unidad_academica'
    )
    
    carrera = django_filters.ModelChoiceFilter(
        queryset=Carrera.objects.none(),  # Se carga dinámicamente
        empty_label="Seleccione una Carrera",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_carrera',
            'onchange': 'actualizarSemestresPorCarrera()'
        })
    )
    
    semestre = django_filters.ChoiceFilter(
        choices=[('', 'Seleccione un Semestre')],  # Se carga dinámicamente
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_semestre',
            'onchange': 'actualizarAsignaturasPorFiltros()'
        })
    )
    
    nombre = django_filters.ChoiceFilter(
        choices=[('', 'Seleccione una Asignatura')],  # Se carga dinámicamente
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_nombre'
        }),
        field_name='id'  # Filtrar por ID de la asignatura
    )
    
    search = django_filters.CharFilter(
        method='filter_search',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, código, sigla, carrera...',
            'id': 'id_search'
        })
    )

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)
        
        # Configurar queryset inicial para asignaturas basado en el queryset padre
        initial_queryset = kwargs.get('queryset', Asignatura.objects.all())
        
        # Si hay datos, configurar los querysets según los valores seleccionados
        if data:
            unidad_id = data.get('unidad_academica')
            carrera_id = data.get('carrera') 
            semestre = data.get('semestre')
            asignatura_id = data.get('nombre')
            
            if unidad_id:
                self.filters['carrera'].queryset = Carrera.objects.filter(unidad_academica_id=unidad_id)
                
                if carrera_id:
                    # Actualizar opciones de semestre
                    semestres_disponibles = initial_queryset.filter(
                        carrera_id=carrera_id
                    ).values_list('semestre', flat=True).distinct().order_by('semestre')
                    
                    choices = [('', 'Seleccione un Semestre')]
                    for sem in semestres_disponibles:
                        choices.append((sem, f'{sem}° Semestre'))
                    self.filters['semestre'].extra['choices'] = choices
                    
                    if semestre:
                        # Actualizar asignaturas por carrera y semestre usando el queryset inicial
                        asignaturas_filtradas = initial_queryset.filter(
                            carrera_id=carrera_id,
                            semestre=semestre
                        ).order_by('nombre')
                        
                        # Actualizar las opciones del selector de asignaturas
                        choices = [('', 'Seleccione una Asignatura')]
                        for asig in asignaturas_filtradas:
                            choices.append((asig.id, asig.nombre))
                        self.filters['nombre'].extra['choices'] = choices
                    else:
                        # Si no hay semestre, limpiar opciones de asignaturas
                        self.filters['nombre'].extra['choices'] = [('', 'Seleccione una Asignatura')]
                else:
                    # Si no hay carrera, limpiar opciones dependientes  
                    self.filters['nombre'].extra['choices'] = [('', 'Seleccione una Asignatura')]
            else:
                # Si no hay unidad, limpiar todos los querysets dependientes
                self.filters['carrera'].queryset = Carrera.objects.none()
                self.filters['nombre'].extra['choices'] = [('', 'Seleccione una Asignatura')]

    def filter_unidad_academica(self, queryset, name, value):
        """Filtrar por unidad académica a través de carrera"""
        if value:
            return queryset.filter(carrera__unidad_academica=value)
        return queryset

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

    class Meta:
        model = Asignatura
        fields = ['unidad_academica', 'carrera', 'semestre', 'nombre', 'search']


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