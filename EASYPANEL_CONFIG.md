# 🚀 Configuración Easypanel - Link-IN

## 📋 Variables de Entorno

### Variables Requeridas

Ninguna variable es estrictamente requerida, pero se recomienda configurar al menos las keywords.

### Variables Opcionales

| Variable | Descripción | Valor por Defecto | Ejemplo |
|----------|-------------|-------------------|---------|
| `GMAIL_APP_PASSWORD` | Contraseña de aplicación de Gmail para envío de emails | (vacío) | `abcd efgh ijkl mnop` |
| `LINKEDIN_KEYWORDS` | Keywords para búsqueda en LinkedIn (separadas por comas) | `real estate` | `real estate,software engineer,marketing manager` |
| `PYTHONUNBUFFERED` | Salida sin buffer de Python (recomendado) | `1` | `1` |
| `DOCKER_CONTAINER` | Indicador de que está en Docker | `true` | `true` |

### Configuración en Easypanel

1. Ve a la sección **Environment Variables** de tu aplicación
2. Agrega las siguientes variables:

```
GMAIL_APP_PASSWORD=tu_contraseña_de_aplicación_aquí
LINKEDIN_KEYWORDS=real estate,software engineer
PYTHONUNBUFFERED=1
DOCKER_CONTAINER=true
```

**Nota sobre GMAIL_APP_PASSWORD:**
- Si no configuras esta variable, el sistema funcionará pero NO enviará emails
- Solo extraerá y guardará los datos en el CSV
- Para obtener la contraseña: https://myaccount.google.com/apppasswords

**Nota sobre LINKEDIN_KEYWORDS:**
- Puedes usar múltiples keywords separadas por comas
- Ejemplo: `real estate,software engineer,marketing manager,CEO`
- El sistema procesará cada keyword secuencialmente

---

## 💾 Volúmenes (Persistent Storage)

### Volúmenes Requeridos

Necesitas crear **3 volúmenes** para persistir los datos:

#### 1. Volumen de Cookies (`/data/cookies`)
- **Path en contenedor**: `/data/cookies`
- **Propósito**: Guardar la sesión de LinkedIn (cookies.pkl)
- **Tamaño recomendado**: 10 MB
- **Importante**: Sin este volumen, tendrás que iniciar sesión cada vez que se reinicie el contenedor

#### 2. Volumen de Output (`/data/output`)
- **Path en contenedor**: `/data/output`
- **Propósito**: Guardar los archivos CSV con los leads extraídos
- **Tamaño recomendado**: 100 MB - 1 GB (depende de cuántos leads extraigas)
- **Archivos generados**: `output.csv`

#### 3. Volumen de Logs (`/data/logs`)
- **Path en contenedor**: `/data/logs`
- **Propósito**: Guardar logs de la aplicación
- **Tamaño recomendado**: 50 MB
- **Opcional**: Puede omitirse si no necesitas logs persistentes

### Configuración en Easypanel

1. Ve a la sección **Volumes** o **Persistent Storage** de tu aplicación
2. Crea los siguientes volúmenes:

| Nombre del Volumen | Mount Path | Tamaño |
|-------------------|------------|--------|
| `linkedin-cookies` | `/data/cookies` | 10 MB |
| `linkedin-output` | `/data/output` | 1 GB |
| `linkedin-logs` | `/data/logs` | 50 MB |

### Estructura de Directorios en el Contenedor

```
/data/
├── cookies/
│   └── cookies.pkl          # Sesión de LinkedIn
├── output/
│   └── output.csv           # Leads extraídos
└── logs/
    └── *.log                # Logs de la aplicación
```

---

## 🔧 Configuración Adicional en Easypanel

### Recursos del Contenedor

- **RAM mínima**: 2 GB
- **RAM recomendada**: 4 GB
- **CPU**: 1-2 cores
- **Shared Memory (shm_size)**: 2 GB (importante para Chrome)

### Healthcheck

Easypanel puede configurar un healthcheck automático. El contenedor incluye un healthcheck que verifica la existencia del archivo CSV:

```yaml
healthcheck:
  test: ["CMD", "python3", "-c", "import os; exit(0 if os.path.exists('/data/output/output.csv') else 1)"]
  interval: 60s
  timeout: 10s
  retries: 3
  start_period: 120s
```

### Puerto

**No se requiere puerto** - Esta aplicación no expone ningún servicio HTTP. Es un script que se ejecuta y procesa datos.

---

## 📝 Checklist de Configuración en Easypanel

- [ ] Variables de entorno configuradas:
  - [ ] `LINKEDIN_KEYWORDS` (recomendado)
  - [ ] `GMAIL_APP_PASSWORD` (opcional)
  - [ ] `PYTHONUNBUFFERED=1`
  - [ ] `DOCKER_CONTAINER=true`
- [ ] Volúmenes creados y montados:
  - [ ] `/data/cookies` → `linkedin-cookies`
  - [ ] `/data/output` → `linkedin-output`
  - [ ] `/data/logs` → `linkedin-logs`
- [ ] Recursos asignados:
  - [ ] RAM: mínimo 2 GB
  - [ ] Shared Memory: 2 GB
- [ ] Healthcheck configurado (opcional)

---

## 🚀 Comandos Útiles en Easypanel

### Ver logs en tiempo real
```bash
# Desde la terminal de Easypanel o SSH
docker logs -f linkin
```

### Acceder al contenedor
```bash
docker exec -it linkin bash
```

### Ver archivos CSV generados
```bash
docker exec linkin cat /data/output/output.csv
```

### Descargar CSV
```bash
# Desde Easypanel, usa la función de descarga de volúmenes
# O desde SSH:
docker cp linkin:/data/output/output.csv ./output.csv
```

---

## ⚠️ Notas Importantes

1. **Primera ejecución**: El sistema necesitará que inicies sesión en LinkedIn. Esto se hace a través de los logs o ejecutando el contenedor de forma interactiva.

2. **Modo Headless**: En Docker, Chrome se ejecuta en modo headless (sin interfaz gráfica). Esto es normal y necesario.

3. **Persistencia**: Los datos se guardan en volúmenes, por lo que persisten entre reinicios.

4. **Rate Limiting**: LinkedIn puede limitar tu cuenta si haces demasiadas búsquedas muy rápido. El sistema incluye delays, pero ten cuidado.

5. **Cookies**: El archivo de cookies contiene tu sesión de LinkedIn. Mantén el volumen seguro.

---

## 🔍 Verificación Post-Despliegue

1. Verifica que el contenedor está corriendo:
   ```bash
   docker ps | grep linkin
   ```

2. Verifica que los volúmenes están montados:
   ```bash
   docker inspect linkin | grep -A 10 Mounts
   ```

3. Verifica que las variables de entorno están configuradas:
   ```bash
   docker exec linkin env | grep -E "LINKEDIN|GMAIL|PYTHON"
   ```

4. Verifica que los directorios existen:
   ```bash
   docker exec linkin ls -la /data/
   ```

---

## 📞 Soporte

Si tienes problemas con la configuración:
1. Revisa los logs: `docker logs linkin`
2. Verifica que los volúmenes están montados correctamente
3. Verifica que las variables de entorno están configuradas
4. Asegúrate de que el contenedor tiene suficientes recursos (RAM, CPU)

