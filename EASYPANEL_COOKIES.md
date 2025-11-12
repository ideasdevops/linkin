# 🍪 Configuración de Cookies en Easypanel

## Problema Actual

El contenedor está en standby porque no encuentra las cookies. El archivo JSON está en GitHub, pero necesita estar en el **volumen persistente** de Docker.

## Solución: Copiar Cookies al Volumen

### Opción 1: Usar la Interfaz de Easypanel (Recomendado)

1. **Ve a tu proyecto en Easypanel**
2. **Abre el servicio `linkin`**
3. **Ve a la pestaña "Volumes" o "Storage"**
4. **Busca el volumen `linkin-cookies`** (o el nombre que hayas configurado)
5. **Sube el archivo JSON:**
   - Descarga el archivo desde GitHub: `cookies/www.linkedin.com_json_sumpetrol.json`
   - O exporta nuevas cookies desde tu navegador
   - Sube el archivo al volumen en la ruta: `/data/cookies/`

### Opción 2: Usar SSH/Shell de Easypanel

Si Easypanel tiene acceso SSH o shell:

```bash
# 1. Conecta al servidor donde está el contenedor
ssh tu-usuario@tu-servidor

# 2. Encuentra el volumen de Docker
docker volume ls | grep linkin-cookies

# 3. Copia el archivo al volumen
# Opción A: Si tienes el archivo localmente
docker cp cookies/www.linkedin.com_json_sumpetrol.json linkin:/data/cookies/

# Opción B: Si necesitas descargarlo desde GitHub
docker exec linkin mkdir -p /data/cookies
docker exec linkin wget -O /data/cookies/www.linkedin.com_json_sumpetrol.json \
  https://raw.githubusercontent.com/ideasdevops/linkin/main/cookies/www.linkedin.com_json_sumpetrol.json
```

### Opción 3: Montar el Archivo desde el Código (Temporal)

Modifica `docker-compose.yml` o la configuración en Easypanel para montar la carpeta `cookies`:

```yaml
volumes:
  - linkin_cookies:/data/cookies
  - ./cookies:/app/cookies:ro  # Montar desde código (solo lectura)
```

**Nota:** Esta opción copia el archivo desde el código al volumen la primera vez.

## Verificar que Funciona

Después de copiar el archivo, verifica:

```bash
# Ver logs del contenedor
docker logs linkin -f

# Deberías ver:
# [+] Encontrado archivo JSON de cookies: www.linkedin.com_json_sumpetrol.json
# [+] Convirtiendo 22 cookies de JSON a pickle...
# [+] ✅ Cookies convertidas y guardadas en /data/cookies/cookies.pkl
```

## Estructura Esperada en el Volumen

```
/data/cookies/
├── www.linkedin.com_json_sumpetrol.json  # Archivo JSON (se convertirá automáticamente)
└── cookies.pkl                            # Archivo pickle (generado automáticamente)
```

## Reiniciar el Contenedor

Después de copiar el archivo:

1. **En Easypanel:** Haz clic en "Restart" o "Redeploy"
2. **O desde terminal:**
   ```bash
   docker restart linkin
   ```

## Solución Automática (Futura)

El código ahora busca cookies en múltiples ubicaciones:
1. `/data/cookies/` (volumen persistente) - **Prioridad 1**
2. `/app/cookies/` (código fuente) - **Prioridad 2** (si el volumen está vacío)

Esto significa que si el archivo JSON está en el código, se copiará automáticamente al volumen la primera vez.

## Exportar Nuevas Cookies

Si necesitas actualizar las cookies:

1. **Exporta desde tu navegador:**
   - Instala extensión "Cookie-Editor"
   - Ve a LinkedIn e inicia sesión
   - Exporta cookies como JSON

2. **Sube al volumen:**
   - Reemplaza el archivo JSON en `/data/cookies/`
   - Elimina `cookies.pkl` si existe (para forzar reconversión)
   - Reinicia el contenedor

## Troubleshooting

### Error: "No se encontró archivo de cookies"
- Verifica que el archivo JSON esté en `/data/cookies/`
- Verifica permisos del volumen
- Revisa los logs: `docker logs linkin`

### Error: "Formato de JSON no reconocido"
- Asegúrate de exportar en formato JSON desde Cookie-Editor
- Verifica que el archivo no esté corrupto

### El contenedor sigue en standby
- Verifica que el archivo JSON tenga el formato correcto
- Revisa los logs completos
- Asegúrate de que el volumen esté montado correctamente

