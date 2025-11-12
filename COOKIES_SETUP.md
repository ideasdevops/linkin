# 🍪 Configuración de Cookies para Link-IN en Docker

## Problema

En Docker (modo headless), no es posible hacer login interactivo. El contenedor necesita las cookies de LinkedIn para funcionar.

## Solución Rápida: Exportar Cookies desde tu Navegador

### Paso 1: Exportar Cookies desde Chrome/Firefox

1. **Instala una extensión de cookies:**
   - Chrome: "Cookie-Editor" o "EditThisCookie"
   - Firefox: "Cookie-Editor"

2. **Exporta las cookies de LinkedIn:**
   - Ve a https://www.linkedin.com
   - Inicia sesión normalmente
   - Abre la extensión de cookies
   - Exporta las cookies en formato JSON

3. **Convierte a formato pickle:**

Crea un archivo `convert_cookies.py`:

```python
import pickle
import json

# Pega aquí tus cookies exportadas
cookies_json = [
    {
        "name": "li_at",
        "value": "tu_valor_aqui",
        "domain": ".linkedin.com",
        "path": "/",
        "secure": True,
        "httpOnly": True,
        "sameSite": "None"
    },
    # ... más cookies (li_rm, JSESSIONID, etc.)
]

# Guardar como pickle
with open('cookies.pkl', 'wb') as f:
    pickle.dump(cookies_json, f)
print("✅ Cookies convertidas a cookies.pkl")
```

Ejecuta:
```bash
python3 convert_cookies.py
```

### Paso 2: Subir Cookies al Contenedor

```bash
# Opción A: Si el contenedor está corriendo
docker cp cookies.pkl linkin:/data/cookies/cookies.pkl

# Opción B: Montar el archivo directamente
# Edita docker-compose.yml y agrega:
volumes:
  - ./cookies.pkl:/data/cookies/cookies.pkl:ro
```

### Paso 3: Reiniciar el Contenedor

```bash
docker-compose restart linkin
```

## Solución Alternativa: Login con VNC (Más Complejo)

Si necesitas ver el navegador para hacer login:

1. Agrega un servicio VNC al `docker-compose.yml`
2. Conéctate via VNC
3. Haz login visualmente
4. Las cookies se guardarán automáticamente

## Verificar que Funciona

```bash
# Ver logs
docker-compose logs -f linkin

# Deberías ver:
# [+] Cookies cargadas exitosamente
# [+] Navegando a LinkedIn...
```

## Cookies Importantes de LinkedIn

Las cookies más importantes son:
- `li_at` - Token de autenticación principal
- `JSESSIONID` - ID de sesión
- `li_rm` - Cookie de recordarme

## Nota de Seguridad

⚠️ **Las cookies contienen tu sesión de LinkedIn. Mantén el volumen seguro y no las compartas.**

