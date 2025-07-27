# Imagen base con Python 3.11
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/workspace

# Instalar dependencias del sistema para desarrollo
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    zsh \
    sudo \
    vim \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Instalar Node.js 18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Crear usuario developer con sudo
RUN groupadd --gid 1000 developer \
    && useradd --uid 1000 --gid 1000 -m developer \
    && echo developer ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/developer \
    && chmod 0440 /etc/sudoers.d/developer

# Configurar zsh para developer
RUN chsh -s /usr/bin/zsh developer

# Instalar Poetry globalmente
RUN pip install poetry==1.7.1

# Configurar Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Configurar directorio de trabajo
WORKDIR /workspace

# Instalar Claude Code globalmente
RUN npm install -g @anthropic-ai/claude-code

# Cambiar a usuario developer
USER developer

# Preparar el directorio de trabajo
WORKDIR /workspace

# Script de inicialización para configurar pre-commit
COPY .devcontainer/init-dev.sh /scripts/init-dev.sh
RUN chmod +x /scripts/init-dev.sh
