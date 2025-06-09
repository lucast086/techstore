# Funcionalidades Pendientes

Este documento registra las funcionalidades que han sido identificadas como necesarias pero cuya implementación se ha decidido posponer para fases posteriores del desarrollo.

## Sistema de Usuarios

### Flujos de registro y onboarding
- Registro de usuarios con validación de email
- Verificación de email mediante token
- Recuperación de contraseñas
- Formularios de onboarding para completar perfil
- Captcha para prevenir registros automatizados

### Gestión avanzada de permisos
- Panel para que admin configure permisos personalizados por rol
- Grupos de usuarios con permisos específicos
- Registros de actividad de usuarios (logs)

### Autenticación avanzada
- Autenticación de dos factores (2FA)
- Login con proveedores externos (Google, Facebook, etc.)
- Detección de actividad sospechosa
- Bloqueo de cuentas después de intentos fallidos

## Mejoras de UX/UI

### Personalización de tenant
- Configuración de temas/colores por tenant
- Personalización de logo y assets visuales
- Configuración de emails personalizados

### Dashboard personalizable
- Widgets configurables por usuario
- Estadísticas y gráficos relevantes
- Personalización de vistas

## Funcionalidades Comerciales

### Sistema de notificaciones
- Notificaciones en tiempo real (WebSockets)
- Notificaciones por email configurables
- Centro de notificaciones para usuarios

### Reportes y analytics
- Reportes personalizados por tenant
- Exportación de datos en diferentes formatos
- Visualización avanzada de datos

## Infraestructura

### Optimizaciones de rendimiento
- Implementación de caching
- Optimización de consultas y modelos
- Compresión y optimización de assets

### Backup y recuperación
- Sistema automático de backups por tenant
- Herramientas de restauración para admin
- Exportación/importación de datos entre tenants 