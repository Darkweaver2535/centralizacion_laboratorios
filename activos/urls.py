from django.urls import path
from . import views

app_name = 'activos'

urlpatterns = [
    # Vistas principales
    path('seleccionar-metodo/', views.seleccionar_metodo_activos, name='seleccionar_metodo'),
    path('lista/', views.lista_activos, name='lista_activos'),
    path('agregar/', views.agregar_activo, name='agregar_activo'),
    path('detalle/<int:activo_id>/', views.detalle_activo, name='detalle_activo'),
    path('editar/<int:activo_id>/', views.editar_activo, name='editar_activo'),
    path('eliminar/<int:activo_id>/', views.eliminar_activo, name='eliminar_activo'),
    
    # APIs AJAX
    path('ajax/laboratorios-por-unidad/', views.ajax_laboratorios_por_unidad, name='ajax_laboratorios_por_unidad'),
    path('ajax/carreras-por-unidad/', views.ajax_carreras_por_unidad, name='ajax_carreras_por_unidad'),
    
    # Reportes
    path('exportar/excel/', views.exportar_activos_excel, name='exportar_excel'),
]