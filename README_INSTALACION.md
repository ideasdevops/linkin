# Link-IN - Guía de Instalación y Uso

## 📋 Requisitos Previos

- Python 3.7 o superior
- Google Chrome instalado
- Cuenta de LinkedIn
- Cuenta de Gmail con contraseña de aplicación (para envío de emails)
- Extensión AllForLeads (incluida en `allforleads.zip`)

## 🚀 Instalación

### 1. Crear entorno virtual (Recomendado - Especialmente en Linux)

**En Linux/Ubuntu/Debian:**
```bash
cd linkin
python3 -m venv venv
source venv/bin/activate
```

**En Windows:**
```bash
cd linkin
python -m venv venv
venv\Scripts\activate
```

### 2. Instalar dependencias de Python

```bash
pip install -r requirements.txt
```

### 3. Configurar la extensión AllForLeads

1. Descomprime el archivo `allforleads.zip` en la carpeta del proyecto:
```bash
unzip allforleads.zip
```

2. Asegúrate de que la carpeta `allforleads` esté en el mismo directorio que `main.py`

### 4. Configurar Gmail para envío de emails (Opcional)

**Nota:** El envío de emails es opcional. El sistema funcionará perfectamente sin esta configuración, solo extraerá y guardará los datos en el CSV.

Si deseas habilitar el envío automático de emails:

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Activa la verificación en 2 pasos
3. Genera una "Contraseña de aplicación":
   - Ve a: https://myaccount.google.com/apppasswords
   - Selecciona "Correo" y "Otro (nombre personalizado)"
   - Ingresa "LinkedIn Leads" como nombre
   - Copia la contraseña generada

4. Crea un archivo `.env` en la carpeta del proyecto:
```bash
GMAIL_APP_PASSWORD=tu_contraseña_de_aplicación_aquí
```

## 🎯 Uso

### Activar el entorno virtual (si usas uno)

**En Linux:**
```bash
source venv/bin/activate
```

**En Windows:**
```bash
venv\Scripts\activate
```

### Primera ejecución

1. Ejecuta el script:
```bash
# En Linux
python3 main.py

# En Windows (si tienes python configurado)
python main.py
```

2. El navegador se abrirá automáticamente
3. Si es la primera vez, inicia sesión manualmente en LinkedIn
4. Presiona Enter cuando hayas iniciado sesión
5. Las cookies se guardarán automáticamente para próximas ejecuciones

### Ejecuciones posteriores

El sistema cargará automáticamente las cookies guardadas, por lo que no necesitarás iniciar sesión nuevamente.

## ⚙️ Configuración

### Modificar keywords de búsqueda

Edita la línea 128 en `main.py`:
```python
keywords = ["real estate"]  # Cambia por tus keywords
```

### Ajustar límites de emails y teléfonos

El sistema ahora extrae **TODOS** los emails y teléfonos disponibles (hasta 10 de cada uno en el CSV). Para cambiar este límite, edita las líneas 110-111 en `main.py`:
```python
max_emails = 10  # Cambia según necesites
max_phones = 10  # Cambia según necesites
```

## 📊 Salida de Datos

Los datos se guardan en `output.csv` con las siguientes columnas:
- Name
- Headline
- Linkedin URL
- Email 1, Email 2, ..., Email 10
- Phone Number 1, Phone Number 2, ..., Phone Number 10

## 🔧 Mejoras Implementadas

✅ **Paths relativos**: El sistema ahora usa paths relativos, funcionando en cualquier sistema
✅ **Sin límites de contacto**: Extrae TODOS los emails y teléfonos disponibles (no solo 2)
✅ **Manejo mejorado de cookies**: Crea automáticamente el archivo de cookies si no existe
✅ **Mejor manejo de errores**: Mensajes más claros y manejo robusto de excepciones
✅ **CSV dinámico**: Soporta hasta 10 emails y 10 teléfonos por lead

## ⚠️ Notas Importantes

- **Respeto a LinkedIn**: El sistema incluye delays para evitar ser detectado como bot
- **Rate Limiting**: LinkedIn puede limitar tu cuenta si haces demasiadas búsquedas muy rápido
- **Extensión AllForLeads**: Necesitas una cuenta activa en AllForLeads para que la extensión funcione
- **Cookies**: El archivo `cookies.pkl` contiene tu sesión de LinkedIn, mantenlo seguro

## 🐛 Solución de Problemas

### Error: "La carpeta de extensión no existe"
- Descomprime `allforleads.zip` en la carpeta del proyecto
- Asegúrate de que la carpeta se llame exactamente `allforleads`

### Error: "No se encontró archivo de cookies"
- Es normal en la primera ejecución
- Inicia sesión manualmente cuando se te solicite

### Error al enviar emails
- Verifica que tu contraseña de aplicación de Gmail esté correcta en el archivo `.env`
- Asegúrate de que la verificación en 2 pasos esté activada

### No se encuentran emails/teléfonos
- Verifica que la extensión AllForLeads esté funcionando correctamente
- Asegúrate de tener créditos disponibles en tu cuenta de AllForLeads
- Algunos perfiles pueden no tener información de contacto disponible

## 📝 Licencia

Este proyecto es de código abierto. Úsalo responsablemente y respetando los términos de servicio de LinkedIn.

