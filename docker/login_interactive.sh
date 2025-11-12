#!/bin/bash
# Script para hacer login interactivo en Docker
# Uso: docker-compose exec linkin bash /app/docker/login_interactive.sh

echo "[+] Link-IN - Login Interactivo en Docker"
echo "[+] Este script te permitirá hacer login en LinkedIn"
echo ""

# Verificar que estamos en Docker
if [ ! -f /.dockerenv ]; then
    echo "[!] Este script debe ejecutarse dentro del contenedor Docker"
    exit 1
fi

# Verificar que Chrome está disponible
if [ ! -f "$CHROME_BIN" ]; then
    echo "[!] Chrome no encontrado"
    exit 1
fi

echo "[+] Ejecutando script de login..."
echo "[+] NOTA: En modo headless, el login debe hacerse de otra forma"
echo "[+] Opción recomendada: Exportar cookies desde tu navegador local"
echo ""

# Ejecutar Python con modo no-headless temporal
python3 -c "
import os
os.environ['DISABLE_HEADLESS'] = 'true'
exec(open('/app/main.py').read())
"

