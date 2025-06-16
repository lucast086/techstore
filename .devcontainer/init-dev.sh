#!/bin/bash
set -e

echo "🚀 Iniciando configuración del entorno de desarrollo..."

# # Marcar el directorio como seguro para Git (soluciona el problema de "dubious ownership")
echo "🔒 Configurando directorio como seguro para Git..."
git config --global --add safe.directory /workspace

# # Configurar Git con los datos del usuario
# echo "🔧 Configurando Git con información del usuario..."
# git config --global user.name "${GIT_AUTHOR_NAME}"
# git config --global user.email "${GIT_AUTHOR_EMAIL}"

# Verificar e instalar cliente PostgreSQL solo si no está instalado
if ! command -v psql &> /dev/null; then
  echo "📦 Instalando cliente PostgreSQL..."
  apt-get update
  apt-get install -y postgresql-client
else
  echo "✓ Cliente PostgreSQL ya está instalado."
fi

# Verificar si Angular CLI ya está instalado
if ! command -v ng &> /dev/null || ! ng version 2>/dev/null | grep -q "Angular CLI: 16"; then
  echo "📦 Instalando Angular CLI 16..."
  npm install -g @angular/cli@16
else
  echo "✓ Angular CLI 16 ya está instalado."
fi

# Instalar dependencias de Poetry solo si es necesario
if [ -f "techstore/pyproject.toml" ]; then
  if [ ! -d "techstore/.venv" ] || [ ! -f "techstore/poetry.lock" ]; then
    echo "📦 Instalando dependencias de Python con Poetry..."
    cd techstore
    # Eliminar poetry.lock si existe para asegurar que se genere correctamente
    rm -f poetry.lock
    # Generar lock file
    poetry lock
    # Instalar dependencias
    poetry install --no-root
    cd ..
  else
    echo "✓ Dependencias de Poetry ya están instaladas."
  fi
fi

# Instalar dependencias de backend específicas para PostgreSQL si no están instaladas
if [ -f "techstore/backend/pyproject.toml" ]; then
  cd techstore/backend
  if ! poetry show | grep -q "psycopg2-binary" || ! poetry show | grep -q "django-tenants"; then
    echo "📦 Instalando dependencias de PostgreSQL para el backend..."
    poetry add psycopg2-binary django-tenants
  else
    echo "✓ Dependencias de PostgreSQL para el backend ya están instaladas."
  fi
  cd ../..
fi

# Verificar si pre-commit está instalado
if ! command -v pre-commit &> /dev/null; then
  echo "🔧 Instalando pre-commit..."
  pip install pre-commit
else
  echo "✓ pre-commit ya está instalado."
fi

# Instalar pre-commit hooks si existe el archivo de configuración
if [ -f .pre-commit-config.yaml ]; then
  if ! grep -q "pre-commit" .git/hooks/pre-commit 2>/dev/null; then
    echo "🔧 Instalando pre-commit hooks..."
    pre-commit install
  else
    echo "✓ pre-commit hooks ya están instalados."
  fi
fi

# Verificar si se ha instalado correctamente
echo "✅ Verificando instalación de pre-commit..."
pre-commit --version

# Ejecutar pre-commit para todos los archivos
echo "🔍 Ejecutando pre-commit en todos los archivos..."
pre-commit run --all-files || true

# Esperar a que PostgreSQL esté disponible
echo "⏳ Esperando a que PostgreSQL esté disponible..."
timeout=60
elapsed=0
while ! PGPASSWORD=postgres psql -h db -U postgres -c '\q' 2>/dev/null; do
  if [ $elapsed -ge $timeout ]; then
    echo "❌ Tiempo de espera agotado para PostgreSQL. Verifica que el servicio esté funcionando."
    break
  fi
  echo "PostgreSQL no disponible todavía, esperando... ($elapsed/$timeout segundos)"
  sleep 2
  elapsed=$((elapsed+2))
done

if [ $elapsed -lt $timeout ]; then
  echo "✅ PostgreSQL está disponible y listo para usar."
fi

echo "✨ Entorno de desarrollo configurado correctamente."
echo "🐚 ZSH está instalado y configurado como shell predeterminado."
echo "🔧 Git configurado localmente para este proyecto."
echo "📱 Angular CLI instalado globalmente."
echo "📦 Dependencias de Python instaladas con Poetry."
echo "🐘 PostgreSQL configurado y disponible para la arquitectura multitenant."

echo "Configuración de desarrollo completada"
