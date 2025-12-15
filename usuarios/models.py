from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from core.models import UnidadAcademica, Laboratorio
import string
import secrets

def validar_correo_institucional(email):
    """Validador personalizado para correos institucionales de EMI"""
    dominios_validos = ['@est.emi.edu.bo', '@doc.emi.edu.bo', '@adm.emi.edu.bo']
    
    if not any(email.endswith(dominio) for dominio in dominios_validos):
        raise ValidationError(
            'El correo debe terminar en @est.emi.edu.bo, @doc.emi.edu.bo o @adm.emi.edu.bo'
        )

class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario"""
    
    def create_user(self, correo_institucional, password=None, **extra_fields):
        """Crea y guarda un usuario regular"""
        if not correo_institucional:
            raise ValueError('El correo institucional es requerido')
        
        # Generar username si no se proporciona
        if 'username' not in extra_fields:
            extra_fields['username'] = correo_institucional.split('@')[0]
        
        # Normalizar el correo
        correo_institucional = self.normalize_email(correo_institucional)
        extra_fields['email'] = correo_institucional
        
        # Configurar valores por defecto
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('estado_usuario', 'activo')
        extra_fields.setdefault('debe_cambiar_password', True)
        
        # Crear el usuario
        user = self.model(correo_institucional=correo_institucional, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, correo_institucional, password=None, **extra_fields):
        """Crea y guarda un superusuario"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'administrador')
        extra_fields.setdefault('sede_asignacion', 'emi')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')
            
        return self.create_user(correo_institucional, password, **extra_fields)


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado para el sistema de laboratorios
    Implementa jerarquía: Administrador -> Docente -> Jefe UYCIT -> Auxiliar
    """
    
    # Roles del sistema
    ROLES = [
        ('administrador', 'Administrador'),
        ('docente', 'Docente'),
        ('estudiante', 'Estudiante'),
        ('jefe_uycit', 'Jefe UYCIT'),
        ('auxiliar', 'Auxiliar/Encargado de Laboratorio'),
    ]
    
    # Sedes disponibles
    SEDES = [
        ('UALP', 'Unidad Académica La Paz'),
        ('UACB', 'Unidad Académica Cochabamba'),
        ('UASC', 'Unidad Académica Santa Cruz'),
        ('UATP', 'Unidad Académica Trópico'),
        ('UARB', 'Unidad Académica Riberalta'),
    ]
    
    # Estados de usuario
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('suspendido', 'Suspendido Temporalmente'),
    ]
    
    # Niveles de formación (para auxiliares)
    NIVELES_FORMACION = [
        ('ingeniero', 'Ingeniero'),
        ('licenciado', 'Licenciado'),
        ('tecnico_superior', 'Técnico Superior'),
        ('tecnico_medio', 'Técnico Medio'),
        ('otro', 'Otro'),
    ]
    
    # Turnos de trabajo
    TURNOS = [
        ('grado', 'Grado'),
        ('tecnologico', 'Tecnológico'),
    ]
    
    # Información Personal
    nombres = models.CharField(
        max_length=100,
        verbose_name="Nombres"
    )
    apellidos = models.CharField(
        max_length=100,
        verbose_name="Apellidos"
    )
    numero_documento = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de Carnet de Identidad",
        validators=[RegexValidator(r'^\d+$', 'Solo se permiten números')]
    )
    telefono_personal = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono Personal",
        validators=[RegexValidator(r'^\+?[\d\s\-\(\)]+$', 'Formato de teléfono inválido')]
    )
    
    @property
    def telefono(self):
        """Alias para telefono_personal para compatibilidad"""
        return self.telefono_personal
    
    @property
    def cargo(self):
        """Alias para cargo_posicion para compatibilidad"""
        return self.cargo_posicion
    foto_perfil = models.ImageField(
        upload_to='usuarios/fotos/',
        blank=True,
        null=True,
        verbose_name="Foto de Perfil"
    )
    
    # Información Profesional
    especialidad_area = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Especialidad/Área de Conocimiento"
    )
    nivel_formacion = models.CharField(
        max_length=20,
        choices=NIVELES_FORMACION,
        blank=True,
        verbose_name="Nivel de Formación"
    )
    area_formacion = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Área de Formación"
    )
    experiencia_laboratorios = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Experiencia en Laboratorios (años)"
    )
    
    # Información Institucional
    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        verbose_name="Rol en el Sistema"
    )
    sede_asignacion = models.CharField(
        max_length=10,
        choices=SEDES,
        verbose_name="Sede de Asignación"
    )
    cargo_posicion = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Cargo/Posición Institucional"
    )
    unidad = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Unidad"
    )
    correo_institucional = models.EmailField(
        unique=True,
        verbose_name="Correo Institucional",
        validators=[validar_correo_institucional]
    )
    turno_trabajo = models.CharField(
        max_length=20,
        choices=TURNOS,
        blank=True,
        verbose_name="Turno de Trabajo"
    )
    
    # Responsabilidades y Permisos
    laboratorios_asignados = models.ManyToManyField(
        Laboratorio,
        blank=True,
        verbose_name="Laboratorios Asignados"
    )
    descripcion_responsabilidades = models.TextField(
        blank=True,
        verbose_name="Descripción de Responsabilidades"
    )
    
    # Jerarquía
    jefe_superior = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'rol': 'jefe_uycit'},
        verbose_name="Jefe Inmediato Superior"
    )
    creado_por = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios_creados',
        verbose_name="Creado por"
    )
    
    # Información Adicional
    fecha_inicio = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Inicio"
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )
    estado_usuario = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='activo',
        verbose_name="Estado del Usuario"
    )
    debe_cambiar_password = models.BooleanField(
        default=True,
        verbose_name="Debe cambiar contraseña en el próximo acceso"
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Manager personalizado
    objects = UsuarioManager()
    
    # Email field para el sistema de autenticación
    EMAIL_FIELD = 'correo_institucional'
    USERNAME_FIELD = 'correo_institucional'
    REQUIRED_FIELDS = ['nombres', 'apellidos']
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['apellidos', 'nombres']
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.get_rol_display()})"
    
    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def usuario_generado(self):
        """Genera el username automáticamente"""
        nombres_clean = self.nombres.lower().replace(' ', '.')
        apellidos_clean = self.apellidos.lower().replace(' ', '.')
        sede = self.sede_asignacion.lower()
        return f"{nombres_clean}.{apellidos_clean}.{sede}"
    
    def puede_crear_usuario(self, rol_destino):
        """Verifica si el usuario puede crear otro usuario con el rol especificado"""
        if self.rol == 'administrador':
            return rol_destino in ['administrador', 'jefe_uycit', 'auxiliar']
        elif self.rol == 'jefe_uycit':
            return rol_destino == 'auxiliar'
        return False
    
    def get_laboratorios_disponibles(self):
        """Retorna los laboratorios disponibles según la sede del usuario"""
        # Esta funcionalidad se implementará según la estructura de laboratorios
        return Laboratorio.objects.all()  # Por ahora todos
    
    def save(self, *args, **kwargs):
        # Generar username automáticamente si no existe
        if not self.username:
            self.username = self.usuario_generado
        
        # Establecer email como correo institucional si no está definido
        if not self.email and self.correo_institucional:
            self.email = self.correo_institucional
            
        super().save(*args, **kwargs)


class PermisoUsuario(models.Model):
    """
    Modelo para gestionar permisos específicos de usuarios
    """
    AREAS_RESPONSABILIDAD = [
        ('gestion_equipos', 'Gestión de Equipos'),
        ('gestion_insumos', 'Gestión de Insumos'),
        ('supervision_guias', 'Supervisión de Guías de Laboratorio'),
        ('investigacion_servicios', 'Investigación y Servicios'),
        ('administracion_usuarios', 'Administración de Usuarios'),
        ('dashboard_reordenamiento', 'Dashboard de Reordenamiento'),
    ]
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='permisos'
    )
    area = models.CharField(
        max_length=30,
        choices=AREAS_RESPONSABILIDAD
    )
    activo = models.BooleanField(default=True)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['usuario', 'area']
        verbose_name = "Permiso de Usuario"
        verbose_name_plural = "Permisos de Usuarios"
    
    def __str__(self):
        return f"{self.usuario.nombre_completo} - {self.get_area_display()}"


class LogActividad(models.Model):
    """
    Modelo para registrar actividades del sistema
    """
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='actividades'
    )
    accion = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Log de Actividad"
        verbose_name_plural = "Logs de Actividades"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.usuario.nombre_completo} - {self.accion}"
