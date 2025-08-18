from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('ajax/carreras-por-unidad/', views.get_carreras_por_unidad_ajax, name='carreras_por_unidad'),
    path('ajax/asignaturas-por-carrera/', views.get_asignaturas_por_carrera_ajax, name='asignaturas_por_carrera'),
    path('ajax/unidades-tematicas/', views.get_unidades_tematicas_ajax, name='unidades_tematicas'),
    path('ajax/guias-laboratorio/', views.get_guias_laboratorio_ajax, name='guias_laboratorio'),
    path('ajax/practicas/', views.get_practicas_ajax, name='practicas'),
    path('ajax/laboratorios/', views.get_laboratorios_ajax, name='laboratorios'),
]