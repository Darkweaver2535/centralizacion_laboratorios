from django.urls import path
from . import views
from . import views_reordenamiento

app_name = 'insumos'

urlpatterns = [
    path('', views.lista_insumos, name='lista'),
    path('nuevo/', views.nuevo_insumo, name='nuevo'),
    path('<int:insumo_id>/', views.detalle_insumo, name='detalle'),
    path('<int:insumo_id>/editar/', views.editar_insumo, name='editar'),
    path('eliminar/<int:insumo_id>/', views.eliminar_insumo, name='eliminar'),
    path('exportar-excel/', views.exportar_excel, name='exportar_excel'),
    
    # APIs para dropdowns dinámicos
    path('api/carreras/', views.api_carreras, name='api_carreras'),
    path('api/asignaturas/', views.api_asignaturas, name='api_asignaturas'),
    path('api/unidades-tematicas/', views.api_unidades_tematicas, name='api_unidades_tematicas'),
    
    # URLs de reordenamiento de insumos
    path('reordenamiento/', views_reordenamiento.lista_tareas_reordenamiento_insumos, name='reordenamiento_insumos'),
    path('reordenamiento/nueva/', views_reordenamiento.nueva_tarea_reordenamiento_insumos, name='nueva_tarea_reordenamiento'),
    path('reordenamiento/<int:pk>/', views_reordenamiento.detalle_tarea_reordenamiento_insumos, name='detalle_tarea_reordenamiento'),
    path('reordenamiento/<int:pk>/editar/', views_reordenamiento.editar_tarea_reordenamiento_insumos, name='editar_tarea_reordenamiento'),
    path('reordenamiento/<int:pk>/eliminar/', views_reordenamiento.eliminar_tarea_reordenamiento_insumos, name='eliminar_tarea_reordenamiento'),
    path('reordenamiento/<int:pk>/procesar/', views_reordenamiento.procesar_tarea_reordenamiento_insumos, name='procesar_tarea_reordenamiento'),
    path('reordenamiento/<int:pk>/agregar-insumos/', views_reordenamiento.agregar_insumos_tarea, name='agregar_insumos_tarea'),
    path('api/buscar-insumos-reordenamiento/', views_reordenamiento.buscar_insumos_reordenamiento, name='buscar_insumos_reordenamiento'),
]