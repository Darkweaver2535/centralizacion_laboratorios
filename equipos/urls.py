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
    
    # URLs para el sistema de reordenamiento
    path('reordenamiento/', views.lista_tareas_reordenamiento, name='reordenamiento'),
    path('reordenamiento/nueva-tarea/', views.nueva_tarea_reordenamiento, name='nueva_tarea'),
    path('reordenamiento/tarea/<int:pk>/', views.detalle_tarea_reordenamiento, name='detalle_tarea'),
    path('reordenamiento/tarea/<int:pk>/editar/', views.editar_tarea_reordenamiento, name='editar_tarea'),
    path('reordenamiento/tarea/<int:pk>/eliminar/', views.eliminar_tarea_reordenamiento, name='eliminar_tarea'),
    path('reordenamiento/tarea/<int:pk>/procesar/', views.procesar_tarea_reordenamiento, name='procesar_tarea'),
    path('reordenamiento/buscar-equipos/', views.buscar_equipos_reordenamiento, name='buscar_equipos'),
    path('reordenamiento/ajax/laboratorios-unidad/', views.get_laboratorios_unidad_ajax, name='laboratorios_unidad_ajax'),
    
    # APIs para selección de equipos en reordenamiento
    path('api/equipos-disponibles/', views.api_equipos_disponibles, name='api_equipos_disponibles'),
    path('api/laboratorios-por-unidad/<int:unidad_id>/', views.api_laboratorios_por_unidad, name='api_laboratorios_por_unidad'),
]
