from django.urls import path
from . import views

app_name = 'guias'

urlpatterns = [
    path('', views.lista_guias, name='lista'),
    path('nueva/', views.nueva_guia, name='nueva'),
    path('<int:guia_id>/', views.detalle_guia, name='detalle'),
    path('eliminar/<int:guia_id>/', views.eliminar_guia, name='eliminar'),
    path('descargar/<int:guia_id>/word/', views.descargar_word, name='descargar_word'),
    path('descargar/<int:guia_id>/pdf/', views.descargar_pdf, name='descargar_pdf'),
    
    # API para dropdowns dinámicos
    path('api/asignaturas/', views.api_asignaturas, name='api_asignaturas'),
]
