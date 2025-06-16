# Tenant and User Management Guide

## Overview

TechStore uses django-tenants for multi-tenant architecture with schema separation. Each tenant (store) has its own PostgreSQL schema with isolated data.

## Tenant Management

### Creating the Public Tenant (Required First Step)
The public tenant is required for the system to work properly:

```bash
python manage.py init_public_tenant
```

This creates:
- Schema: `public`
- Domain: `localhost`
- Name: `TechStore`

### Creating a Test Tenant
For development and testing:

```bash
python manage.py create_test_tenant
```

This creates:
- Schema: `teststore`
- Domain: `teststore.localhost`
- Name: `TestStore`

### Creating Custom Tenants
You can create custom tenants programmatically:

```python
from tenants.models import Store, Domain

# Create the tenant
tenant = Store(
    schema_name='mystore',  # Must be lowercase, no spaces
    name='My Store',
    email='contact@mystore.com',
    is_active=True,
    on_trial=True,
)
tenant.save()

# Create the domain
domain = Domain(
    domain='mystore.localhost',  # For local development
    tenant=tenant,
    is_primary=True,
)
domain.save()
```

## User Management

### Creating Superusers

For multi-tenant apps, you need to specify which schema to create the user in:

```bash
# Create superuser in a specific tenant
python manage.py create_tenant_superuser --schema=teststore

# Interactive mode - will prompt for username, email, and password
python manage.py create_tenant_superuser --schema=teststore

# With parameters
python manage.py create_tenant_superuser --schema=teststore --username=admin --email=admin@teststore.com
```

### Setting Up Roles

Each tenant needs to have roles (groups) set up:

```bash
# Set up roles for a specific tenant
python manage.py tenant_command setup_roles --schema=teststore

# This creates three default roles:
# - Administrador (Administrator)
# - Vendedor (Salesperson)  
# - Técnico (Technician)
```

### Creating Regular Users

Regular users can be created through:

1. **Django Admin**: Access at `http://teststore.localhost:8000/admin`
2. **Programmatically**:

```python
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

# Create a user
user = User.objects.create_user(
    username='vendedor1',
    email='vendedor1@teststore.com',
    password='secure_password123',
    first_name='Juan',
    last_name='Pérez',
    phone='+1234567890'
)

# Assign a role
vendedor_group = Group.objects.get(name='Vendedor')
user.groups.add(vendedor_group)
```

## Accessing Different Tenants

### Local Development

1. **Public tenant**: `http://localhost:8000`
2. **Test tenant**: `http://teststore.localhost:8000`

### Adding Local Domain Resolution

Add to your `/etc/hosts` file (Linux/Mac) or `C:\Windows\System32\drivers\etc\hosts` (Windows):

```
127.0.0.1   localhost
127.0.0.1   teststore.localhost
```

### Production Setup

In production, you would use real domains:
- Public: `admin.techstore.com`
- Tenants: `storename.techstore.com`

## Common Commands

### Tenant-Specific Commands

Run any Django command for a specific tenant:

```bash
# Run migrations for a tenant
python manage.py migrate_schemas --schema=teststore

# Run any command for a tenant
python manage.py tenant_command <command_name> --schema=<schema_name>

# Examples:
python manage.py tenant_command shell --schema=teststore
python manage.py tenant_command dbshell --schema=teststore
```

### List All Tenants

```python
from tenants.models import Store

# List all tenants
for tenant in Store.objects.all():
    print(f"Schema: {tenant.schema_name}, Name: {tenant.name}")
```

## Troubleshooting

### Common Issues

1. **"relation does not exist" errors**: Run migrations for the schema
   ```bash
   python manage.py migrate_schemas --schema=<schema_name>
   ```

2. **Cannot access tenant domain**: Check your hosts file configuration

3. **Permission errors**: Ensure roles are set up for the tenant
   ```bash
   python manage.py tenant_command setup_roles --schema=<schema_name>
   ```

## Security Considerations

1. **Schema Isolation**: Each tenant's data is completely isolated
2. **Domain Validation**: Always validate tenant domains
3. **User Permissions**: Users exist per-tenant, not globally
4. **Superuser Access**: Superusers in one tenant cannot access other tenants 