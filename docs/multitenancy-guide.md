# Arquitectura Multitenant con Django y PostgreSQL

## Introducción a los Sistemas Multitenant

Un sistema multitenant (multiinquilino) es una arquitectura de software donde una única instancia de la aplicación sirve a múltiples clientes o "inquilinos" (tenants). Cada inquilino tiene sus propios datos aislados, configuraciones personalizadas y, a menudo, su propia URL o subdominio.

Como explica la [documentación oficial de django-tenants](https://django-tenants.readthedocs.io/en/latest/):

> "django-tenants is a Django application for managing multiple tenants on a single database instance using PostgreSQL schemas. A vital feature for Software-as-a-Service (SaaS) applications."

## Enfoques de Multitenancy

Existen varios enfoques para implementar multitenancy:

1. **Múltiples bases de datos**: Cada tenant tiene su propia base de datos física.
2. **Múltiples esquemas**: Todos los tenants comparten el mismo servidor de base de datos, pero cada uno tiene su propio esquema (implementación elegida).
3. **Tablas compartidas**: Todos los datos se almacenan en las mismas tablas, usando un campo discriminador para identificar a qué tenant pertenece cada registro.

## Esquemas en PostgreSQL

PostgreSQL ofrece una característica llamada "schemas" que permite dividir una base de datos en múltiples espacios de nombres. Como menciona la [documentación de PostgreSQL](https://www.postgresql.org/docs/current/ddl-schemas.html):

> "A schema is essentially a namespace: it contains named objects (tables, data types, functions, and operators) whose names can duplicate those of other objects existing in other schemas."

Esta característica es perfecta para implementar multitenancy, ya que:
- Proporciona aislamiento real de datos entre inquilinos
- Mantiene todas las ventajas de una única conexión a base de datos
- Permite compartir ciertos datos a través del esquema público

## Estructura y Responsabilidades en la Arquitectura Multitenant

### Responsabilidad de la App `tenants`

La app `tenants` es una pieza fundamental en la arquitectura multitenant y debe tener responsabilidades específicas y bien delimitadas:

1. **Gestión del ciclo de vida de los tenants**:
   - Creación de nuevos inquilinos y sus esquemas correspondientes
   - Activación, desactivación y eliminación de tenants
   - Administración de estados (activo, suspendido, en prueba, etc.)

2. **Gestión de dominios**:
   - Mapeo entre dominios/subdominios y los tenants
   - Validación de dominios y certificación de propiedad
   - Gestión de dominios primarios y secundarios

3. **Configuración específica de tenant**:
   - Almacenamiento de metadatos del tenant (nombre, información de contacto)
   - Configuración de planes y límites de suscripción
   - Preferencias y configuraciones a nivel de tenant

4. **Utilidades para multitenancy**:
   - Comandos de administración para operaciones en múltiples schemas
   - Helpers para cambiar entre contextos de schema
   - Herramientas para migraciones y mantenimiento

5. **Interfaces de administración**:
   - Panel admin para gestionar tenants
   - APIs para crear/modificar tenants y dominios
   - Herramientas de diagnóstico y monitoreo

Es crucial entender que la app `tenants` **NO** debe contener:
- Lógica de negocio específica de la aplicación
- Modelos relacionados con usuarios o autenticación
- Funcionalidades que pertenecen a la operativa del tenant

### Separación de Otras Funcionalidades

La gestión de usuarios, autenticación, y las funcionalidades específicas del negocio deben estar en apps separadas:

- **App de usuarios**: Maneja usuarios, roles, permisos, autenticación
- **Apps de dominio**: Contienen la lógica de negocio específica (productos, ventas, etc.)

### Ejemplo de Estructura de Proyecto

```
techstore/
├── apps/
│   ├── tenants/                  # Gestión de tenants (schema público)
│   │   ├── models.py             # Tenant, Domain
│   │   ├── admin.py              # Admin para gestionar tenants
│   │   └── management/           # Comandos para tenants
│   │
│   ├── users/                    # Gestión de usuarios (schema de tenant)
│   ├── products/                 # Gestión de productos (schema de tenant)
│   └── technical_service/        # Servicio técnico (schema de tenant)
│
└── techstore_api/                # Configuración del proyecto
    ├── settings.py               # Configuración multitenant
    ├── urls_public.py            # URLs para schema público
    └── urls_tenant.py            # URLs para schemas de tenant
```

## Django-Tenants: Implementación

Django-tenants utiliza esquemas de PostgreSQL para implementar multitenancy. Veamos los componentes clave:

### 1. Configuración de la Base de Datos

```python
DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": "techstore_db",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "db",
        "PORT": "5432",
    }
}
```

El backend `django_tenants.postgresql_backend` extiende el backend PostgreSQL estándar de Django para manejar múltiples esquemas. Cuando Django necesita acceder a datos, este backend se asegura de que las consultas se ejecuten en el esquema correcto.

### 2. Router de Base de Datos

```python
DATABASE_ROUTERS = ['django_tenants.routers.TenantSyncRouter']
```

El router `TenantSyncRouter` gestiona cómo se dirigen las consultas a los esquemas apropiados. Según la [documentación](https://django-tenants.readthedocs.io/en/latest/use.html#the-tenant-database-router):

> "The router ensures all queries to tenant-specific applications go to the tenant schema and all queries to shared applications go to the public schema."

### 3. Modelos Tenant y Domain

```python
TENANT_MODEL = 'tenants.Tenant'
TENANT_DOMAIN_MODEL = 'tenants.Domain'
```

Estos ajustes especifican los modelos que representan a los inquilinos y sus dominios asociados. Un ejemplo de estos modelos sería:

```python
class Tenant(TenantMixin):
    name = models.CharField(max_length=100)
    # Otros campos específicos del tenant

class Domain(DomainMixin):
    pass
```

Donde `TenantMixin` proporciona campos como `schema_name` y funcionalidad para crear y eliminar esquemas.

### 4. Aplicaciones Compartidas vs. Específicas

```python
SHARED_APPS = [
    'django_tenants',
    'apps.tenants',
    'django.contrib.admin',
    # ...
]

TENANT_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.admin',
    # ...
]

INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]
```

Esta configuración define:
- **SHARED_APPS**: Aplicaciones cuyos modelos existen en el esquema público, accesibles para todos los inquilinos
- **TENANT_APPS**: Aplicaciones cuyos modelos se crean en cada esquema de inquilino, con datos aislados
- **INSTALLED_APPS**: Combina ambas listas para que Django registre todas las aplicaciones

La [documentación](https://django-tenants.readthedocs.io/en/latest/install.html#apps-that-work-with-django-tenants) explica:

> "Any app can be either shared or tenant-specific. Django's auth works in both situations... Shared apps live in the 'public' schema and are available to all tenants. Tenant apps have one copy of their tables in each tenant's schema."

### 5. Middleware para Resolución de Tenant

```python
MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',
    # Otros middlewares...
]
```

El middleware `TenantMainMiddleware` se encarga de:
1. Identificar el tenant actual basado en el dominio de la solicitud
2. Establecer la conexión al esquema correspondiente
3. Hacer que el tenant sea accesible en el objeto request (`request.tenant`)

Es crucial que este middleware sea el primero, para asegurar que todas las operaciones de base de datos posteriores utilicen el esquema correcto.

### 6. Configuración de URLs

Creamos dos archivos:

- **urls_tenant.py**: Para rutas en esquemas de tenant
  ```python
  @api_view(["GET"])
  def tenant_api_root(request):
      tenant = request.tenant
      return Response({
          "message": f"API funcionando en tenant: {tenant.name}",
          # ...
      })
  ```

- **urls_public.py**: Para rutas en el esquema público
  ```python
  @api_view(["GET"])
  def public_api_root(request):
      return Response({
          "message": "API funcionando en esquema público",
          # ...
      })
  ```

En una implementación completa, configuraríamos:
```python
PUBLIC_SCHEMA_URLCONF = 'techstore_api.urls_public'
ROOT_URLCONF = 'techstore_api.urls_tenant'
```

Esto permite que cada tipo de esquema tenga su propio conjunto de URLs.

## Flujo de una Solicitud en un Sistema Multitenant

Cuando llega una solicitud al sistema:

1. **TenantMainMiddleware** intercepta la solicitud y examina el dominio (ejemplo: `tienda1.techstore.com`)
2. Busca en la tabla **Domain** para encontrar el tenant asociado a ese dominio
3. **Establece la conexión** al esquema correspondiente (ejemplo: `tienda1`)
4. Hace que el tenant sea accesible a través de `request.tenant`
5. El resto del procesamiento ocurre en el contexto de ese esquema
6. Las consultas a aplicaciones en TENANT_APPS utilizan el esquema del tenant
7. Las consultas a aplicaciones en SHARED_APPS utilizan el esquema público

## Ejemplos Prácticos

### Creación de un Nuevo Tenant

```python
from apps.tenants.models import Tenant, Domain

# Crear un nuevo tenant
tenant = Tenant(schema_name='tienda1', name='Tienda Ejemplo 1')
tenant.save()  # Esto crea automáticamente el esquema en PostgreSQL

# Asociar un dominio al tenant
domain = Domain(domain='tienda1.localhost', tenant=tenant, is_primary=True)
domain.save()
```

Cuando se crea un tenant, django-tenants ejecuta migraciones para todas las TENANT_APPS en el nuevo esquema.

### Consulta de Datos Específicos de Tenant

```python
# Dentro de una vista o función
def listar_productos(request):
    # request.tenant ya está configurado por TenantMainMiddleware
    # Las consultas usan automáticamente el esquema del tenant actual
    productos = Producto.objects.all()  # Solo muestra productos de este tenant
    return Response(ProductoSerializer(productos, many=True).data)
```

### Acceso a Datos en el Esquema Público

```python
from django_tenants.utils import schema_context

def obtener_informacion_tenant(request):
    tenant_actual = request.tenant
    
    # Para acceder a datos en el esquema público:
    with schema_context('public'):
        todos_los_tenants = Tenant.objects.all()
        # ...
    
    return Response(...)
```

El contexto `schema_context` permite cambiar temporalmente al esquema especificado.

## Ventajas y Consideraciones

### Ventajas
- **Aislamiento de datos**: Cada tenant tiene sus propios datos completamente separados
- **Seguridad**: Menor riesgo de filtración de datos entre tenants
- **Personalización**: Cada tenant puede tener su propia configuración
- **Eficiencia**: Todos los tenants comparten la misma instancia de la aplicación

### Consideraciones
- **Migraciones**: Se deben aplicar a todos los esquemas de tenant
- **Consultas entre esquemas**: Requieren manejo especial
- **Backup y restauración**: Más complejos que en una base de datos única

## Patrones de Uso Avanzados

### Comandos de Administración

Django-tenants proporciona una forma de ejecutar comandos de administración para todos los tenants o para un tenant específico:

```python
# Ejecutar un comando para todos los tenants
python manage.py tenant_command migrate

# Ejecutar un comando para un tenant específico
python manage.py tenant_command migrate --schema=tienda1
```

### Pruebas Específicas de Tenant

Para pruebas, django-tenants proporciona clases base específicas:

```python
from django_tenants.test.cases import TenantTestCase
from django_tenants.test.client import TenantClient

class ProductoTestCase(TenantTestCase):
    def setUp(self):
        self.client = TenantClient(self.tenant)
        # ...
    
    def test_listar_productos(self):
        response = self.client.get('/api/productos/')
        # ...
```

### Migraciones para Tenants Existentes

Cuando se añaden nuevas aplicaciones a TENANT_APPS, es necesario ejecutar migraciones para todos los tenants existentes:

```python
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
```

## Conclusión

La arquitectura multitenant con separación de esquemas PostgreSQL ofrece un balance excelente entre aislamiento de datos y eficiencia operativa. Django-tenants facilita la implementación de esta arquitectura, manejando automáticamente muchas de las complejidades asociadas.

Para un proyecto SaaS como TechStore, esta arquitectura permite que cada comercio técnico tenga su propio espacio de datos aislado dentro de una única aplicación compartida, cumpliendo con los requisitos de un sistema SaaS escalable y seguro.

## Referencias

- [Documentación oficial de django-tenants](https://django-tenants.readthedocs.io/en/latest/)
- [Documentación de PostgreSQL sobre esquemas](https://www.postgresql.org/docs/current/ddl-schemas.html)
- [Multitenancy en Django - Real Python](https://realpython.com/django-multi-tenant/)
- [Patrones de Arquitectura SaaS - Microsoft](https://docs.microsoft.com/es-es/azure/architecture/patterns/) 