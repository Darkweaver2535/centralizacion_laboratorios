from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class FlexibleAuthBackend(ModelBackend):
    """
    Backend de autenticación personalizado que permite login con:
    - Username
    - Correo institucional
    - Email (si es diferente al correo institucional)
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        try:
            # Buscar usuario por username, correo institucional o email
            user = User.objects.get(
                Q(username__iexact=username) | 
                Q(correo_institucional__iexact=username) |
                Q(email__iexact=username)
            )
            
            # Verificar la contraseña
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
                
        except User.DoesNotExist:
            # Ejecutar hash de contraseña para evitar ataques de timing
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Si hay múltiples usuarios (no debería pasar), usar el primero
            users = User.objects.filter(
                Q(username__iexact=username) | 
                Q(correo_institucional__iexact=username) |
                Q(email__iexact=username)
            )
            for user in users:
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
        
        return None
    
    def user_can_authenticate(self, user):
        """
        Verificar si el usuario puede autenticarse
        """
        return getattr(user, 'is_active', True)
