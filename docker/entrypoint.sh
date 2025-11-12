#!/bin/bash
set -e

echo "[+] LinkedIn Leads Generation - Docker Entrypoint"
echo "[+] Inicializando contenedor..."

# Verificar que Chrome está instalado
if [ ! -f "$CHROME_BIN" ]; then
    echo "[!] Error: Chrome no encontrado en $CHROME_BIN"
    exit 1
fi

echo "[+] Chrome encontrado: $CHROME_BIN"

# Verificar que los directorios de datos existen
mkdir -p /data/cookies
mkdir -p /data/output
mkdir -p /data/logs

echo "[+] Directorios de datos creados"

# Configurar permisos
chmod -R 755 /data

# Verificar que la extensión existe (si está configurada)
if [ -d "/app/allforleads" ]; then
    echo "[+] Extensión AllForLeads encontrada"
else
    echo "[!] Advertencia: Extensión AllForLeads no encontrada"
fi

# Mostrar configuración
echo "[+] Configuración:"
echo "    - DISPLAY: ${DISPLAY:-:99}"
echo "    - CHROME_BIN: ${CHROME_BIN}"
echo "    - Keywords: ${LINKEDIN_KEYWORDS:-real estate}"
echo "    - Gmail configurado: $([ -n "$GMAIL_APP_PASSWORD" ] && echo "Sí" || echo "No")"

# Ejecutar el comando pasado como argumento
echo "[+] Ejecutando aplicación..."
exec "$@"

