# 🐳 Docker Deployment - LinkedIn Leads Generation

## 📋 Requisitos

- Docker Engine 20.10+
- Docker Compose 2.0+
- Al menos 2GB de RAM disponible
- Conexión a Internet

## 🚀 Inicio Rápido

### 1. Construir la imagen

```bash
docker-compose build
```

### 2. Configurar variables de entorno (Opcional)

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Gmail para envío de emails (opcional)
GMAIL_APP_PASSWORD=tu_contraseña_de_aplicación

# Keywords para búsqueda en LinkedIn (separadas por comas)
LINKEDIN_KEYWORDS=real estate,software engineer,marketing manager
```

### 3. Ejecutar el contenedor

```bash
docker-compose up -d
```

### 4. Ver logs

```bash
docker-compose logs -f
```

## 📁 Estructura de Datos Persistentes

Los datos se guardan en volúmenes de Docker:

- **Cookies**: `/data/cookies/cookies.pkl` - Sesión de LinkedIn
- **Output CSV**: `/data/output/output.csv` - Leads extraídos
- **Logs**: `/data/logs/` - Archivos de log

### Acceder a los datos

```bash
# Ver el CSV de salida
docker-compose exec linkedin-leads cat /data/output/output.csv

# Copiar el CSV al host
docker cp linkedin-leads-generation:/data/output/output.csv ./output.csv

# Ver logs
docker-compose logs linkedin-leads
```

## ⚙️ Configuración

### Variables de Entorno

| Variable | Descripción | Default | Requerido |
|----------|-------------|---------|-----------|
| `GMAIL_APP_PASSWORD` | Contraseña de aplicación de Gmail | - | No |
| `LINKEDIN_KEYWORDS` | Keywords separadas por comas | `real estate` | No |
| `PYTHONUNBUFFERED` | Salida sin buffer de Python | `1` | No |

### Modificar keywords

Edita el archivo `.env` o usa variables de entorno:

```bash
LINKEDIN_KEYWORDS="real estate,software engineer" docker-compose up
```

## 🔧 Comandos Útiles

### Ejecutar manualmente

```bash
# Ejecutar el script manualmente
docker-compose exec linkedin-leads python3 main.py

# Acceder al shell del contenedor
docker-compose exec linkedin-leads bash
```

### Reiniciar el contenedor

```bash
docker-compose restart
```

### Detener y eliminar

```bash
# Detener
docker-compose down

# Detener y eliminar volúmenes (¡CUIDADO! Elimina datos)
docker-compose down -v
```

### Reconstruir la imagen

```bash
docker-compose build --no-cache
```

## 🐛 Solución de Problemas

### El contenedor se detiene inmediatamente

```bash
# Ver logs para diagnosticar
docker-compose logs linkedin-leads

# Verificar que Chrome está instalado
docker-compose exec linkedin-leads which google-chrome-stable
```

### Problemas de memoria

Aumenta el `shm_size` en `docker-compose.yml`:

```yaml
shm_size: '4gb'  # En lugar de 2gb
```

### Chrome no inicia

Verifica los logs:

```bash
docker-compose logs linkedin-leads | grep -i chrome
```

### Cookies no persisten

Verifica que el volumen está montado:

```bash
docker-compose exec linkedin-leads ls -la /data/cookies/
```

## 📊 Monitoreo

### Healthcheck

El contenedor incluye un healthcheck que verifica que el CSV existe:

```bash
# Ver estado del healthcheck
docker-compose ps
```

### Ver uso de recursos

```bash
docker stats linkedin-leads-generation
```

## 🔒 Seguridad

- **No expongas** el archivo `.env` en repositorios públicos
- Las cookies contienen tu sesión de LinkedIn - mantenlas seguras
- Los datos extraídos pueden contener información sensible

## 📝 Notas Importantes

1. **Primera ejecución**: El sistema necesitará que inicies sesión en LinkedIn manualmente. En Docker, esto se hace a través de los logs o ejecutando el contenedor de forma interactiva.

2. **Modo Headless**: En Docker, Chrome se ejecuta en modo headless (sin interfaz gráfica). Esto es necesario para contenedores.

3. **Persistencia**: Los datos se guardan en volúmenes de Docker, por lo que persisten entre reinicios del contenedor.

4. **Rendimiento**: El contenedor puede usar hasta 2GB de RAM. Ajusta según tus necesidades.

## 🚀 Despliegue en Producción

Para producción, considera:

1. **Variables de entorno seguras**: Usa un gestor de secretos (Vault, AWS Secrets Manager, etc.)
2. **Monitoreo**: Integra con sistemas de logging (ELK, Datadog, etc.)
3. **Backups**: Configura backups automáticos de los volúmenes
4. **Rate Limiting**: Implementa límites para evitar bloqueos de LinkedIn
5. **Escalado**: Si necesitas múltiples instancias, considera Kubernetes o Docker Swarm

## 📚 Referencias

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Selenium Docker Images](https://github.com/SeleniumHQ/docker-selenium)

