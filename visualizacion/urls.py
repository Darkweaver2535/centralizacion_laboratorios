from django.urls import path
from . import views

urlpatterns = [
    path('', views.visualizacion_view, name='visualizacion'),
    path('filtrar/', views.filtrar_datos, name='filtrar_datos'),
    path('opciones-filtro/', views.obtener_opciones_filtro, name='opciones_filtro'),
    path('equipos/', views.equipos_ajax, name='equipos_ajax'),
    path('exportar-excel/', views.exportar_excel, name='exportar_excel'),
]