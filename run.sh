#!/bin/bash

# Script para ejecutar Link-IN
# Uso: ./run.sh

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}[+] Link-IN${NC}"
echo ""

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}[!] No se encontró el entorno virtual. Creándolo...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[!] Error creando el entorno virtual${NC}"
        exit 1
    fi
    echo -e "${GREEN}[+] Entorno virtual creado${NC}"
fi

# Activar el entorno virtual
echo -e "${GREEN}[+] Activando entorno virtual...${NC}"
source venv/bin/activate

# Verificar si las dependencias están instaladas
if ! python3 -c "import selenium" 2>/dev/null; then
    echo -e "${YELLOW}[!] Instalando dependencias...${NC}"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}[!] Error instalando dependencias${NC}"
        exit 1
    fi
    echo -e "${GREEN}[+] Dependencias instaladas${NC}"
fi

# Verificar si la extensión está descomprimida
if [ ! -d "allforleads" ]; then
    if [ -f "allforleads.zip" ]; then
        echo -e "${YELLOW}[!] Descomprimiendo extensión...${NC}"
        unzip -q allforleads.zip
        echo -e "${GREEN}[+] Extensión descomprimida${NC}"
    else
        echo -e "${RED}[!] No se encontró allforleads.zip${NC}"
        exit 1
    fi
fi

# Ejecutar el script principal
echo -e "${GREEN}[+] Ejecutando script principal...${NC}"
echo ""
python3 main.py

