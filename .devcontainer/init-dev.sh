#!/bin/bash
set -e

echo "🚀 Iniciando configuración del entorno FastAPI + HTMX..."

# Marcar el directorio como seguro para Git
echo "🔒 Configurando directorio como seguro para Git..."
git config --global --add safe.directory /workspace

# Verificar e instalar cliente PostgreSQL
if ! command -v psql &> /dev/null; then
  echo "📦 Instalando cliente PostgreSQL..."
  sudo apt-get update
  sudo apt-get install -y postgresql-client
else
  echo "✓ Cliente PostgreSQL ya está instalado."
fi

# Instalar dependencias Python con Poetry
echo "📦 Instalando dependencias de Python con Poetry..."
if [ -f pyproject.toml ]; then
  sudo poetry install
  echo "✓ Dependencias de Python instaladas."
else
  echo "⚠️ No se encontró pyproject.toml"
fi

# Instalar pre-commit hooks si existe configuración
if [ -f .pre-commit-config.yaml ]; then
  echo "🔧 Instalando pre-commit hooks..."
  sudo poetry run pre-commit install
  echo "✓ pre-commit hooks instalados."
fi

# Esperar a que PostgreSQL esté disponible
echo "⏳ Esperando a que PostgreSQL esté disponible..."
timeout=60
elapsed=0
while ! PGPASSWORD=postgres psql -h db -U postgres -c '\q' 2>/dev/null; do
  if [ $elapsed -ge $timeout ]; then
    echo "❌ Tiempo de espera agotado para PostgreSQL."
    break
  fi
  echo "PostgreSQL no disponible, esperando... ($elapsed/$timeout s)"
  sleep 2
  elapsed=$((elapsed+2))
done

if [ $elapsed -lt $timeout ]; then
  echo "✅ PostgreSQL disponible."
  
  # Crear base de datos si no existe
  echo "🗄️ Verificando base de datos..."
  PGPASSWORD=postgres psql -h db -U postgres -c "CREATE DATABASE techstore_db;" 2>/dev/null || echo "✓ Base de datos ya existe."
fi

# Verificar instalaciones
echo "🔍 Verificando instalaciones..."
echo "FastAPI: $(poetry run python -c 'import fastapi; print(fastapi.__version__)' 2>/dev/null || echo 'No instalado')"
echo "SQLAlchemy: $(poetry run python -c 'import sqlalchemy; print(sqlalchemy.__version__)' 2>/dev/null || echo 'No instalado')"
echo "Alembic: $(poetry run alembic --version 2>/dev/null || echo 'No instalado')"

echo "✨ Entorno FastAPI + HTMX configurado correctamente."
echo "🚀 Listo para desarrollar con FastAPI, PostgreSQL y HTMX!"
