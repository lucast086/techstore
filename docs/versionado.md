# Guía de Versionado

Este proyecto sigue el [Versionado Semántico](https://semver.org/lang/es/) y utiliza un flujo de trabajo basado en Git Flow para gestionar el ciclo de vida del desarrollo.

## Versionado Semántico (SemVer)

Las versiones siguen el formato `X.Y.Z` donde:

- **X (Mayor)**: Cambios incompatibles con versiones anteriores
- **Y (Menor)**: Nuevas funcionalidades compatibles con versiones anteriores
- **Z (Parche)**: Correcciones de errores compatibles con versiones anteriores

## Flujo de Trabajo Git

El proyecto utiliza un flujo de trabajo basado en Git Flow con las siguientes ramas:

- **main**: Código en producción
- **develop**: Código en desarrollo activo
- **feature/xxx**: Nuevas funcionalidades
- **release/x.y.z**: Preparación para nuevas versiones
- **hotfix/x.y.z**: Correcciones urgentes para producción

## Script de Versionado

Hemos desarrollado un script para facilitar el manejo del versionado en `scripts/version.sh`:

```bash
# Inicializar el flujo de trabajo
./scripts/version.sh init

# Iniciar una nueva funcionalidad
./scripts/version.sh feature start auth-system

# Finalizar una funcionalidad
./scripts/version.sh feature finish auth-system

# Iniciar una versión
./scripts/version.sh release start 1.0.0

# Finalizar una versión
./scripts/version.sh release finish 1.0.0

# Iniciar un hotfix
./scripts/version.sh hotfix start 1.0.1

# Finalizar un hotfix
./scripts/version.sh hotfix finish 1.0.1

# Ver la versión actual
./scripts/version.sh current
```

## Convenciones de Commits

Para facilitar la generación automática de changelogs y la identificación de cambios, recomendamos seguir el formato de [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<ámbito>): <descripción>

[cuerpo opcional]

[pie opcional]
```

Donde `<tipo>` puede ser:

- **feat**: Nueva funcionalidad
- **fix**: Corrección de errores
- **docs**: Cambios en la documentación
- **style**: Cambios que no afectan al código (formato, espacios en blanco, etc.)
- **refactor**: Cambios en el código que no corrigen errores ni añaden funcionalidades
- **perf**: Cambios que mejoran el rendimiento
- **test**: Adición o corrección de pruebas
- **build**: Cambios en el sistema de build o dependencias externas
- **ci**: Cambios en la configuración de CI/CD
- **chore**: Otros cambios que no modifican archivos de código o pruebas

## Etiquetas (Tags)

Las etiquetas se crean automáticamente al finalizar una versión o un hotfix:

```bash
git tag -a v1.0.0 -m "Versión 1.0.0"
git push origin --tags
```

## Changelog

El historial de cambios se genera automáticamente basado en los commits convencionales y las etiquetas. 