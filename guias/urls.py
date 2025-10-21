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
    
    # Nuevas URLs para generación de PDF completo
    path('<int:guia_id>/generar-pdf/', views.generar_guia_pdf_completa, name='generar_pdf_completa'),
    path('<int:guia_id>/detalle/', views.detalle_guia_completa, name='detalle_completa'),
    
    # URLs para prácticas de laboratorio (nuevas guías basadas en prácticas reales)
    path('practica/<int:practica_id>/generar-pdf/', views.generar_practica_pdf, name='generar_practica_pdf'),
    path('practica/<int:practica_id>/detalle/', views.detalle_practica_completa, name='detalle_practica_completa'),
    
    # API para dropdowns dinámicos
    path('api/asignaturas/', views.api_asignaturas, name='api_asignaturas'),
]
