ARG VARIANT=3.11
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

# Evitar mensajes de advertencia
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER root

# Instalar dependencias del sistema
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && apt-get -y install --no-install-recommends \
    build-essential \
    curl \
    git \
    zsh \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Instalar Node.js 16
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs

# Configurar zsh como shell predeterminado
RUN chsh -s /usr/bin/zsh root

# Instalar Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"

# Configurar Poetry para que no cree entornos virtuales dentro del contenedor
RUN poetry config virtualenvs.create false

# Instalar pre-commit y ruff globalmente
RUN pip install pre-commit ruff

# Preparar el directorio de trabajo
WORKDIR /workspace

# Script de inicialización para configurar pre-commit
COPY .devcontainer/init-dev.sh /usr/local/bin/init-dev.sh
RUN chmod +x /usr/local/bin/init-dev.sh
