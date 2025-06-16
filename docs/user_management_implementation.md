# User Management Implementation Plan

## Overview
This document outlines the comprehensive implementation plan for the user management system within our multitenant architecture. The system will handle authentication, authorization, and user profile management specific to each tenant following TDD methodology.

## App Location and Structure
The `users` app will be a tenant-specific application located at `techstore/backend/users/`, following standard Django app structure:

```
techstore/backend/
└── users/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── serializers.py
    ├── urls.py
    └── views.py
└── tests/
    └── users/
        ├── __init__.py
        ├── test_models.py
        ├── test_serializers.py
        └── test_views.py
    
```

Important: This app will be used within tenant schemas, not in the public schema, ensuring proper tenant data isolation.

## Implementation Steps

### 1. User Model Implementation (TDD)

#### 1.1 Testing Approach
- Write tests for custom user model extending `AbstractUser`
- Test role model implementation and relationship with users
- Verify tenant isolation and permissions

#### 1.2 Model Design
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.Model):
    """Role model with predefined roles: admin, staff, client"""
    name = models.CharField(max_length=50)
    # Additional fields for permissions

class User(AbstractUser):
    """Custom user model with tenant-specific fields"""
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    # Additional tenant-specific fields
```

### 2. Authentication System (TDD)

#### Example:
Arquitectura de Autenticación Multi-Tenant
1. Sistema de Autenticación por Niveles
python# authentication/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import get_public_schema_name, schema_context
from customers.models import Client, Domain
import logging

logger = logging.getLogger(__name__)

class TenantAuthenticationBackend(ModelBackend):
    """
    Backend de autenticación que considera el contexto del tenant
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica usuarios considerando el schema actual
        """
        # Obtener el dominio actual
        hostname = self._get_hostname(request)
        
        # Determinar el tenant basado en el dominio
        tenant = self._get_tenant_from_hostname(hostname)
        
        if not tenant:
            logger.warning(f"No se encontró tenant para el dominio: {hostname}")
            return None
        
        # Autenticar en el contexto del tenant
        with schema_context(tenant.schema_name):
            User = get_user_model()
            try:
                user = User.objects.get(username=username)
                if user.check_password(password) and self.user_can_authenticate(user):
                    # Agregar información del tenant al usuario
                    user.tenant = tenant
                    return user
            except User.DoesNotExist:
                logger.info(f"Usuario {username} no encontrado en tenant {tenant.name}")
                return None
    
    def _get_hostname(self, request):
        """Extrae el hostname de la request"""
        return request.get_host().split(':')[0]
    
    def _get_tenant_from_hostname(self, hostname):
        """Obtiene el tenant basado en el hostname"""
        try:
            domain = Domain.objects.select_related('tenant').get(
                domain=hostname
            )
            return domain.tenant
        except Domain.DoesNotExist:
            return None


class SystemAdminAuthenticationBackend(ModelBackend):
    """
    Backend para autenticar administradores del sistema (schema público)
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica solo en el schema público para administradores del sistema
        """
        # Solo funciona si estamos intentando acceder al admin del sistema
        if not self._is_system_admin_url(request):
            return None
        
        with schema_context(get_public_schema_name()):
            User = get_user_model()
            try:
                user = User.objects.get(username=username)
                if user.check_password(password) and user.is_staff:
                    user.is_system_admin = True
                    return user
            except User.DoesNotExist:
                return None
    
    def _is_system_admin_url(self, request):
        """Verifica si es una URL del admin del sistema"""
        return request.path.startswith('/system-admin/')
2. Modelos de Usuario Extendidos
python# users/models.py
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone
import uuid

class TenantUser(AbstractUser):
    """
    Modelo de usuario específico para cada tenant
    """
    # Identificador único global
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Información del tenant
    tenant_id = models.CharField(max_length=100, db_index=True)
    
    # Información adicional
    department = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Control de acceso
    is_tenant_admin = models.BooleanField(default=False)
    can_access_all_departments = models.BooleanField(default=False)
    
    # Auditoría
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    # Configuración de MFA (Multi-Factor Authentication)
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, blank=True)
    
    class Meta:
        db_table = 'tenant_users'
        indexes = [
            models.Index(fields=['tenant_id', 'username']),
            models.Index(fields=['email', 'tenant_id']),
        ]
    
    def is_account_locked(self):
        """Verifica si la cuenta está bloqueada"""
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False
    
    def increment_failed_login(self):
        """Incrementa los intentos fallidos y bloquea si es necesario"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=30)
        self.save()
    
    def reset_failed_login(self):
        """Resetea los intentos fallidos"""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save()


class TenantRole(models.Model):
    """
    Roles personalizados por tenant
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission)
    tenant_id = models.CharField(max_length=100, db_index=True)
    
    # Roles predefinidos
    is_system_role = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tenant_roles'
        unique_together = ['name', 'tenant_id']
3. Sistema de Permisos y Autorización
python# authorization/permissions.py
from rest_framework import permissions
from django.db import connection
from django_tenants.utils import get_public_schema_name

class IsTenantUser(permissions.BasePermission):
    """
    Permite acceso solo a usuarios del tenant actual
    """
    
    def has_permission(self, request, view):
        # Verificar que no estamos en el schema público
        if connection.schema_name == get_public_schema_name():
            return False
        
        # Verificar que el usuario está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Verificar que el usuario pertenece al tenant actual
        return hasattr(request.user, 'tenant_id') and \
               request.user.tenant_id == connection.schema_name


class IsTenantAdmin(permissions.BasePermission):
    """
    Permite acceso solo a administradores del tenant
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'is_tenant_admin') and
            request.user.is_tenant_admin
        )


class HasTenantPermission(permissions.BasePermission):
    """
    Verifica permisos específicos dentro del tenant
    """
    
    def __init__(self, permission_codename):
        self.permission_codename = permission_codename
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Verificar permiso en el contexto del tenant
        return request.user.has_perm(self.permission_codename)


class DepartmentAccessPermission(permissions.BasePermission):
    """
    Controla acceso basado en departamentos
    """
    
    def has_object_permission(self, request, view, obj):
        # Administradores tienen acceso total
        if request.user.can_access_all_departments:
            return True
        
        # Verificar si el objeto tiene departamento
        if hasattr(obj, 'department'):
            return obj.department == request.user.department
        
        return True
4. Middleware de Seguridad Multi-Tenant
python# middleware/security.py
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.db import connection
from django_tenants.utils import get_public_schema_name
import logging

logger = logging.getLogger(__name__)

class TenantSecurityMiddleware:
    """
    Middleware para gestionar la seguridad en contexto multi-tenant
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verificar consistencia del tenant
        if request.user.is_authenticated:
            if not self._verify_tenant_consistency(request):
                logout(request)
                return redirect('/unauthorized/')
        
        # Registrar actividad
        self._log_activity(request)
        
        response = self.get_response(request)
        
        # Agregar headers de seguridad
        self._add_security_headers(response)
        
        return response
    
    def _verify_tenant_consistency(self, request):
        """
        Verifica que el usuario esté accediendo al tenant correcto
        """
        # Skip para schema público
        if connection.schema_name == get_public_schema_name():
            return True
        
        # Verificar que el usuario pertenece al tenant actual
        if hasattr(request.user, 'tenant_id'):
            return request.user.tenant_id == connection.schema_name
        
        return False
    
    def _log_activity(self, request):
        """
        Registra la actividad del usuario
        """
        if request.user.is_authenticated:
            # Actualizar última actividad
            request.user.last_activity = timezone.now()
            request.user.last_login_ip = self._get_client_ip(request)
            request.user.save(update_fields=['last_activity', 'last_login_ip'])
    
    def _get_client_ip(self, request):
        """Obtiene la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _add_security_headers(self, response):
        """Agrega headers de seguridad"""
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
5. Vistas de Autenticación Seguras
python# authentication/views.py
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.db import connection
from django_tenants.utils import get_tenant_model
import pyotp
import qrcode
import io
import base64

class TenantLoginView(View):
    """
    Vista de login con soporte para MFA
    """
    template_name = 'auth/login.html'
    
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        # Si ya está autenticado, redirigir
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        context = {
            'tenant_name': self._get_tenant_name(),
            'enable_mfa': getattr(settings, 'ENABLE_MFA', False)
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        mfa_token = request.POST.get('mfa_token', '')
        
        # Intentar autenticar
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Verificar si la cuenta está bloqueada
            if user.is_account_locked():
                return JsonResponse({
                    'success': False,
                    'error': 'Cuenta bloqueada. Intente más tarde.'
                }, status=403)
            
            # Verificar MFA si está habilitado
            if user.mfa_enabled:
                if not self._verify_mfa_token(user, mfa_token):
                    user.increment_failed_login()
                    return JsonResponse({
                        'success': False,
                        'error': 'Token MFA inválido'
                    }, status=401)
            
            # Login exitoso
            user.reset_failed_login()
            login(request, user)
            
            # Registrar en log de auditoría
            self._log_successful_login(user, request)
            
            return JsonResponse({
                'success': True,
                'redirect_url': request.GET.get('next', '/dashboard/')
            })
        else:
            # Intentar obtener el usuario para incrementar intentos fallidos
            self._handle_failed_login(username, request)
            
            return JsonResponse({
                'success': False,
                'error': 'Credenciales inválidas'
            }, status=401)
    
    def _get_tenant_name(self):
        """Obtiene el nombre del tenant actual"""
        try:
            from customers.models import Client
            tenant = Client.objects.get(schema_name=connection.schema_name)
            return tenant.name
        except:
            return "Sistema"
    
    def _verify_mfa_token(self, user, token):
        """Verifica el token MFA"""
        if not token:
            return False
        
        totp = pyotp.TOTP(user.mfa_secret)
        return totp.verify(token, valid_window=1)
    
    def _log_successful_login(self, user, request):
        """Registra un login exitoso"""
        from .models import LoginAudit
        
        LoginAudit.objects.create(
            user=user,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=True,
            tenant_id=connection.schema_name
        )
    
    def _handle_failed_login(self, username, request):
        """Maneja un intento de login fallido"""
        from users.models import TenantUser
        
        try:
            user = TenantUser.objects.get(username=username)
            user.increment_failed_login()
        except TenantUser.DoesNotExist:
            pass
        
        # Registrar intento fallido
        from .models import LoginAudit
        
        LoginAudit.objects.create(
            username_attempted=username,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=False,
            tenant_id=connection.schema_name
        )


class MFASetupView(View):
    """
    Vista para configurar MFA
    """
    
    @method_decorator(login_required)
    def get(self, request):
        """Genera QR code para configurar MFA"""
        user = request.user
        
        # Generar secret si no existe
        if not user.mfa_secret:
            user.mfa_secret = pyotp.random_base32()
            user.save()
        
        # Generar URL para el QR
        totp_uri = pyotp.totp.TOTP(user.mfa_secret).provisioning_uri(
            name=user.email,
            issuer_name=self._get_tenant_name()
        )
        
        # Generar QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return render(request, 'auth/mfa_setup.html', {
            'qr_code': f'data:image/png;base64,{img_str}',
            'secret': user.mfa_secret
        })
    
    @method_decorator(login_required)
    def post(self, request):
        """Verifica y activa MFA"""
        token = request.POST.get('token')
        user = request.user
        
        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(token):
            user.mfa_enabled = True
            user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'MFA activado correctamente'
            })
        
        return JsonResponse({
            'success': False,
            'error': 'Token inválido'
        }, status=400)
6. API de Autorización con JWT
python# api/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context
import jwt

class TenantJWTAuthentication(JWTAuthentication):
    """
    Autenticación JWT que considera el contexto del tenant
    """
    
    def get_user(self, validated_token):
        """
        Obtiene el usuario del token validado en el contexto del tenant
        """
        try:
            user_id = validated_token['user_id']
            tenant_schema = validated_token.get('tenant_schema')
            
            if not tenant_schema:
                return None
            
            # Obtener usuario en el contexto del tenant
            with schema_context(tenant_schema):
                User = get_user_model()
                user = User.objects.get(id=user_id)
                user.tenant_schema = tenant_schema
                return user
                
        except (User.DoesNotExist, KeyError):
            return None


class TenantRefreshToken(RefreshToken):
    """
    Token personalizado que incluye información del tenant
    """
    
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        
        # Agregar claims personalizados
        token['tenant_schema'] = getattr(user, 'tenant_id', None)
        token['is_tenant_admin'] = getattr(user, 'is_tenant_admin', False)
        token['department'] = getattr(user, 'department', None)
        
        return token


# api/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.db import connection

@api_view(['POST'])
@permission_classes([AllowAny])
def tenant_token_obtain_pair(request):
    """
    Obtiene par de tokens (access/refresh) para autenticación API
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Username y password son requeridos'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Autenticar usuario
    user = authenticate(request, username=username, password=password)
    
    if user:
        # Generar tokens
        refresh = TenantRefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_tenant_admin': user.is_tenant_admin,
                'tenant_schema': connection.schema_name
            }
        })
    
    return Response({
        'error': 'Credenciales inválidas'
    }, status=status.HTTP_401_UNAUTHORIZED)
7. Decoradores y Utilidades de Autorización
python# authorization/decorators.py
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.db import connection
from django_tenants.utils import get_public_schema_name

def tenant_required(view_func):
    """
    Decorador que asegura que la vista se ejecute en contexto de tenant
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if connection.schema_name == get_public_schema_name():
            return redirect('/select-tenant/')
        return view_func(request, *args, **kwargs)
    return wrapped_view


def tenant_admin_required(view_func):
    """
    Decorador que requiere que el usuario sea admin del tenant
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not getattr(request.user, 'is_tenant_admin', False):
            raise PermissionDenied("Acceso denegado. Se requieren permisos de administrador.")
        
        return view_func(request, *args, **kwargs)
    return wrapped_view


def require_tenant_permission(permission_codename):
    """
    Decorador que verifica un permiso específico del tenant
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not request.user.has_perm(permission_codename):
                raise PermissionDenied(f"Se requiere el permiso: {permission_codename}")
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


# authorization/mixins.py
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

class TenantAdminRequiredMixin(UserPassesTestMixin):
    """
    Mixin que requiere que el usuario sea admin del tenant
    """
    
    def test_func(self):
        return self.request.user.is_authenticated and \
               getattr(self.request.user, 'is_tenant_admin', False)
    
    def handle_no_permission(self):
        raise PermissionDenied("Acceso denegado. Se requieren permisos de administrador.")


class TenantPermissionRequiredMixin(UserPassesTestMixin):
    """
    Mixin que verifica permisos específicos del tenant
    """
    permission_required = None
    
    def test_func(self):
        if not self.permission_required:
            return True
        
        return self.request.user.has_perm(self.permission_required)
8. Gestión de Sesiones y Tokens
python# authentication/managers.py
from django.contrib.sessions.models import Session
from django.utils import timezone
from django_tenants.utils import schema_context, get_tenant_model
from datetime import timedelta
import redis
import json

class TenantSessionManager:
    """
    Gestiona sesiones por tenant con Redis para mejor rendimiento
    """
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
    
    def create_session(self, user, request):
        """
        Crea una sesión segura para el usuario
        """
        session_data = {
            'user_id': user.id,
            'username': user.username,
            'tenant_id': user.tenant_id,
            'ip_address': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'created_at': timezone.now().isoformat(),
            'last_activity': timezone.now().isoformat()
        }
        
        # Generar ID único de sesión
        session_id = self._generate_session_id()
        
        # Guardar en Redis con TTL
        self.redis_client.setex(
            f"tenant_session:{user.tenant_id}:{session_id}",
            timedelta(hours=24),
            json.dumps(session_data)
        )
        
        # Registrar sesión activa del usuario
        self._register_active_session(user, session_id)
        
        return session_id
    
    def validate_session(self, session_id, tenant_id):
        """
        Valida que la sesión existe y es válida
        """
        session_key = f"tenant_session:{tenant_id}:{session_id}"
        session_data = self.redis_client.get(session_key)
        
        if not session_data:
            return None
        
        data = json.loads(session_data)
        
        # Actualizar última actividad
        data['last_activity'] = timezone.now().isoformat()
        self.redis_client.setex(
            session_key,
            timedelta(hours=24),
            json.dumps(data)
        )
        
        return data
    
    def revoke_session(self, session_id, tenant_id):
        """
        Revoca una sesión específica
        """
        session_key = f"tenant_session:{tenant_id}:{session_id}"
        return self.redis_client.delete(session_key)
    
    def revoke_all_user_sessions(self, user):
        """
        Revoca todas las sesiones de un usuario
        """
        pattern = f"tenant_session:{user.tenant_id}:*"
        
        for key in self.redis_client.scan_iter(match=pattern):
            session_data = json.loads(self.redis_client.get(key))
            if session_data['user_id'] == user.id:
                self.redis_client.delete(key)
    
    def get_active_sessions_count(self, tenant_id):
        """
        Obtiene el número de sesiones activas por tenant
        """
        pattern = f"tenant_session:{tenant_id}:*"
        return len(list(self.redis_client.scan_iter(match=pattern)))
    
    def _generate_session_id(self):
        """Genera un ID de sesión seguro"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _get_client_ip(self, request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _register_active_session(self, user, session_id):
        """Registra la sesión activa del usuario"""
        user_sessions_key = f"user_sessions:{user.tenant_id}:{user.id}"
        self.redis_client.sadd(user_sessions_key, session_id)
        self.redis_client.expire(user_sessions_key, timedelta(days=30))
9. Auditoría y Monitoreo
python# authentication/models.py
from django.db import models
from django.contrib.auth import get_user_model

class LoginAudit(models.Model):
    """
    Registro de auditoría de intentos de login
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    username_attempted = models.CharField(max_length=150, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    success = models.BooleanField()
    failure_reason = models.CharField(max_length=100, blank=True)
    tenant_id = models.CharField(max_length=100, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'login_audit'
        indexes = [
            models.Index(fields=['tenant_id', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]


class PermissionAudit(models.Model):
    """
    Registro de auditoría de cambios en permisos
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # grant, revoke, modify
    permission = models.CharField(max_length=255)
    target_user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='permission_changes'
    )
    tenant_id = models.CharField(max_length=100, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'permission_audit'
10. Configuración de Settings
python# settings.py

# Backends de autenticación
AUTHENTICATION_BACKENDS = [
    'authentication.backends.TenantAuthenticationBackend',
    'authentication.backends.SystemAdminAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',  # Fallback
]

# Configuración de sesiones
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_COOKIE_SECURE = True  # Solo HTTPS en producción
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'

# Configuración de CSRF
CSRF_COOKIE_SECURE = True  # Solo HTTPS en producción
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Configuración de passwords
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('api.authentication.TenantRefreshToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Configuración de MFA
ENABLE_MFA = True
MFA_ISSUER_NAME = 'Multi-Tenant App'

# Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_STORAGE_URL = 'redis://localhost:6379/1'
Flujo Completo de Autenticación

Usuario accede a empresa.example.com
Sistema identifica el tenant por el dominio
Usuario ingresa credenciales
Backend autentica en el schema del tenant
Si tiene MFA, solicita token
Crea sesión y/o JWT token
Todas las requests posteriores validan el contexto del tenant

Esta implementación proporciona:

Aislamiento completo entre tenants
Autenticación segura con MFA opcional
Autorización granular por permisos y roles
Auditoría completa de accesos
Gestión eficiente de sesiones
API REST con JWT para aplicaciones móviles
Protección contra ataques comunes


#### 2.1 JWT Authentication
- Implement token-based authentication with JWT
- Configure token expiration and refresh mechanisms
- Test token generation, validation, and refresh

#### 2.2 API Endpoints
- `/api/auth/login/` - Login endpoint
- `/api/auth/refresh/` - Token refresh endpoint
- `/api/auth/logout/` - Logout endpoint
- `/api/users/` - User management endpoints (CRUD)
- `/api/users/me/` - Current user profile endpoint

### 3. Role-Based Authorization (TDD)

#### 3.1 Role Implementation
- Create predefined roles: admin, staff, client
- Define permissions matrix for each role
- Test permission validation and access control

#### 3.2 Tenant Isolation
- Ensure users can only access their assigned tenant's data
- Implement tenant validation middleware
- Test cross-tenant access prevention

### 4. Admin Interface

#### 4.1 Tenant Admin Panel
- Customize Django admin for user management
- Implement role assignment interface
- Add filters and search for user management

### 5. Frontend Integration

#### 5.1 Login Interface
- Create login page with form validation
- Implement token storage and management in frontend
- Add error handling and user feedback

#### 5.2 User Dashboard
- Create welcome dashboard based on user role
- Implement navigation specific to user permissions
- Display user profile and settings

## Implementation Milestones

| Milestone | Description | Acceptance Criteria |
|-----------|-------------|---------------------|
| M1 | User model implementation | Tests pass, migrations run successfully |
| M2 | Authentication API | Login/logout works with JWT tokens |
| M3 | Role-based permissions | Users can only access permitted resources |
| M4 | Admin interface | Admin can manage users and roles |
| M5 | Frontend integration | Login and dashboard pages functional |

## Testing Strategy

### Test-Driven Development Approach
For each component, we will:
1. Write tests that define the expected behavior
2. Implement the minimum code required to pass the tests
3. Refactor while keeping tests passing

### Test Categories
- **Unit Tests**: Models, serializers, and isolated components
- **Integration Tests**: Authentication flow, role-based access, tenant isolation
- **End-to-End Tests**: Complete user journeys (login, user management, etc.)

## Dependencies
- Django REST framework for API implementation
- Simple JWT for token-based authentication
- django-tenants integration for schema-based isolation 