from django.urls import path
from . import views

app_name = 'visualizacion'

urlpatterns = [
    path('', views.visualizacion_view, name='analisis'),
    path('filtrar/', views.filtrar_datos, name='filtrar_datos'),
    path('opciones-filtro/', views.obtener_opciones_filtro, name='opciones_filtro'),
    path('equipos/', views.equipos_ajax, name='equipos_ajax'),
    path('exportar-excel/', views.exportar_excel, name='exportar_excel'),
]