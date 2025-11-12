# 🚀 Instrucciones Rápidas - LinkedIn Leads Generation

## ✅ Estado Actual
- ✅ Entorno virtual creado (`venv`)
- ✅ Dependencias instaladas
- ✅ Extensión AllForLeads descomprimida en carpeta `allforleads`

## 🎯 Ejecutar el Sistema

### Opción 1: Usar el script automático (Recomendado)
```bash
./run.sh
```

### Opción 2: Ejecución manual

1. **Activar el entorno virtual:**
```bash
source venv/bin/activate
```

2. **Ejecutar el script:**
```bash
python3 main.py
```

## ⚙️ Configuración

### 1. Configurar Gmail (Opcional - solo si quieres enviar emails)

**IMPORTANTE:** El sistema funciona perfectamente sin configurar Gmail. Solo extraerá y guardará los datos en el CSV. El envío de emails es completamente opcional.

Crea un archivo `.env` en la carpeta del proyecto:
```bash
nano .env
```

Agrega:
```
GMAIL_APP_PASSWORD=tu_contraseña_de_aplicación_aquí
```

Para obtener la contraseña de aplicación:
1. Ve a: https://myaccount.google.com/apppasswords
2. Genera una contraseña para "Correo"
3. Cópiala en el archivo `.env`

### 2. Primera ejecución - Iniciar sesión en LinkedIn

La primera vez que ejecutes el script:
1. Se abrirá Chrome automáticamente
2. Inicia sesión manualmente en LinkedIn
3. Presiona Enter en la terminal cuando hayas iniciado sesión
4. Las cookies se guardarán automáticamente

## 📝 Notas Importantes

- **Comando correcto**: Usa `python3` no `python` en Linux
- **Entorno virtual**: Siempre activa el entorno virtual antes de ejecutar
- **Extensión**: La carpeta `allforleads` debe existir con los archivos de la extensión
- **Chrome**: Asegúrate de tener Google Chrome instalado

## 🐛 Solución de Problemas

### Error: "python3: command not found"
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

### Error: "Chrome/ChromeDriver no encontrado"
El sistema usa `undetected-chromedriver` que descarga ChromeDriver automáticamente.

### Error: "No se encontró archivo de cookies"
Es normal en la primera ejecución. Inicia sesión manualmente cuando se te solicite.

## 📊 Salida

Los datos se guardan en `output.csv` con:
- Name, Headline, Linkedin URL
- Email 1, Email 2, ..., Email 10
- Phone Number 1, Phone Number 2, ..., Phone Number 10

