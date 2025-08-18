from django.urls import path
from . import views

app_name = 'insumos'

urlpatterns = [
    path('', views.insumos_view, name='lista'),
    path('nuevo/', views.nuevo_insumo_view, name='nuevo'),
    path('<int:pk>/', views.detalle_insumo_view, name='detalle'),
    path('<int:pk>/solicitar/', views.solicitar_insumo_view, name='solicitar'),
    path('exportar/', views.exportar_insumos_excel, name='exportar'),
    # Mantener rutas antiguas para compatibilidad
    path('ingreso/', views.nuevo_insumo_view, name='ingreso_insumos'),
    path('visualizacion/', views.insumos_view, name='visualizacion_insumos'),
]