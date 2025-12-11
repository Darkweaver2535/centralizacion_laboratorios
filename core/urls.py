from django.urls import path
from . import views
from .import_views import seleccionar_metodo_carga, importar_excel_view, descargar_plantilla_excel

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('ajax/carreras-por-unidad/', views.get_carreras_por_unidad_ajax, name='carreras_por_unidad'),
    path('ajax/asignaturas-por-carrera/', views.get_asignaturas_por_carrera_ajax, name='asignaturas_por_carrera'),
    path('ajax/unidades-tematicas/', views.get_unidades_tematicas_ajax, name='unidades_tematicas'),
    path('ajax/guias-laboratorio/', views.get_guias_laboratorio_ajax, name='guias_laboratorio'),
    path('ajax/practicas/', views.get_practicas_ajax, name='practicas'),
    path('ajax/laboratorios/', views.get_laboratorios_ajax, name='laboratorios'),
    
    # Malla Curricular
    path('malla-curricular/', views.malla_curricular_view, name='malla_curricular'),
    path('malla-curricular/asignatura/<int:asignatura_id>/', views.detalle_asignatura_view, name='detalle_asignatura'),
    path('malla-curricular/agregar-datos/', views.agregar_datos_malla_view, name='agregar_datos_malla'),
    path('malla-curricular/combinacion/<int:combinacion_id>/', views.detalle_combinacion_view, name='detalle_combinacion'),
    path('malla-curricular/contenido/<int:contenido_id>/componentes/', views.agregar_componentes_contenido_view, name='agregar_componentes_contenido'),
    path('ajax/criterios-desempeno/', views.get_criterios_desempeno_ajax, name='criterios_desempeno'),
    path('ajax/unidades-didacticas/', views.get_unidades_didacticas_ajax, name='unidades_didacticas'),
    path('ajax/contenidos-analiticos/', views.get_contenidos_analiticos_ajax, name='contenidos_analiticos'),
    
    # Prueba CKEditor 5
    path('prueba-ckeditor/', views.prueba_ckeditor_view, name='prueba_ckeditor'),
    
    # Equipos e Insumos AJAX
    path('ajax/equipos-por-unidad/', views.get_equipos_por_unidad_ajax, name='equipos_por_unidad'),
    path('ajax/insumos-por-unidad/', views.get_insumos_por_unidad_ajax, name='insumos_por_unidad'),
    path('ajax/agregar-equipo-rapido/', views.agregar_equipo_rapido_ajax, name='agregar_equipo_rapido'),
    path('ajax/agregar-insumo-rapido/', views.agregar_insumo_rapido_ajax, name='agregar_insumo_rapido'),
    
    # AJAX para filtros en cascada de malla curricular
    path('ajax/carreras-por-unidad-filtro/', views.carreras_por_unidad_ajax, name='carreras_por_unidad_filtro'),
    path('ajax/semestres-por-carrera-filtro/', views.semestres_por_carrera_ajax, name='semestres_por_carrera_filtro'),
    path('ajax/asignaturas-por-filtros/', views.asignaturas_por_filtros_ajax, name='asignaturas_por_filtros'),
    path('ajax/criterios-por-asignatura/', views.criterios_por_asignatura_ajax, name='criterios_por_asignatura'),
    path('ajax/unidades-didacticas-por-asignatura/', views.unidades_didacticas_por_asignatura_ajax, name='unidades_didacticas_por_asignatura'),
    path('ajax/contenidos-por-asignatura/', views.contenidos_por_asignatura_ajax, name='contenidos_por_asignatura'),
    
    # Sistema de importación R1
    path('seleccionar-metodo/<str:tipo>/', seleccionar_metodo_carga, name='seleccionar_metodo'),
    path('importar-excel/<str:tipo>/', importar_excel_view, name='importar_excel'),
    path('plantilla-excel/<str:tipo>/', descargar_plantilla_excel, name='plantilla_excel'),
]