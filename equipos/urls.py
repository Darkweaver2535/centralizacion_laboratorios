from django.urls import path
from . import views

app_name = 'equipos'

urlpatterns = [
    path('', views.equipos_view, name='lista'),
    path('nuevo/', views.nuevo_equipo_view, name='nuevo'),
    path('<int:pk>/', views.detalle_equipo_view, name='detalle'),
    path('<int:pk>/editar/', views.editar_equipo_view, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_equipo_view, name='eliminar'),
    path('exportar/', views.exportar_equipos_excel, name='exportar'),
    path('filtrar/', views.filtrar_equipos_ajax, name='filtrar'),
    path('ajax/carreras/', views.get_carreras_ajax, name='carreras_ajax'),
    path('ajax/asignaturas/', views.get_asignaturas_ajax, name='asignaturas_ajax'),
    path('ajax/unidades-tematicas/', views.get_unidades_tematicas_ajax, name='unidades_tematicas_ajax'),
    path('ajax/guias-laboratorio/', views.get_guias_laboratorio_ajax, name='guias_laboratorio_ajax'),
    path('ajax/practicas/', views.get_practicas_ajax, name='practicas_ajax'),
    path('ajax/laboratorios/', views.get_laboratorios_ajax, name='laboratorios_ajax'),
]
