"""
URL configuration for centralizacion project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

# Imports para las APIs
from core.models import UnidadAcademica, Carrera, Asignatura, UnidadTematica, GuiaLaboratorio, Practica

@login_required
def api_carreras(request):
    """Vista API para carreras por unidad académica"""
    unidad_academica = request.GET.get('unidad_academica')
    
    if not unidad_academica:
        return JsonResponse({'error': 'Unidad académica requerida'}, status=400)
    
    try:
        from core.models import UnidadAcademica, Carrera
        
        # Mapear los valores del formulario a los nombres en la base de datos
        mapeo_unidades = {
            'la_paz': 'UALP',
            'santa_cruz': 'UASC', 
            'cochabamba': 'UACB',
            'riberalta': 'UCRB',
            'tropico': 'UATP'
        }
        
        # Obtener la unidad académica por ID o por nombre mapeado
        unidad = None
        
        # Si es un número, buscar por ID
        if unidad_academica.isdigit():
            try:
                unidad = UnidadAcademica.objects.get(id=int(unidad_academica))
            except UnidadAcademica.DoesNotExist:
                return JsonResponse({'error': 'Unidad académica no encontrada'}, status=404)
        else:
            # Si es texto, mapear a nombre oficial
            nombre_unidad = mapeo_unidades.get(unidad_academica)
            if not nombre_unidad:
                return JsonResponse({'error': 'Unidad académica no válida'}, status=400)
                
            try:
                unidad = UnidadAcademica.objects.get(nombre=nombre_unidad)
            except UnidadAcademica.DoesNotExist:
                return JsonResponse({'error': f'Unidad académica {nombre_unidad} no encontrada'}, status=404)
        
        # Obtener carreras de esa unidad
        carreras = Carrera.objects.filter(unidad_academica=unidad).order_by('nombre')
        
        # Preparar los datos para el frontend
        carreras_data = []
        for carrera in carreras:
            carreras_data.append({
                'id': carrera.id,
                'nombre': carrera.get_nombre_display()
            })
        
        return JsonResponse(carreras_data, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)

@login_required
def api_asignaturas(request):
    """Vista API para asignaturas por carrera y semestre"""
    carrera_id = request.GET.get('carrera')
    semestre = request.GET.get('semestre')
    
    if not carrera_id:
        return JsonResponse({'error': 'Carrera requerida'}, status=400)
    
    try:
        from core.models import Carrera, Asignatura
        
        # Obtener la carrera por ID
        try:
            carrera = Carrera.objects.get(id=carrera_id)
        except Carrera.DoesNotExist:
            return JsonResponse({'error': 'Carrera no encontrada'}, status=404)
        
        # Filtrar asignaturas por carrera
        asignaturas = Asignatura.objects.filter(carrera=carrera).order_by('nombre')
        
        # Si se especifica semestre, filtrar también por semestre
        if semestre:
            try:
                semestre_int = int(semestre)
                asignaturas = asignaturas.filter(semestre=semestre_int)
            except ValueError:
                pass
        
        # Preparar los datos para el frontend
        asignaturas_data = []
        for asignatura in asignaturas:
            asignaturas_data.append({
                'id': asignatura.id,
                'nombre': asignatura.nombre,
                'semestre': asignatura.semestre if hasattr(asignatura, 'semestre') else None
            })
        
        return JsonResponse(asignaturas_data, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)

@login_required
def api_unidades_tematicas(request):
    """Vista API para unidades temáticas por asignatura"""
    asignatura_id = request.GET.get('asignatura')
    
    if not asignatura_id:
        return JsonResponse({'error': 'Asignatura requerida'}, status=400)
    
    try:
        from core.models import Asignatura, UnidadTematica
        
        # Obtener la asignatura por ID
        try:
            asignatura = Asignatura.objects.get(id=asignatura_id)
        except Asignatura.DoesNotExist:
            return JsonResponse({'error': 'Asignatura no encontrada'}, status=404)
        
        # Obtener unidades temáticas de esa asignatura
        unidades = UnidadTematica.objects.filter(asignatura=asignatura).order_by('numero')
        
        # Preparar los datos para el frontend
        unidades_data = []
        for unidad in unidades:
            unidades_data.append({
                'id': unidad.id,
                'nombre': unidad.nombre,
                'numero': unidad.numero
            })
        
        return JsonResponse(unidades_data, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)

@login_required 
def api_proveedores(request):
    """Vista API para proveedores"""
    if request.method == 'GET':
        try:
            # Verificar si existe el modelo Proveedor
            try:
                from insumos.models import Proveedor
                proveedores = Proveedor.objects.all().order_by('nombre')
                
                proveedores_data = []
                for proveedor in proveedores:
                    proveedores_data.append({
                        'id': proveedor.id,
                        'nombre': proveedor.nombre,
                        'contacto': getattr(proveedor, 'contacto', ''),
                        'telefono': getattr(proveedor, 'telefono', ''),
                        'email': getattr(proveedor, 'email', '')
                    })
                
                return JsonResponse(proveedores_data, safe=False)
                
            except (ImportError, AttributeError):
                # Si no existe el modelo, devolver lista vacía pero sin error
                return JsonResponse([], safe=False)
            
        except Exception as e:
            return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)
    
    elif request.method == 'POST':
        # Crear nuevo proveedor
        try:
            from insumos.models import Proveedor
            data = json.loads(request.body)
            
            proveedor = Proveedor.objects.create(
                nombre=data.get('nombre', ''),
                contacto=data.get('contacto', ''),
                telefono=data.get('telefono', ''),
                email=data.get('email', '')
            )
            
            return JsonResponse({
                'id': proveedor.id,
                'nombre': proveedor.nombre,
                'success': True
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
@csrf_exempt
def api_insumos_detalle(request, insumo_id):
    """Vista API para detalles de insumos específicos"""
    try:
        from insumos.models import Insumo
        
        try:
            insumo = Insumo.objects.get(id=insumo_id)
        except Insumo.DoesNotExist:
            return JsonResponse({'error': 'Insumo no encontrado'}, status=404)
        
        if request.method == 'GET':
            insumo_data = {
                'id': insumo.id,
                'nombre': insumo.nombre,
                'descripcion': getattr(insumo, 'descripcion', ''),
                'stock_actual': getattr(insumo, 'stock_actual', 0),
                'stock_minimo': getattr(insumo, 'stock_minimo', 0),
                'precio_unitario': float(getattr(insumo, 'precio_unitario', 0)),
                'unidad_medida': getattr(insumo, 'unidad_medida', ''),
                'proveedor': {
                    'id': insumo.proveedor.id if hasattr(insumo, 'proveedor') and insumo.proveedor else None,
                    'nombre': insumo.proveedor.nombre if hasattr(insumo, 'proveedor') and insumo.proveedor else None
                }
            }
            
            return JsonResponse(insumo_data)
            
        elif request.method == 'PUT':
            # Actualizar insumo
            data = json.loads(request.body)
            
            for key, value in data.items():
                if hasattr(insumo, key):
                    setattr(insumo, key, value)
            
            insumo.save()
            
            return JsonResponse({'success': True, 'message': 'Insumo actualizado correctamente'})
        
        elif request.method == 'DELETE':
            insumo.delete()
            return JsonResponse({'success': True, 'message': 'Insumo eliminado correctamente'})
            
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
@csrf_exempt
def api_insumos_ajustar_stock(request, insumo_id):
    """Vista API para ajustar stock de insumos"""
    if request.method == 'POST':
        try:
            from insumos.models import Insumo
            data = json.loads(request.body)
            
            try:
                insumo = Insumo.objects.get(id=insumo_id)
            except Insumo.DoesNotExist:
                return JsonResponse({'error': 'Insumo no encontrado'}, status=404)
            
            ajuste = data.get('ajuste', 0)
            motivo = data.get('motivo', '')
            
            # Aplicar el ajuste
            nuevo_stock = getattr(insumo, 'stock_actual', 0) + ajuste
            insumo.stock_actual = max(0, nuevo_stock)  # No permitir stock negativo
            insumo.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Stock ajustado correctamente. Nuevo stock: {insumo.stock_actual}',
                'nuevo_stock': insumo.stock_actual
            })
            
        except Exception as e:
            return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def api_guias_laboratorio(request):
    """Vista API para guías de laboratorio"""
    try:
        unidad_tematica_id = request.GET.get('unidad_tematica')
        
        if not unidad_tematica_id:
            return JsonResponse({'error': 'unidad_tematica es requerido'}, status=400)
        
        # Obtener guías de laboratorio de esa unidad temática
        guias = GuiaLaboratorio.objects.filter(unidad_tematica=unidad_tematica_id).order_by('numero')
        
        # Preparar los datos para el frontend
        guias_data = []
        for guia in guias:
            guias_data.append({
                'id': guia.id,
                'nombre': guia.nombre,
                'numero': guia.numero
            })
        
        return JsonResponse(guias_data, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)

@login_required
def api_practicas(request):
    """Vista API para prácticas"""
    try:
        guia_laboratorio_id = request.GET.get('guia_laboratorio')
        
        if not guia_laboratorio_id:
            return JsonResponse({'error': 'guia_laboratorio es requerido'}, status=400)
        
        # Obtener prácticas de esa guía de laboratorio
        practicas = Practica.objects.filter(guia_laboratorio=guia_laboratorio_id).order_by('numero')
        
        # Preparar los datos para el frontend
        practicas_data = []
        for practica in practicas:
            practicas_data.append({
                'id': practica.id,
                'nombre': practica.nombre,
                'numero': practica.numero
            })
        
        return JsonResponse(practicas_data, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login'), name='home'),
    path('login/', include('login.urls')),
    path('equipos/', include('equipos.urls')),
    path('insumos/', include('insumos.urls')),
    path('activos/', include('activos.urls')),
    path('guias/', include('guias.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('dashboard/', include('core.urls', namespace='core')),
    # CKEditor 5 URLs
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    # API endpoints
    path('api/carreras/', api_carreras, name='api_carreras'),
    path('api/asignaturas/', api_asignaturas, name='api_asignaturas'),
    path('api/unidades-tematicas/', api_unidades_tematicas, name='api_unidades_tematicas'),
    path('api/guias-laboratorio/', api_guias_laboratorio, name='api_guias_laboratorio'),
    path('api/practicas/', api_practicas, name='api_practicas'),
    path('api/proveedores/', api_proveedores, name='api_proveedores'),
    path('api/insumos/<int:insumo_id>/', api_insumos_detalle, name='api_insumos_detalle'),
    path('api/insumos/<int:insumo_id>/ajustar-stock/', api_insumos_ajustar_stock, name='api_insumos_ajustar_stock'),
    # Mantener rutas existentes para compatibilidad
    path('ingreso-datos/', include('ingreso_datos.urls')),
    path('visualizacion/', include('visualizacion.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


