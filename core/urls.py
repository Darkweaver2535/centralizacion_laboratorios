from django.urls import path
from . import views
from .import_views import seleccionar_metodo_carga, importar_excel_view, descargar_plantilla_excel

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('ajax/carreras-por-unidad/', views.get_carreras_por_unidad_ajax, name='carreras_por_unidad'),
    path('ajax/asignaturas-por-carrera/', views.get_asignaturas_por_carrera_ajax, name='asignaturas_por_carrera'),
    path('ajax/unidades-tematicas/', views.get_unidades_tematicas_ajax, name='unidades_tematicas'),
    path('ajax/guias-laboratorio/', views.get_guias_laboratorio_ajax, name='guias_laboratorio'),
    path('ajax/practicas/', views.get_practicas_ajax, name='practicas'),
    path('ajax/laboratorios/', views.get_laboratorios_ajax, name='laboratorios'),
    
    # Malla Curricular
    path('malla-curricular/', views.malla_curricular_view, name='malla_curricular'),
    path('malla-curricular/asignatura/<int:asignatura_id>/', views.detalle_asignatura_view, name='detalle_asignatura'),
    path('ajax/criterios-desempeno/', views.get_criterios_desempeno_ajax, name='criterios_desempeno'),
    path('ajax/unidades-didacticas/', views.get_unidades_didacticas_ajax, name='unidades_didacticas'),
    path('ajax/contenidos-analiticos/', views.get_contenidos_analiticos_ajax, name='contenidos_analiticos'),
    
    # Sistema de importación R1
    path('seleccionar-metodo/<str:tipo>/', seleccionar_metodo_carga, name='seleccionar_metodo'),
    path('importar-excel/<str:tipo>/', importar_excel_view, name='importar_excel'),
    path('plantilla-excel/<str:tipo>/', descargar_plantilla_excel, name='plantilla_excel'),
]