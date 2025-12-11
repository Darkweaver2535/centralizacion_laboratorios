from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Vistas principales
    path('', views.lista_usuarios, name='lista'),
    path('crear/', views.crear_usuario, name='crear'),
    path('crear-simple/', views.crear_usuario_simple, name='crear_simple'),
    path('<int:pk>/', views.detalle_usuario, name='detalle'),
    path('<int:pk>/editar/', views.editar_usuario, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar_usuario, name='eliminar'),
    
    # Vistas de perfil personal
    path('mi-perfil/', views.mi_perfil, name='perfil'),
    path('configuracion/', views.configuracion_usuario, name='configuracion'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
    
    # Acciones administrativas
    path('<int:pk>/cambiar-estado/', views.cambiar_estado, name='cambiar_estado'),
    
    # APIs para formularios dinámicos
    path('api/laboratorios-por-sede/<str:sede>/', views.api_laboratorios_por_sede, name='api_laboratorios_sede'),
    path('api/jefes-por-sede/<str:sede>/', views.api_jefes_por_sede, name='api_jefes_sede'),
]
