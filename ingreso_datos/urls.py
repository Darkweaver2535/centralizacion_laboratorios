from django.urls import path
from . import views

urlpatterns = [
    path('', views.ingreso_datos_view, name='ingreso_datos'),
    path('carreras/', views.get_carreras_por_unidad, name='get_carreras_por_unidad'),
]