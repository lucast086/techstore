#!/bin/bash

# Script para automatizar el build de Angular y la copia a Django
# Uso: ./build.sh [dev|prod]

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directorios del proyecto
PROJECT_ROOT="/workspace/techstore"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_DIR="$PROJECT_ROOT/backend"
STATIC_DIR="$BACKEND_DIR/static"
TEMPLATES_DIR="$BACKEND_DIR/templates"

# Verificar el entorno
ENV=${1:-"dev"}
BUILD_CONFIG=""

if [ "$ENV" = "prod" ]; then
    BUILD_CONFIG="--configuration production"
    echo -e "${YELLOW}Construyendo para PRODUCCIÓN${NC}"
else
    echo -e "${YELLOW}Construyendo para DESARROLLO${NC}"
fi

# Paso 1: Construir la aplicación Angular
echo -e "${GREEN}Paso 1: Construyendo aplicación Angular...${NC}"
cd "$FRONTEND_DIR" || exit 1
npm run build $BUILD_CONFIG

if [ $? -ne 0 ]; then
    echo "Error al construir la aplicación Angular"
    exit 1
fi

# Paso 2: Preparar directorios en Django
echo -e "${GREEN}Paso 2: Preparando directorios en Django...${NC}"
mkdir -p "$STATIC_DIR"
mkdir -p "$TEMPLATES_DIR"

# Paso 3: Copiar archivos a Django
echo -e "${GREEN}Paso 3: Copiando archivos a Django...${NC}"
# Copiar index.html al directorio de templates
cp "$FRONTEND_DIR/dist/frontend/index.html" "$TEMPLATES_DIR/"

# Copiar archivos estáticos (JS, CSS, assets) al directorio static
cp "$FRONTEND_DIR/dist/frontend"/*.js "$STATIC_DIR/"
cp "$FRONTEND_DIR/dist/frontend"/*.css "$STATIC_DIR/"
cp "$FRONTEND_DIR/dist/frontend/favicon.ico" "$STATIC_DIR/" 2>/dev/null || :

# Copiar directorio assets si existe
if [ -d "$FRONTEND_DIR/dist/frontend/assets" ]; then
    mkdir -p "$STATIC_DIR/assets"
    cp -r "$FRONTEND_DIR/dist/frontend/assets/"* "$STATIC_DIR/assets/" 2>/dev/null || :
fi

# Paso 4: Modificar index.html para usar rutas absolutas
echo -e "${GREEN}Paso 4: Actualizando rutas en index.html...${NC}"
sed -i 's/src="\([^"]*\.js\)"/src="\/static\/\1"/g' "$TEMPLATES_DIR/index.html"
sed -i 's/href="\([^"]*\.css\)"/href="\/static\/\1"/g' "$TEMPLATES_DIR/index.html"
sed -i 's/href="favicon.ico"/href="\/static\/favicon.ico"/g' "$TEMPLATES_DIR/index.html"

# Paso 5: Collectstatic en Django
echo -e "${GREEN}Paso 5: Ejecutando collectstatic en Django...${NC}"
cd "$BACKEND_DIR" || exit 1
python manage.py collectstatic --noinput

echo -e "${GREEN}¡Construcción completa!${NC}"
echo -e "Para ejecutar el servidor Django: cd $BACKEND_DIR && python manage.py runserver" 