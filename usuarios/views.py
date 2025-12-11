from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
import random
import string

from .models import Usuario, PermisoUsuario, LogActividad
from core.models import Laboratorio


def get_client_ip(request):
    """Obtener la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def enviar_credenciales_correo(usuario, password):
    """Enviar credenciales por correo electrónico"""
    try:
        send_mail(
            subject='Credenciales de acceso - Sistema de Laboratorios EMI',
            message=f'''
Hola {usuario.nombre_completo},

Se ha creado tu cuenta en el Sistema de Laboratorios EMI.

Tus credenciales de acceso son:
Usuario: {usuario.email}
Contraseña: {password}

Por seguridad, te recomendamos cambiar tu contraseña en el primer acceso.

Saludos,
Equipo de Sistemas EMI
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.correo_institucional],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error enviando correo: {e}")
        raise e


def puede_ver_usuario(user, usuario):
    """Verificar si un usuario puede ver otro usuario"""
    if user.rol == 'administrador':
        return True
    elif user.rol == 'jefe_uycit':
        return usuario.sede_asignacion == user.sede_asignacion
    else:
        return user == usuario

User = get_user_model()


@login_required
def lista_usuarios(request):
    """Vista principal para listar usuarios"""
    
    # Verificar permisos
    if not request.user.puede_crear_usuario('auxiliar') and request.user.rol != 'administrador':
        messages.error(request, 'No tienes permisos para acceder a esta sección')
        return redirect('core:dashboard')
    
    # Obtener filtros
    filtros = {
        'rol': request.GET.get('rol', ''),
        'sede': request.GET.get('sede', ''),
        'estado': request.GET.get('estado', ''),
        'busqueda': request.GET.get('busqueda', ''),
    }
    
    # Construir queryset con filtros
    usuarios = Usuario.objects.select_related('jefe_superior', 'creado_por')
    
    # Filtrar según el rol del usuario actual
    if request.user.rol == 'jefe_uycit':
        # Los jefes solo ven auxiliares de su sede
        usuarios = usuarios.filter(
            sede_asignacion=request.user.sede_asignacion,
            rol='auxiliar'
        )
    elif request.user.rol == 'administrador':
        # Los administradores ven todos
        pass
    else:
        # Auxiliares no tienen acceso
        messages.error(request, 'No tienes permisos para ver usuarios')
        return redirect('core:dashboard')
    
    # Aplicar filtros adicionales
    if filtros['rol']:
        usuarios = usuarios.filter(rol=filtros['rol'])
    
    if filtros['sede']:
        usuarios = usuarios.filter(sede_asignacion=filtros['sede'])
    
    if filtros['estado']:
        usuarios = usuarios.filter(estado_usuario=filtros['estado'])
    
    if filtros['busqueda']:
        usuarios = usuarios.filter(
            Q(nombres__icontains=filtros['busqueda']) |
            Q(apellidos__icontains=filtros['busqueda']) |
            Q(numero_documento__icontains=filtros['busqueda']) |
            Q(correo_institucional__icontains=filtros['busqueda'])
        )
    
    # Ordenar por fecha de creación más reciente
    usuarios = usuarios.order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(usuarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'usuarios': page_obj,
        'filtros': filtros,
        'roles': Usuario.ROLES,
        'sedes': Usuario.SEDES,
        'estados': Usuario.ESTADOS,
        'total_usuarios': usuarios.count(),
    }
    
    return render(request, 'usuarios/lista.html', context)


@login_required
def crear_usuario(request):
    """Vista para crear un nuevo usuario"""
    
    # Verificar permisos básicos
    if not request.user.puede_crear_usuario('auxiliar'):
        messages.error(request, 'No tienes permisos para crear usuarios')
        return redirect('usuarios:lista')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Obtener datos del formulario
                rol = request.POST.get('rol')
                
                # Verificar permisos específicos para el rol
                if not request.user.puede_crear_usuario(rol):
                    messages.error(request, f'No tienes permisos para crear usuarios con el rol {rol}')
                    return redirect('usuarios:crear')
                
                # Crear el usuario
                usuario = Usuario()
                
                # Información personal
                usuario.nombres = request.POST.get('nombres')
                usuario.apellidos = request.POST.get('apellidos')
                usuario.numero_documento = request.POST.get('numero_documento')
                usuario.telefono_personal = request.POST.get('telefono_personal', '')
                usuario.correo_institucional = request.POST.get('correo_institucional')
                
                # Información profesional
                if rol in ['administrador', 'jefe_uycit']:
                    usuario.especialidad_area = request.POST.get('especialidad_area')
                else:
                    usuario.nivel_formacion = request.POST.get('nivel_formacion')
                    usuario.area_formacion = request.POST.get('area_formacion')
                    usuario.experiencia_laboratorios = request.POST.get('experiencia_laboratorios') or None
                
                # Información institucional
                usuario.rol = rol
                usuario.sede_asignacion = request.POST.get('sede_asignacion')
                usuario.cargo_posicion = request.POST.get('cargo_posicion', '')
                usuario.unidad = request.POST.get('unidad', '')
                
                if rol == 'auxiliar':
                    usuario.turno_trabajo = request.POST.get('turno_trabajo')
                    fecha_inicio = request.POST.get('fecha_inicio')
                    if fecha_inicio:
                        usuario.fecha_inicio = fecha_inicio
                    
                    # Asignar jefe superior
                    jefe_id = request.POST.get('jefe_superior')
                    if jefe_id:
                        usuario.jefe_superior_id = jefe_id
                
                # Información adicional
                usuario.descripcion_responsabilidades = request.POST.get('descripcion_responsabilidades', '')
                usuario.observaciones = request.POST.get('observaciones', '')
                usuario.estado_usuario = request.POST.get('estado_usuario', 'activo')
                
                # Información de acceso
                contraseña = request.POST.get('password')
                usuario.password = make_password(contraseña)
                usuario.creado_por = request.user
                
                # Generar username automáticamente
                usuario.email = usuario.correo_institucional
                
                # Manejar foto de perfil
                if 'foto_perfil' in request.FILES:
                    usuario.foto_perfil = request.FILES['foto_perfil']
                
                usuario.save()
                
                # Asignar laboratorios
                laboratorios_ids = request.POST.getlist('laboratorios_asignados')
                if laboratorios_ids:
                    usuario.laboratorios_asignados.set(laboratorios_ids)
                
                # Asignar permisos para administradores y jefes
                if rol in ['administrador', 'jefe_uycit']:
                    permisos = request.POST.getlist('areas_responsabilidad')
                    for permiso in permisos:
                        PermisoUsuario.objects.create(
                            usuario=usuario,
                            area=permiso
                        )
                
                # Registrar actividad
                LogActividad.objects.create(
                    usuario=request.user,
                    accion='Creación de usuario',
                    descripcion=f'Se creó el usuario {usuario.nombre_completo} con rol {usuario.get_rol_display()}',
                    ip_address=get_client_ip(request)
                )
                
                # Enviar credenciales por correo (opcional)
                try:
                    enviar_credenciales_correo(usuario, contraseña)
                except Exception as e:
                    messages.warning(request, f'Usuario creado pero no se pudo enviar el correo: {str(e)}')
                
                messages.success(request, f'Usuario {usuario.nombre_completo} creado exitosamente')
                return redirect('usuarios:detalle', pk=usuario.pk)
                
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
    
    # Obtener datos para el formulario
    laboratorios = Laboratorio.objects.all()
    jefes_disponibles = Usuario.objects.filter(
        rol='jefe_uycit',
        sede_asignacion=request.user.sede_asignacion if request.user.rol == 'jefe_uycit' else None,
        estado_usuario='activo'
    )
    
    # Definir roles que puede crear
    roles_disponibles = []
    if request.user.rol == 'administrador':
        roles_disponibles = [('administrador', 'Administrador'), ('jefe_uycit', 'Jefe UYCIT')]
    elif request.user.rol == 'jefe_uycit':
        roles_disponibles = [('auxiliar', 'Auxiliar/Encargado de Laboratorio')]
    
    context = {
        'roles_disponibles': roles_disponibles,
        'sedes': Usuario.SEDES,
        'estados': Usuario.ESTADOS,
        'niveles_formacion': Usuario.NIVELES_FORMACION,
        'turnos': Usuario.TURNOS,
        'laboratorios': laboratorios,
        'jefes_disponibles': jefes_disponibles,
        'areas_responsabilidad': PermisoUsuario.AREAS_RESPONSABILIDAD,
    }
    
    return render(request, 'usuarios/crear.html', context)


@login_required
def crear_usuario_simple(request):
    """Vista simplificada para crear un nuevo usuario"""
    
    # Verificar permisos básicos
    if not request.user.puede_crear_usuario('auxiliar'):
        messages.error(request, 'No tienes permisos para crear usuarios')
        return redirect('usuarios:lista')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Obtener datos del formulario
                rol = request.POST.get('rol')
                
                # Crear el usuario
                usuario = Usuario()
                
                # Información personal
                usuario.nombres = request.POST.get('nombres')
                usuario.apellidos = request.POST.get('apellidos')
                usuario.numero_documento = request.POST.get('numero_documento')
                usuario.correo_institucional = request.POST.get('correo_institucional')
                
                # Información institucional
                usuario.rol = rol
                usuario.sede_asignacion = request.POST.get('sede_asignacion')
                usuario.cargo_posicion = request.POST.get('cargo_posicion', '')
                
                # Información adicional
                usuario.nivel_formacion = request.POST.get('nivel_formacion')
                usuario.area_formacion = request.POST.get('area_formacion')
                usuario.turno_trabajo = request.POST.get('turno_trabajo')
                usuario.estado_usuario = request.POST.get('estado_usuario', 'activo')
                
                # Información de acceso
                contraseña = request.POST.get('password')
                usuario.password = make_password(contraseña)
                usuario.creado_por = request.user
                usuario.email = usuario.correo_institucional
                
                usuario.save()
                
                messages.success(request, f'Usuario {usuario.nombre_completo} creado exitosamente')
                return redirect('usuarios:detalle', pk=usuario.pk)
                
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
    
    # Obtener datos para el formulario
    roles_disponibles = []
    if request.user.rol == 'administrador':
        roles_disponibles = [('administrador', 'Administrador'), ('jefe_uycit', 'Jefe UYCIT'), ('auxiliar', 'Auxiliar')]
    elif request.user.rol == 'jefe_uycit':
        roles_disponibles = [('auxiliar', 'Auxiliar/Encargado de Laboratorio')]
    
    context = {
        'roles_disponibles': roles_disponibles,
        'sedes': Usuario.SEDES,
        'estados': Usuario.ESTADOS,
        'niveles_formacion': Usuario.NIVELES_FORMACION,
        'turnos': Usuario.TURNOS,
    }
    
    return render(request, 'usuarios/crear_simple.html', context)


@login_required
def detalle_usuario(request, pk):
    """Vista para ver detalles de un usuario"""
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Verificar permisos de acceso
    if not puede_ver_usuario(request.user, usuario):
        messages.error(request, 'No tienes permisos para ver este usuario')
        return redirect('usuarios:lista')
    
    context = {
        'usuario': usuario,
        'permisos': usuario.permisos.filter(activo=True),
        'actividades': usuario.actividades.order_by('-fecha')[:10],
        'usuarios_creados': usuario.usuarios_creados.all()[:5],
        'estados': [
            ('activo', 'Activo'),
            ('inactivo', 'Inactivo'),
            ('suspendido', 'Suspendido Temporalmente'),
        ],
    }
    
    return render(request, 'usuarios/detalle.html', context)


@login_required
def editar_usuario(request, pk):
    """Vista para editar un usuario"""
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Verificar permisos
    if not puede_editar_usuario(request.user, usuario):
        messages.error(request, 'No tienes permisos para editar este usuario')
        return redirect('usuarios:detalle', pk=pk)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Guardar datos anteriores para el log
                datos_anteriores = {
                    'nombres': usuario.nombres,
                    'apellidos': usuario.apellidos,
                    'estado': usuario.estado_usuario,
                }
                
                # Actualizar información personal
                usuario.nombres = request.POST.get('nombres')
                usuario.apellidos = request.POST.get('apellidos')
                usuario.telefono_personal = request.POST.get('telefono_personal', '')
                
                # Actualizar información profesional
                if usuario.rol in ['administrador', 'jefe_uycit']:
                    usuario.especialidad_area = request.POST.get('especialidad_area')
                else:
                    usuario.area_formacion = request.POST.get('area_formacion')
                    usuario.experiencia_laboratorios = request.POST.get('experiencia_laboratorios') or None
                
                # Actualizar información institucional
                usuario.cargo_posicion = request.POST.get('cargo_posicion', '')
                usuario.unidad = request.POST.get('unidad', '')
                usuario.descripcion_responsabilidades = request.POST.get('descripcion_responsabilidades', '')
                usuario.observaciones = request.POST.get('observaciones', '')
                usuario.estado_usuario = request.POST.get('estado_usuario')
                
                # Manejar foto de perfil
                if 'foto_perfil' in request.FILES:
                    usuario.foto_perfil = request.FILES['foto_perfil']
                
                usuario.save()
                
                # Actualizar laboratorios asignados
                laboratorios_ids = request.POST.getlist('laboratorios_asignados')
                usuario.laboratorios_asignados.set(laboratorios_ids)
                
                # Actualizar permisos si es admin o jefe
                if usuario.rol in ['administrador', 'jefe_uycit']:
                    # Eliminar permisos actuales
                    usuario.permisos.all().delete()
                    
                    # Crear nuevos permisos
                    permisos = request.POST.getlist('areas_responsabilidad')
                    for permiso in permisos:
                        PermisoUsuario.objects.create(
                            usuario=usuario,
                            area=permiso
                        )
                
                # Registrar cambios en el log
                cambios = []
                if datos_anteriores['nombres'] != usuario.nombres:
                    cambios.append(f"Nombres: '{datos_anteriores['nombres']}' → '{usuario.nombres}'")
                if datos_anteriores['apellidos'] != usuario.apellidos:
                    cambios.append(f"Apellidos: '{datos_anteriores['apellidos']}' → '{usuario.apellidos}'")
                if datos_anteriores['estado'] != usuario.estado_usuario:
                    cambios.append(f"Estado: '{datos_anteriores['estado']}' → '{usuario.estado_usuario}'")
                
                if cambios:
                    LogActividad.objects.create(
                        usuario=request.user,
                        accion='Edición de usuario',
                        descripcion=f"Usuario {usuario.nombre_completo} editado. Cambios: {'; '.join(cambios)}",
                        ip_address=get_client_ip(request)
                    )
                
                messages.success(request, f'Usuario {usuario.nombre_completo} actualizado exitosamente')
                return redirect('usuarios:detalle', pk=usuario.pk)
                
        except Exception as e:
            messages.error(request, f'Error al actualizar usuario: {str(e)}')
    
    # Datos para el formulario
    laboratorios = Laboratorio.objects.all()
    permisos_actuales = list(usuario.permisos.filter(activo=True).values_list('area', flat=True))
    
    context = {
        'usuario': usuario,
        'sedes': Usuario.SEDES,
        'estados': Usuario.ESTADOS,
        'niveles_formacion': Usuario.NIVELES_FORMACION,
        'turnos': Usuario.TURNOS,
        'laboratorios': laboratorios,
        'areas_responsabilidad': PermisoUsuario.AREAS_RESPONSABILIDAD,
        'permisos_actuales': permisos_actuales,
    }
    
    return render(request, 'usuarios/editar.html', context)


@login_required
def eliminar_usuario(request, pk):
    """Vista para eliminar/desactivar un usuario"""
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Verificar permisos
    if not puede_eliminar_usuario(request.user, usuario):
        messages.error(request, 'No tienes permisos para eliminar este usuario')
        return redirect('usuarios:detalle', pk=pk)
    
    if request.method == 'POST':
        try:
            # En lugar de eliminar, desactivamos el usuario
            usuario.estado_usuario = 'inactivo'
            usuario.is_active = False
            usuario.save()
            
            # Registrar actividad
            LogActividad.objects.create(
                usuario=request.user,
                accion='Desactivación de usuario',
                descripcion=f'Se desactivó el usuario {usuario.nombre_completo}',
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, f'Usuario {usuario.nombre_completo} desactivado exitosamente')
            return redirect('usuarios:lista')
            
        except Exception as e:
            messages.error(request, f'Error al desactivar usuario: {str(e)}')
    
    context = {'usuario': usuario}
    return render(request, 'usuarios/eliminar.html', context)


# APIs para formularios dinámicos

@login_required
def api_laboratorios_por_sede(request, sede):
    """API para obtener laboratorios por sede"""
    try:
        # Por ahora devolvemos todos los laboratorios
        # Esta funcionalidad se puede expandir cuando se implemente la relación sede-laboratorio
        laboratorios = Laboratorio.objects.all().values('id', 'nombre')
        
        laboratorios_data = []
        for lab in laboratorios:
            laboratorio_obj = Laboratorio.objects.get(id=lab['id'])
            laboratorios_data.append({
                'id': lab['id'],
                'nombre': laboratorio_obj.get_nombre_display()
            })
        
        return JsonResponse({
            'success': True,
            'laboratorios': laboratorios_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_jefes_por_sede(request, sede):
    """API para obtener jefes UYCIT por sede"""
    try:
        jefes = Usuario.objects.filter(
            rol='jefe_uycit',
            sede_asignacion=sede,
            estado_usuario='activo'
        ).values('id', 'nombres', 'apellidos')
        
        jefes_data = []
        for jefe in jefes:
            jefes_data.append({
                'id': jefe['id'],
                'nombre_completo': f"{jefe['nombres']} {jefe['apellidos']}"
            })
        
        return JsonResponse({
            'success': True,
            'jefes': jefes_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Funciones auxiliares

def puede_ver_usuario(usuario_actual, usuario_objetivo):
    """Verifica si un usuario puede ver otro usuario"""
    if usuario_actual.rol == 'administrador':
        return True
    elif usuario_actual.rol == 'jefe_uycit':
        return (usuario_objetivo.rol == 'auxiliar' and 
                usuario_objetivo.sede_asignacion == usuario_actual.sede_asignacion)
    return usuario_actual == usuario_objetivo


def puede_editar_usuario(usuario_actual, usuario_objetivo):
    """Verifica si un usuario puede editar otro usuario"""
    if usuario_actual.rol == 'administrador':
        return True
    elif usuario_actual.rol == 'jefe_uycit':
        return (usuario_objetivo.rol == 'auxiliar' and 
                usuario_objetivo.sede_asignacion == usuario_actual.sede_asignacion)
    return False


def puede_eliminar_usuario(usuario_actual, usuario_objetivo):
    """Verifica si un usuario puede eliminar otro usuario"""
    # Solo administradores pueden eliminar usuarios
    return usuario_actual.rol == 'administrador'


def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def generar_contraseña_temporal():
    """Genera una contraseña temporal segura"""
    length = 12
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(length))


def enviar_credenciales_correo(usuario, contraseña):
    """Envía las credenciales por correo al usuario"""
    asunto = f'Bienvenido al Sistema de Laboratorios - {usuario.sede_asignacion}'
    
    mensaje = f"""
    Estimado/a {usuario.nombre_completo},
    
    Se ha creado su cuenta en el Sistema de Centralización de Laboratorios.
    
    Sus credenciales de acceso son:
    Usuario: {usuario.username}
    Contraseña: {contraseña}
    
    Rol: {usuario.get_rol_display()}
    Sede: {usuario.get_sede_asignacion_display()}
    
    Para acceder al sistema, ingrese a: [URL del sistema]
    
    Por seguridad, se recomienda cambiar su contraseña en el primer acceso.
    
    Saludos cordiales,
    Equipo de Administración del Sistema
    """
    
    send_mail(
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,
        [usuario.correo_institucional],
        fail_silently=False,
    )


@login_required
def mi_perfil(request):
    """Vista para mostrar y editar el perfil del usuario actual"""
    
    if request.method == 'POST':
        usuario = request.user
        
        # Actualizar datos básicos
        usuario.nombres = request.POST.get('nombres', usuario.nombres)
        usuario.apellidos = request.POST.get('apellidos', usuario.apellidos)
        usuario.telefono = request.POST.get('telefono', usuario.telefono)
        usuario.ci = request.POST.get('ci', usuario.ci)
        usuario.expedido = request.POST.get('expedido', usuario.expedido)
        usuario.fecha_nacimiento = request.POST.get('fecha_nacimiento') or usuario.fecha_nacimiento
        
        # Validar que no se cambie correo institucional
        nuevo_correo = request.POST.get('correo_institucional')
        if nuevo_correo and nuevo_correo != usuario.correo_institucional:
            messages.warning(request, 'El correo institucional no puede ser modificado. Contacta al administrador si necesitas cambiarlo.')
        
        try:
            usuario.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('usuarios:perfil')
        except Exception as e:
            messages.error(request, f'Error al actualizar el perfil: {str(e)}')
    
    # Datos para el contexto
    context = {
        'usuario': request.user,
        'estados_ci': [
            ('LP', 'La Paz'),
            ('CB', 'Cochabamba'),
            ('SC', 'Santa Cruz'),
            ('OR', 'Oruro'),
            ('PT', 'Potosí'),
            ('TJ', 'Tarija'),
            ('CH', 'Chuquisaca'),
            ('BE', 'Beni'),
            ('PD', 'Pando'),
        ],
    }
    
    return render(request, 'usuarios/mi_perfil.html', context)


@login_required
def configuracion_usuario(request):
    """Vista para configuraciones de la cuenta del usuario"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'cambiar_password':
            password_actual = request.POST.get('password_actual')
            password_nuevo = request.POST.get('password_nuevo')
            password_confirmacion = request.POST.get('password_confirmacion')
            
            # Verificar password actual
            if not request.user.check_password(password_actual):
                messages.error(request, 'La contraseña actual es incorrecta')
                return redirect('usuarios:configuracion')
            
            # Verificar que las nuevas contraseñas coincidan
            if password_nuevo != password_confirmacion:
                messages.error(request, 'Las nuevas contraseñas no coinciden')
                return redirect('usuarios:configuracion')
            
            # Verificar longitud mínima
            if len(password_nuevo) < 8:
                messages.error(request, 'La nueva contraseña debe tener al menos 8 caracteres')
                return redirect('usuarios:configuracion')
            
            # Cambiar contraseña
            try:
                request.user.set_password(password_nuevo)
                request.user.save()
                
                # Registrar actividad
                LogActividad.objects.create(
                    usuario=request.user,
                    accion='cambio_password',
                    detalles='Usuario cambió su contraseña'
                )
                
                messages.success(request, 'Contraseña cambiada correctamente. Por favor, inicia sesión nuevamente.')
                return redirect('login:logout')
            except Exception as e:
                messages.error(request, f'Error al cambiar la contraseña: {str(e)}')
    
    # Obtener actividad reciente del usuario
    actividades_recientes = LogActividad.objects.filter(
        usuario=request.user
    ).order_by('-fecha')[:10]
    
    context = {
        'usuario': request.user,
        'actividades_recientes': actividades_recientes,
    }
    
    return render(request, 'usuarios/configuracion.html', context)


