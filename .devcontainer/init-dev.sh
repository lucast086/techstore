#!/bin/bash
set -e

echo "🚀 Iniciando configuración del entorno de desarrollo..."

# Marcar el directorio como seguro para Git (soluciona el problema de "dubious ownership")
echo "🔒 Configurando directorio como seguro para Git..."
git config --global --add safe.directory /workspace

# Verificar si el repositorio está inicializado
if [ ! -d ".git" ]; then
  echo "🔄 Inicializando repositorio Git..."
  git init
  # Asegurar que estamos dentro del repositorio Git antes de configurar
  cd /workspace
fi

# Verificar que estamos en un repositorio Git antes de configurar
if [ -d ".git" ]; then
  # Configurar Git localmente
  echo "📝 Configurando Git para este proyecto..."
  git config --local user.name "${GIT_AUTHOR_NAME:-lucast086}"
  git config --local user.email "${GIT_AUTHOR_EMAIL:-turlettilucasdev@gmail.com}"
else
  echo "⚠️ No se pudo configurar Git localmente. Directorio .git no encontrado."
fi

# Instalar dependencias globales de Angular
echo "📦 Instalando Angular CLI 16..."
npm install -g @angular/cli@16

# Instalar dependencias de Poetry
if [ -f "techstore/pyproject.toml" ]; then
  echo "📦 Instalando dependencias de Python con Poetry..."
  cd techstore
  # Eliminar poetry.lock si existe para asegurar que se genere correctamente
  rm -f poetry.lock
  # Generar lock file
  poetry lock
  # Instalar dependencias
  poetry install --no-root
  cd ..
fi

# Instalar pre-commit hooks si existe el archivo de configuración
if [ -f .pre-commit-config.yaml ]; then
    echo "🔧 Instalando pre-commit hooks..."
    pre-commit install
fi

# Verificar si se ha instalado correctamente
echo "✅ Verificando instalación de pre-commit..."
pre-commit --version

# Ejecutar pre-commit para todos los archivos
echo "🔍 Ejecutando pre-commit en todos los archivos..."
pre-commit run --all-files || true

echo "✨ Entorno de desarrollo configurado correctamente."
echo "🐚 ZSH está instalado y configurado como shell predeterminado."
echo "🔧 Git configurado localmente para este proyecto."
echo "📱 Angular CLI 16 instalado globalmente."
echo "📦 Dependencias de Python instaladas con Poetry."
echo "👉 Puedes iniciar el servidor backend con: cd techstore/backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "👉 Puedes iniciar el servidor frontend con: cd techstore/frontend && ng serve --host 0.0.0.0"

echo "Configuración de desarrollo completada" 