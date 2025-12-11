from django.urls import path
from . import views

app_name = 'visualizacion'

urlpatterns = [
    path('', views.visualizacion_view, name='analisis'),
    path('filtrar/', views.filtrar_datos, name='filtrar_datos'),
    path('opciones-filtro/', views.obtener_opciones_filtro, name='opciones_filtro'),
    path('equipos/', views.equipos_ajax, name='equipos_ajax'),
    path('exportar-excel/', views.exportar_excel, name='exportar_excel'),
    
        # AJAX endpoints para filtros dinámicos
    path('ajax/carreras-por-unidad/', views.ajax_carreras_por_unidad, name='ajax_carreras_por_unidad'),
    path('ajax/semestres-por-carrera/', views.ajax_semestres_por_carrera, name='ajax_semestres_por_carrera'),
    path('ajax/asignaturas-por-carrera/', views.ajax_asignaturas_por_carrera, name='ajax_asignaturas_por_carrera'),
    path('ajax/unidades-didacticas-por-asignatura/', views.ajax_unidades_didacticas_por_asignatura, name='ajax_unidades_didacticas_por_asignatura'),
    path('ajax/contenidos-por-unidad-didactica/', views.ajax_contenidos_por_unidad_didactica, name='ajax_contenidos_por_unidad_didactica'),
    path('ajax/estadisticas-filtradas/', views.ajax_estadisticas_filtradas, name='ajax_estadisticas_filtradas'),
    
    # AJAX endpoints para sistema de correlaciones
    path('ajax/correlaciones-equipo/', views.ajax_correlaciones_equipo, name='ajax_correlaciones_equipo'),
    path('ajax/correlaciones-guia/', views.ajax_correlaciones_guia, name='ajax_correlaciones_guia'),
    path('ajax/correlaciones-insumo/', views.ajax_correlaciones_insumo, name='ajax_correlaciones_insumo'),
    path('ajax/resumen-correlaciones/', views.ajax_resumen_correlaciones, name='ajax_resumen_correlaciones'),
    
    # Nuevas funciones de exportación para docentes
    path('exportar-excel-avanzado/', views.exportar_excel_avanzado, name='exportar_excel_avanzado'),
    path('exportar-pdf-guia/', views.exportar_pdf_guia, name='exportar_pdf_guia'),
    path('exportar-guias-pdf/', views.exportar_guias_filtradas_pdf, name='exportar_guias_pdf'),
    
    # Nuevos endpoints API para vista dinámica
    path('api/filtros/<str:filtro>/', views.api_filtros, name='api_filtros'),
    path('api/buscar/', views.api_buscar, name='api_buscar'),
    path('api/categoria/<str:categoria>/', views.api_categoria, name='api_categoria'),
    path('api/buscar-titulos-guias/', views.api_buscar_titulos_guias, name='api_buscar_titulos_guias'),
    
    # Vista temporal de debug
    path('debug/', views.debug_api_view, name='debug_api'),
]