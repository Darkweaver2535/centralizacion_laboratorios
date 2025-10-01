from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django_filters.views import FilterView
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from equipos.models import Equipo
from insumos.models import Insumo
from guias.models import GuiaGenerada
from .filters import EquipoFilter, InsumoFilter, GuiaFilter


@method_decorator(login_required, name='dispatch')
class EquipoFilterView(FilterView):
    """Vista filtrada para equipos usando django-filter"""
    model = Equipo
    filterset_class = EquipoFilter
    template_name = 'visualizacion_filter/equipos_list.html'
    context_object_name = 'equipos'
    paginate_by = 20
    
    def get_queryset(self):
        return Equipo.objects.select_related(
            'unidad_academica', 'carrera', 'asignatura'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria'] = 'equipos'
        context['total_count'] = self.get_queryset().count()
        context['filtered_count'] = context['object_list'].count() if hasattr(context['object_list'], 'count') else len(context['object_list'])
        return context


@method_decorator(login_required, name='dispatch')
class InsumoFilterView(FilterView):
    """Vista filtrada para insumos usando django-filter"""
    model = Insumo
    filterset_class = InsumoFilter
    template_name = 'visualizacion_filter/insumos_list.html'
    context_object_name = 'insumos'
    paginate_by = 20
    
    def get_queryset(self):
        return Insumo.objects.select_related(
            'unidad_academica', 'carrera', 'asignatura'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria'] = 'insumos'
        context['total_count'] = self.get_queryset().count()
        context['filtered_count'] = context['object_list'].count() if hasattr(context['object_list'], 'count') else len(context['object_list'])
        return context


@method_decorator(login_required, name='dispatch')
class GuiaFilterView(FilterView):
    """Vista filtrada para guías usando django-filter"""
    model = GuiaGenerada
    filterset_class = GuiaFilter
    template_name = 'visualizacion_filter/guias_list.html'
    context_object_name = 'guias'
    paginate_by = 20
    
    def get_queryset(self):
        return GuiaGenerada.objects.select_related(
            'carrera', 'asignatura'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria'] = 'guias'
        context['total_count'] = self.get_queryset().count()
        context['filtered_count'] = context['object_list'].count() if hasattr(context['object_list'], 'count') else len(context['object_list'])
        return context


@login_required
def visualizacion_filter_index(request):
    """Vista principal del sistema de filtros mejorado"""
    context = {
        'equipos_count': Equipo.objects.count(),
        'insumos_count': Insumo.objects.count(),
        'guias_count': GuiaGenerada.objects.count(),
    }
    return render(request, 'visualizacion_filter/index.html', context)