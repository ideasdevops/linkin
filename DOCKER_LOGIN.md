# 🔐 Guía de Login en Docker - Link-IN

## Problema

En Docker, especialmente en modo headless, no es posible hacer login interactivo en LinkedIn porque el script no puede recibir entrada del usuario (`input()` no funciona).

## Soluciones

### Opción 1: Login Interactivo (Recomendado para primera vez)

Ejecuta el contenedor de forma interactiva para hacer el login inicial:

```bash
# 1. Detener el contenedor si está corriendo
docker-compose down

# 2. Ejecutar de forma interactiva (sin modo headless temporalmente)
docker-compose run --rm -it linkedin-leads bash

# 3. Dentro del contenedor, ejecutar el script
python3 main.py

# 4. El navegador se abrirá (si tienes X11 forwarding configurado)
# O modifica temporalmente main.py para desactivar headless

# 5. Inicia sesión en LinkedIn cuando se te solicite

# 6. Las cookies se guardarán automáticamente en /data/cookies/cookies.pkl
```

### Opción 2: Subir Cookies Manualmente

Si ya tienes cookies de LinkedIn desde otro lugar:

```bash
# 1. Exporta las cookies desde tu navegador (usando una extensión como "Cookie-Editor")

# 2. Convierte las cookies al formato pickle de Python
# Crea un script temporal:
cat > convert_cookies.py << 'EOF'
import pickle
import json

# Pega aquí tus cookies en formato JSON
cookies_json = [
    {"name": "li_at", "value": "tu_valor_aqui", "domain": ".linkedin.com", ...},
    # ... más cookies
]

# Guardar como pickle
with open('cookies.pkl', 'wb') as f:
    pickle.dump(cookies_json, f)
print("Cookies convertidas a cookies.pkl")
EOF

# 3. Copia el archivo al volumen
docker cp cookies.pkl linkin:/data/cookies/cookies.pkl
```

### Opción 3: Usar VNC/NoVNC para Login Visual

Configura un servidor VNC en el contenedor para ver el navegador:

```yaml
# Agregar al docker-compose.yml
services:
  linkedin-leads:
    # ... configuración existente
    environment:
      - DISPLAY=:1
    # Agregar servicio VNC
  vnc:
    image: dorowu/ubuntu-desktop-lxde-vnc
    ports:
      - "5900:5900"
```

### Opción 4: Modificar Temporalmente para Login

1. Edita `main.py` temporalmente para desactivar headless
2. Ejecuta el contenedor con acceso a display
3. Haz login
4. Restaura los cambios

## Verificar que las Cookies Están Guardadas

```bash
# Verificar que el archivo existe
docker exec linkin ls -la /data/cookies/

# Ver contenido (debería mostrar cookies.pkl)
docker exec linkin ls -la /data/cookies/cookies.pkl
```

## Una Vez que Tengas las Cookies

Una vez que las cookies estén en `/data/cookies/cookies.pkl`, el contenedor funcionará automáticamente sin necesidad de login interactivo.

## Nota Importante

El contenedor está configurado con `restart: on-failure`, lo que significa que:
- Si el script sale con código 0 (éxito), NO se reiniciará
- Si el script sale con código de error, SÍ se reiniciará
- Esto evita loops infinitos cuando no hay cookies