@login_required
def cambiar_password(request):
    """Vista para cambiar contraseña del usuario autenticado"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Verificar password actual
        if not request.user.check_password(current_password):
            messages.error(request, 'La contraseña actual es incorrecta')
            return redirect('usuarios:perfil')
        
        # Verificar que las nuevas contraseñas coincidan
        if new_password != confirm_password:
            messages.error(request, 'Las nuevas contraseñas no coinciden')
            return redirect('usuarios:perfil')
        
        # Verificar longitud mínima
        if len(new_password) < 8:
            messages.error(request, 'La nueva contraseña debe tener al menos 8 caracteres')
            return redirect('usuarios:perfil')
        
        # Cambiar la contraseña
        try:
            request.user.set_password(new_password)
            request.user.save()
            
            # Registrar actividad
            LogActividad.objects.create(
                usuario=request.user,
                accion='cambio_password',
                descripcion='Cambió su contraseña'
            )
            
            messages.success(request, 'Contraseña cambiada exitosamente')
            
            # Re-autenticar al usuario para que no se desloguee
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            
        except Exception as e:
            messages.error(request, f'Error al cambiar la contraseña: {str(e)}')
        
        return redirect('usuarios:perfil')
    
    # Si es GET, redirigir al perfil
    return redirect('usuarios:perfil')


@login_required
def cambiar_estado(request, pk):
    """Vista para cambiar el estado de un usuario (solo administradores)"""
    # Verificar permisos de administrador
    if request.user.rol != 'administrador':
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('usuarios:lista')
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        razon = request.POST.get('razon', '')
        
        # Validar que el estado sea válido
        estados_validos = ['activo', 'inactivo', 'suspendido']
        if nuevo_estado not in estados_validos:
            messages.error(request, 'Estado no válido')
            return redirect('usuarios:detalle', pk=pk)
        
        # No permitir cambiar el estado del propio usuario
        if usuario == request.user:
            messages.error(request, 'No puedes cambiar tu propio estado')
            return redirect('usuarios:detalle', pk=pk)
        
        try:
            # Guardar estado anterior para el log
            estado_anterior = usuario.estado_usuario
            
            # Cambiar el estado del usuario
            usuario.estado_usuario = nuevo_estado
            
            # También actualizar is_active basado en el nuevo estado
            if nuevo_estado == 'activo':
                usuario.is_active = True
            else:
                usuario.is_active = False
            
            usuario.save()
            
            # Registrar actividad
            LogActividad.objects.create(
                usuario=request.user,
                accion='cambio_estado_usuario',
                descripcion=f'Cambió el estado de {usuario.get_full_name()} a {nuevo_estado}. Razón: {razon}'
            )
            
            # También registrar en el log del usuario afectado
            LogActividad.objects.create(
                usuario=usuario,
                accion='estado_cambiado',
                descripcion=f'Su estado fue cambiado a {nuevo_estado} por {request.user.get_full_name()}. Razón: {razon}'
            )
            
            messages.success(request, f'Estado del usuario {usuario.get_full_name()} cambiado a {nuevo_estado} exitosamente')
            
        except Exception as e:
            messages.error(request, f'Error al cambiar el estado: {str(e)}')
        
        return redirect('usuarios:detalle', pk=pk)
    
    # Si es GET, redirigir al detalle
    return redirect('usuarios:detalle', pk=pk)
