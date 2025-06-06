#!/bin/bash
# Script para gestionar versiones siguiendo SemVer

# Asegurar que el directorio scripts existe
mkdir -p $(dirname "$0")

# Funciones de ayuda
function show_help {
  echo "Gestión de versiones con Git"
  echo ""
  echo "Uso:"
  echo "  $0 <comando> [argumentos]"
  echo ""
  echo "Comandos:"
  echo "  init                  - Inicializa la estructura de ramas para Git Flow"
  echo "  feature start <name>  - Inicia una nueva funcionalidad"
  echo "  feature finish <name> - Finaliza una funcionalidad y la integra en development"
  echo "  release start <version> - Inicia una nueva versión"
  echo "  release finish <version> - Finaliza una versión, crea tag y merge a main"
  echo "  hotfix start <version> - Inicia un hotfix desde main"
  echo "  hotfix finish <version> - Finaliza un hotfix, crea tag y merge a main/development"
  echo "  current               - Muestra la versión actual según los tags de Git"
  echo ""
  echo "Ejemplos:"
  echo "  $0 init"
  echo "  $0 feature start auth-system"
  echo "  $0 release start 1.0.0"
  echo "  $0 current"
}

function get_current_version {
  git describe --tags --abbrev=0 2>/dev/null || echo "0.0.0"
}

function init_git_flow {
  # Verificar si estamos en un repositorio Git
  if [ ! -d ".git" ]; then
    echo "❌ No estás en un repositorio Git. Ejecuta 'git init' primero."
    exit 1
  fi
  
  # Verificar rama actual
  current_branch=$(git branch --show-current)
  if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
    echo "⚠️ No estás en la rama main o master. Cambiando a main..."
    git checkout main 2>/dev/null || git checkout -b main
  fi
  
  # Crear rama development si no existe
  if ! git show-ref --verify --quiet refs/heads/development; then
    echo "🔄 Creando rama development..."
    git checkout -b development
    git push -u origin development
  else
    echo "✅ Rama development ya existe."
  fi
  
  echo "✨ Estructura de ramas inicializada correctamente."
}

function feature_start {
  feature_name=$1
  if [ -z "$feature_name" ]; then
    echo "❌ Debes especificar un nombre para la funcionalidad."
    exit 1
  fi
  
  git checkout development
  git pull origin development
  git checkout -b feature/$feature_name development
  echo "✨ Rama feature/$feature_name creada. Ahora puedes comenzar a trabajar en esta funcionalidad."
}

function feature_finish {
  feature_name=$1
  if [ -z "$feature_name" ]; then
    echo "❌ Debes especificar el nombre de la funcionalidad a finalizar."
    exit 1
  fi
  
  git checkout development
  git pull origin development
  git merge --no-ff feature/$feature_name -m "Merge feature/$feature_name into development"
  git push origin development
  echo "✨ Funcionalidad $feature_name integrada en development."
}

function release_start {
  version=$1
  if [ -z "$version" ]; then
    echo "❌ Debes especificar un número de versión (ej: 1.0.0)."
    exit 1
  fi
  
  git checkout development
  git pull origin development
  git checkout -b release/$version development
  git push -u origin release/$version
  echo "✨ Rama release/$version creada. Ahora puedes preparar esta versión para su lanzamiento."
}

function release_finish {
  version=$1
  if [ -z "$version" ]; then
    echo "❌ Debes especificar un número de versión (ej: 1.0.0)."
    exit 1
  fi
  
  # Merge a main
  git checkout main
  git pull origin main
  git merge --no-ff release/$version -m "Release $version"
  git tag -a v$version -m "Version $version"
  git push origin main
  git push origin --tags
  
  # Merge a development
  git checkout development
  git pull origin development
  git merge --no-ff release/$version -m "Merge release $version back to development"
  git push origin development
  
  echo "✨ Versión $version publicada correctamente."
}

function hotfix_start {
  version=$1
  if [ -z "$version" ]; then
    echo "❌ Debes especificar un número de versión para el hotfix (ej: 1.0.1)."
    exit 1
  fi
  
  git checkout main
  git pull origin main
  git checkout -b hotfix/$version main
  echo "✨ Rama hotfix/$version creada. Ahora puedes corregir el bug crítico."
}

function hotfix_finish {
  version=$1
  if [ -z "$version" ]; then
    echo "❌ Debes especificar un número de versión para el hotfix (ej: 1.0.1)."
    exit 1
  fi
  
  # Merge a main
  git checkout main
  git pull origin main
  git merge --no-ff hotfix/$version -m "Hotfix $version"
  git tag -a v$version -m "Version $version"
  git push origin main
  git push origin --tags
  
  # Merge a development
  git checkout development
  git pull origin development
  git merge --no-ff hotfix/$version -m "Merge hotfix $version back to development"
  git push origin development
  
  echo "✨ Hotfix $version publicado correctamente."
}

# Verificar argumentos
if [ $# -lt 1 ]; then
  show_help
  exit 0
fi

# Procesar comandos
case "$1" in
  init)
    init_git_flow
    ;;
  feature)
    if [ "$2" = "start" ] && [ ! -z "$3" ]; then
      feature_start "$3"
    elif [ "$2" = "finish" ] && [ ! -z "$3" ]; then
      feature_finish "$3"
    else
      echo "❌ Comando incorrecto. Usa 'feature start <name>' o 'feature finish <name>'."
    fi
    ;;
  release)
    if [ "$2" = "start" ] && [ ! -z "$3" ]; then
      release_start "$3"
    elif [ "$2" = "finish" ] && [ ! -z "$3" ]; then
      release_finish "$3"
    else
      echo "❌ Comando incorrecto. Usa 'release start <version>' o 'release finish <version>'."
    fi
    ;;
  hotfix)
    if [ "$2" = "start" ] && [ ! -z "$3" ]; then
      hotfix_start "$3"
    elif [ "$2" = "finish" ] && [ ! -z "$3" ]; then
      hotfix_finish "$3"
    else
      echo "❌ Comando incorrecto. Usa 'hotfix start <version>' o 'hotfix finish <version>'."
    fi
    ;;
  current)
    echo "Versión actual: $(get_current_version)"
    ;;
  *)
    show_help
    ;;
esac 