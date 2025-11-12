# 🍪 Guía de Configuración de Cookies para Link-IN

## Método Rápido: Usar Archivo JSON

### Paso 1: Exportar Cookies desde tu Navegador

1. **Instala una extensión de cookies:**
   - Chrome: [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
   - Firefox: [Cookie-Editor](https://addons.mozilla.org/firefox/addon/cookie-editor/)

2. **Exporta las cookies de LinkedIn:**
   - Ve a https://www.linkedin.com
   - Inicia sesión normalmente
   - Abre la extensión Cookie-Editor
   - Haz clic en "Export" → "Export as JSON"
   - Guarda el archivo (ej: `www.linkedin.com_json_sumpetrol.json`)

### Paso 2: Colocar el Archivo JSON

**Opción A: Local (desarrollo)**
```bash
# Coloca el archivo JSON en la carpeta cookies/
mkdir -p cookies
cp tu_archivo.json cookies/www.linkedin.com_json_sumpetrol.json
```

**Opción B: Docker (producción)**
```bash
# Copia el archivo al volumen de Docker
docker cp cookies/www.linkedin.com_json_sumpetrol.json linkin:/data/cookies/

# O monta la carpeta local en docker-compose.yml:
volumes:
  - ./cookies:/data/cookies:ro
```

### Paso 3: Conversión Automática

El sistema **convertirá automáticamente** el JSON a pickle cuando ejecutes el script. No necesitas hacer nada más.

Si quieres convertir manualmente:
```bash
python3 convert_cookies.py cookies/www.linkedin.com_json_sumpetrol.json cookies/cookies.pkl
```

## Método Manual: Convertir JSON a Pickle

Si prefieres convertir manualmente antes de ejecutar:

```bash
# Activa el entorno virtual (si estás en local)
source venv/bin/activate

# Convierte el JSON a pickle
python3 convert_cookies.py cookies/www.linkedin.com_json_sumpetrol.json

# El archivo cookies.pkl se creará automáticamente
```

## Verificar que Funciona

### En Local:
```bash
./run.sh
# Deberías ver:
# [+] Encontrado archivo JSON de cookies: www.linkedin.com_json_sumpetrol.json
# [+] Convirtiendo 22 cookies de JSON a pickle...
# [+] ✅ Cookies convertidas y guardadas
```

### En Docker:
```bash
docker-compose logs -f linkin
# Deberías ver:
# [+] Encontrado archivo JSON de cookies: www.linkedin.com_json_sumpetrol.json
# [+] Convirtiendo 22 cookies de JSON a pickle...
# [+] ✅ Cookies convertidas y guardadas
```

## Estructura de Carpetas

```
linkin/
├── cookies/                          # Carpeta de cookies (local)
│   ├── www.linkedin.com_json_sumpetrol.json  # JSON exportado
│   └── cookies.pkl                   # Pickle generado (opcional)
├── convert_cookies.py                # Script de conversión
└── main.py                           # Detecta y convierte automáticamente
```

En Docker:
```
/data/cookies/                        # Volumen persistente
├── www.linkedin.com_json_sumpetrol.json
└── cookies.pkl
```

## Cookies Importantes

El sistema verifica que existan estas cookies importantes:
- `li_at` - Token de autenticación principal
- `JSESSIONID` - ID de sesión
- `li_rm` - Cookie de "recordarme"

Si faltan, verás una advertencia pero el sistema intentará funcionar igual.

## Solución de Problemas

### Error: "No se encontró formato de cookies reconocido"
- Verifica que el JSON tenga un array de cookies o un objeto con campo `cookies`
- El formato debe ser compatible con Cookie-Editor

### Error: "No se encontraron cookies importantes"
- Asegúrate de exportar las cookies mientras estás **logueado** en LinkedIn
- Las cookies deben incluir `li_at` para autenticación

### Las cookies expiran
- Las cookies de LinkedIn suelen durar varios meses
- Si expiran, simplemente exporta nuevas cookies y reemplaza el archivo JSON

## Seguridad

⚠️ **IMPORTANTE:**
- Las cookies contienen tu sesión de LinkedIn
- No compartas estos archivos
- No los subas a repositorios públicos
- Mantén los volúmenes de Docker seguros

## Actualizar Cookies

Cuando necesites actualizar las cookies:

1. Exporta nuevas cookies desde tu navegador
2. Reemplaza el archivo JSON en `cookies/`
3. Elimina el archivo `cookies.pkl` (si existe) para forzar reconversión
4. Reinicia el contenedor/aplicación

