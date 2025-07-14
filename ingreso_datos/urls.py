from django.urls import path
from . import views

urlpatterns = [
    path('', views.ingreso_datos_view, name='ingreso_datos'),
]