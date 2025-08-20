from django.urls import path
from . import views

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
]