from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, csv, pickle
import undetected_chromedriver as uc
import os
from pathlib import Path
from email_send import send_email

#--------------------------------------------------------#

# Detectar si estamos en Docker
IS_DOCKER = os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER') == 'true'

# Configuración de paths - usar /data en Docker, local en desarrollo
if IS_DOCKER:
    BASE_DIR = Path('/app')
    DATA_DIR = Path('/data')
    COOKIES_FILE = DATA_DIR / "cookies" / "cookies.pkl"
    OUTPUT_CSV = DATA_DIR / "output" / "output.csv"
    print("[+] Modo Docker detectado - usando paths persistentes")
else:
    BASE_DIR = Path(__file__).parent.absolute()
    DATA_DIR = BASE_DIR
    COOKIES_FILE = BASE_DIR / "cookies.pkl"
    OUTPUT_CSV = BASE_DIR / "output.csv"
    print("[+] Modo local - usando paths locales")

EXTENSION_PATH = BASE_DIR / "allforleads"

# Crear directorios si no existen
if IS_DOCKER:
    COOKIES_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

# Verificar si la extensión existe
if not EXTENSION_PATH.exists():
    print(f"[!] Advertencia: La carpeta de extensión '{EXTENSION_PATH}' no existe.")
    print("[!] Por favor, descomprime 'allforleads.zip' en la carpeta del proyecto.")
    extension_path_str = None
else:
    extension_path_str = str(EXTENSION_PATH)

options = webdriver.ChromeOptions()
# En Docker, usar modo headless
if IS_DOCKER:
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    print("[+] Configuración Chrome para Docker (headless)")
else:
    options.add_argument('--start-maximized')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--force-device-scale-factor=1')
    options.add_argument('--disable-blink-features=AutomationControlled')
    print("[+] Configuración Chrome para local")
# Opciones experimentales (comentadas si causan problemas)
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
if extension_path_str:
    options.add_argument(f'--load-extension={extension_path_str}')
options.add_argument('--log-level=3')

# Función para extraer todos los emails y teléfonos disponibles
def extract_all_contact_data(driver, wait):
    """
    Extrae todos los emails y números de teléfono disponibles del perfil.
    Retorna: (lista_emails, lista_telefonos)
    """
    emails = []
    phone_numbers = []
    
    try:
        # Buscar todos los elementos de contacto de la extensión
        # Los emails generalmente están en ContactData_1, ContactData_2, etc.
        # Los teléfonos están en ContactData_3, ContactData_4, etc.
        # Pero necesitamos buscar todos los elementos disponibles
        
        # Buscar todos los elementos que contengan datos de contacto
        contact_elements = driver.find_elements(
            By.XPATH, 
            "//div[@class='KLM_extensionSingleProfileViewWrapperBlockSingleRowData']//div[contains(@class, 'KLM_extensionSingleProfileViewWrapperBlockSingleRowDataContent')]"
        )
        
        for element in contact_elements:
            try:
                text = element.text.strip()
                if not text:
                    continue
                
                # Detectar si es email o teléfono
                if '@' in text and '.' in text:
                    # Es un email
                    if text not in emails:
                        emails.append(text)
                elif any(char.isdigit() for char in text) and ('+' in text or '-' in text or '(' in text or len([c for c in text if c.isdigit()]) >= 7):
                    # Es probablemente un número de teléfono
                    if text not in phone_numbers:
                        phone_numbers.append(text)
            except:
                continue
        
        # Método alternativo: buscar por patrones específicos de la extensión
        # Buscar emails (ContactData_1, ContactData_2, etc. que contengan @)
        email_index = 1
        while True:
            try:
                email_xpath = f"//div[@class='KLM_extensionSingleProfileViewWrapperBlockSingleRowData']//div[contains(@class, 'KLM_extensionSingleProfileViewWrapperBlockSingleRowDataContentContactData_{email_index}')]"
                email_element = driver.find_element(By.XPATH, email_xpath)
                email_text = email_element.text.strip()
                if email_text and '@' in email_text:
                    if email_text not in emails:
                        emails.append(email_text)
                email_index += 1
            except:
                break
        
        # Buscar teléfonos (ContactData_3, ContactData_4, etc. o cualquier ContactData que no sea email)
        phone_index = 1
        while True:
            try:
                phone_xpath = f"//div[@class='KLM_extensionSingleProfileViewWrapperBlockSingleRowData']//div[contains(@class, 'KLM_extensionSingleProfileViewWrapperBlockSingleRowDataContentContactData_{phone_index}')]"
                phone_element = driver.find_element(By.XPATH, phone_xpath)
                phone_text = phone_element.text.strip()
                # Verificar que no sea un email y que parezca un teléfono
                if phone_text and '@' not in phone_text and (any(char.isdigit() for char in phone_text)):
                    if phone_text not in phone_numbers:
                        phone_numbers.append(phone_text)
                phone_index += 1
            except:
                break
                
    except Exception as e:
        print(f"[!] Error extrayendo datos de contacto: {e}")
    
    return emails, phone_numbers

# Inicializar CSV con columnas dinámicas (máximo 10 emails y 10 teléfonos para mantener estructura)
max_emails = 10
max_phones = 10
csv_headers = ['Name', 'Headline', 'Linkedin URL'] + \
              [f'Email {i+1}' for i in range(max_emails)] + \
              [f'Phone Number {i+1}' for i in range(max_phones)]

with open(OUTPUT_CSV, 'w', newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(csv_headers)

# -------------------------------------------------------#

print('[+] Link-IN - Sistema mejorado')
print('[+] Configurado para localhost')

# Función para verificar que la sesión de Chrome está activa
def is_session_active(driver):
    """Verifica si la sesión de Chrome está activa"""
    try:
        driver.current_url
        return True
    except:
        return False

# Usar undetected_chromedriver para mejor compatibilidad
# undetected_chromedriver maneja mejor las opciones, así que creamos opciones separadas
driver = None
try:
    # Para undetected_chromedriver, usar opciones más simples
    uc_options = webdriver.ChromeOptions()
    # En Docker, usar modo headless
    if IS_DOCKER:
        uc_options.add_argument('--headless=new')
        uc_options.add_argument('--no-sandbox')
        uc_options.add_argument('--disable-dev-shm-usage')
        uc_options.add_argument('--disable-gpu')
        uc_options.add_argument('--disable-software-rasterizer')
        uc_options.add_argument('--window-size=1920,1080')
        uc_options.add_argument('--disable-blink-features=AutomationControlled')
        print("[+] undetected_chromedriver configurado para Docker (headless)")
    else:
        uc_options.add_argument('--start-maximized')
        uc_options.add_argument('--no-sandbox')
        uc_options.add_argument('--disable-dev-shm-usage')
        uc_options.add_argument('--disable-gpu')
        uc_options.add_argument('--window-size=1920,1080')
        uc_options.add_argument('--disable-blink-features=AutomationControlled')
        print("[+] undetected_chromedriver configurado para local")
    
    # No cargar extensión inicialmente para evitar problemas
    # if extension_path_str:
    #     uc_options.add_argument(f'--load-extension={extension_path_str}')
    uc_options.add_argument('--log-level=3')
    
    print("[+] Iniciando Chrome con undetected_chromedriver...")
    driver = uc.Chrome(options=uc_options, use_subprocess=True, version_main=None)
    print("[+] Chrome iniciado con undetected_chromedriver")
    
    # Verificar que la sesión está activa
    if not is_session_active(driver):
        raise Exception("La sesión de Chrome no está activa después de iniciar")
        
except Exception as e:
    print(f"[!] Error con undetected_chromedriver: {e}")
    print("[+] Intentando con webdriver estándar...")
    try:
        driver = webdriver.Chrome(options=options)
        print("[+] Chrome iniciado con webdriver estándar")
        
        # Verificar que la sesión está activa
        if not is_session_active(driver):
            raise Exception("La sesión de Chrome no está activa después de iniciar")
    except Exception as e2:
        print(f"[!] Error crítico: No se pudo iniciar Chrome: {e2}")
        print("[!] Por favor, verifica que Chrome está instalado correctamente")
        exit(1)

# Configurar tamaño de ventana explícitamente
try:
    driver.set_window_size(1920, 1080)
    driver.maximize_window()
    # Esperar un momento para que la ventana se renderice
    time.sleep(3)
except:
    pass

# Verificar display en Linux
if os.name == 'posix':
    display = os.environ.get('DISPLAY')
    if not display:
        print("[!] Advertencia: Variable DISPLAY no configurada")
        print("[!] Si estás en un servidor remoto, configura DISPLAY o usa Xvfb")
    else:
        print(f"[+] DISPLAY configurado: {display}")

wait = WebDriverWait(driver, 10)

# Primero, verificar que Chrome funciona cargando una página simple
print("[+] Verificando que Chrome funciona correctamente...")
try:
    driver.get("about:blank")
    time.sleep(1)
    print("[+] Chrome responde correctamente")
except Exception as e:
    print(f"[!] Error verificando Chrome: {e}")

# Obtener keywords desde variable de entorno o usar default
keywords_str = os.environ.get('LINKEDIN_KEYWORDS', 'real estate')
keywords = [k.strip() for k in keywords_str.split(',')]
keyword_num = 0
keyword = keywords[keyword_num] if keywords else "real estate"
print(f"[+] Keywords configuradas: {keywords}")
url = f"https://www.linkedin.com/search/results/people/?keywords={keyword.replace(' ','+')}"
link_wait_time = 8
print(f"[+] Navegando a LinkedIn...")
print(f"[+] URL: {url}")

# Esta sección se ejecutará solo si no hay cookies o si falla la carga de cookies
# Si las cookies se cargan correctamente, la navegación se hace en la sección de cookies
# Por ahora, comentamos esta navegación inicial ya que se hará después de cargar cookies
print("[+] Esperando a que se carguen las cookies antes de navegar...")

# La navegación a la URL de búsqueda ahora se hace después de cargar cookies exitosamente
# Ver sección de carga de cookies más abajo

# Función para cargar cookies desde JSON si existe
def load_cookies_from_json():
    """Intenta cargar cookies desde un archivo JSON en la carpeta cookies"""
    # Buscar en múltiples ubicaciones posibles (en orden de prioridad)
    possible_dirs = [
        DATA_DIR / "cookies",  # Docker: /data/cookies (volumen persistente)
        BASE_DIR / "cookies",  # Local: ./cookies o Docker: /app/cookies (código)
        Path("cookies"),       # Relativo
        Path("/app/cookies"),  # Docker: desde código fuente
    ]
    
    cookies_dir = None
    json_file = None
    
    # Buscar el primer directorio que exista y tenga archivos JSON
    for dir_path in possible_dirs:
        if dir_path.exists():
            json_files = list(dir_path.glob("*.json"))
            if json_files:
                cookies_dir = dir_path
                json_file = json_files[0]
                print(f"[+] Encontrado directorio de cookies: {dir_path}")
                break
    
    if cookies_dir and json_file:
        print(f"[+] Encontrado archivo JSON de cookies: {json_file.name}")
        try:
            import json
            with open(json_file, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
                
                # Manejar diferentes formatos de JSON
                if isinstance(cookies_data, dict):
                    if 'cookies' in cookies_data:
                        cookies = cookies_data['cookies']
                    elif 'www.linkedin.com' in cookies_data:
                        cookies = cookies_data['www.linkedin.com']
                    else:
                        # Buscar cualquier array de cookies
                        cookies = None
                        for key, value in cookies_data.items():
                            if isinstance(value, list):
                                cookies = value
                                break
                        if cookies is None:
                            return None
                elif isinstance(cookies_data, list):
                    cookies = cookies_data
                else:
                    return None
                
            # Convertir y guardar como pickle
            print(f"[+] Convirtiendo {len(cookies)} cookies de JSON a pickle...")
            
            # Asegurar que el directorio de destino existe
            COOKIES_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            with open(COOKIES_FILE, 'wb') as f:
                pickle.dump(cookies, f)
            print(f"[+] ✅ Cookies convertidas y guardadas en {COOKIES_FILE}")
            
            # Si el JSON estaba en el código (/app), copiarlo también al volumen (/data) para persistencia
            if IS_DOCKER and str(json_file).startswith('/app'):
                volume_json = DATA_DIR / "cookies" / json_file.name
                volume_json.parent.mkdir(parents=True, exist_ok=True)
                try:
                    import shutil
                    shutil.copy2(json_file, volume_json)
                    print(f"[+] Archivo JSON copiado al volumen persistente: {volume_json}")
                except Exception as e:
                    print(f"[!] No se pudo copiar JSON al volumen (no crítico): {e}")
            
            return True
        except Exception as e:
            print(f"[!] Error convirtiendo cookies desde JSON: {e}")
            return False
    return False

# Manejo de cookies mejorado
# Primero intentar cargar desde JSON si no existe el pickle
if not COOKIES_FILE.exists():
    print("[+] No se encontró archivo de cookies pickle, buscando JSON...")
    load_cookies_from_json()

if COOKIES_FILE.exists():
    try:
        # Verificar sesión antes de cargar cookies
        if not is_session_active(driver):
            raise Exception("La sesión de Chrome no está activa")
            
        # Las cookies se cargarán después de navegar a LinkedIn
        # (ver código más abajo donde se maneja la navegación)
        if is_session_active(driver):
            # IMPORTANTE: Primero navegar a LinkedIn para establecer el dominio antes de agregar cookies
            print("[+] Navegando a LinkedIn para establecer dominio...")
            driver.get("https://www.linkedin.com")
            time.sleep(2)
            
            # Ahora agregar las cookies (deben agregarse después de estar en el dominio correcto)
            print("[+] Aplicando cookies al dominio de LinkedIn...")
            with open(COOKIES_FILE, 'rb') as f:
                cookies = pickle.load(f)
            
            cookies_added = 0
            cookies_failed = 0
            for cookie in cookies:
                try:
                    # Normalizar la cookie para Selenium
                    # Selenium requiere: name, value, domain, path (opcional: expiry, secure, httpOnly)
                    normalized_cookie = {}
                    
                    # Campos requeridos
                    if 'name' not in cookie or 'value' not in cookie:
                        print(f"[!] Cookie inválida (falta name o value): {cookie.get('name', 'unknown')}")
                        cookies_failed += 1
                        continue
                    
                    normalized_cookie['name'] = cookie['name']
                    normalized_cookie['value'] = cookie['value']
                    
                    # Dominio: Selenium requiere que empiece con punto para dominios
                    if 'domain' in cookie:
                        domain = cookie['domain']
                        # Si el dominio no empieza con punto, agregarlo (excepto si es localhost)
                        if not domain.startswith('.') and 'linkedin.com' in domain:
                            if domain == 'linkedin.com':
                                normalized_cookie['domain'] = '.linkedin.com'
                            else:
                                normalized_cookie['domain'] = domain
                        else:
                            normalized_cookie['domain'] = domain
                    else:
                        # Si no hay dominio, usar el dominio por defecto de LinkedIn
                        normalized_cookie['domain'] = '.linkedin.com'
                    
                    # Path: si no existe, usar '/'
                    normalized_cookie['path'] = cookie.get('path', '/')
                    
                    # Expiry: convertir expirationDate a expiry (Selenium usa expiry)
                    if 'expiry' in cookie:
                        # expiry debe ser un timestamp Unix (segundos desde epoch)
                        try:
                            expiry = int(cookie['expiry'])
                            if expiry > 0:
                                normalized_cookie['expiry'] = expiry
                        except (ValueError, TypeError):
                            pass
                    elif 'expirationDate' in cookie:
                        # Convertir expirationDate a expiry
                        try:
                            expiry = int(cookie['expirationDate'])
                            if expiry > 0:
                                normalized_cookie['expiry'] = expiry
                        except (ValueError, TypeError):
                            pass
                    
                    # Secure: convertir a booleano
                    if 'secure' in cookie:
                        normalized_cookie['secure'] = bool(cookie['secure'])
                    elif 'httpOnly' in cookie and cookie.get('httpOnly'):
                        # Si es httpOnly, también puede ser secure
                        normalized_cookie['secure'] = cookie.get('secure', False)
                    
                    # httpOnly: Selenium no soporta httpOnly directamente, pero lo ignoramos
                    # No incluimos httpOnly en normalized_cookie
                    
                    # Eliminar campos no soportados por Selenium
                    # (sameSite, storeId, etc. no son necesarios)
                    
                    # Intentar agregar la cookie
                    driver.add_cookie(normalized_cookie)
                    cookies_added += 1
                    
                except Exception as e:
                    error_msg = str(e) if str(e) else type(e).__name__
                    print(f"[!] No se pudo agregar cookie '{cookie.get('name', 'unknown')}': {error_msg}")
                    cookies_failed += 1
                    # Mostrar detalles de la cookie para debugging (solo las primeras 3)
                    if cookies_failed <= 3:
                        print(f"    Detalles: domain={cookie.get('domain', 'N/A')}, path={cookie.get('path', 'N/A')}")
                    pass
            
            print(f"[+] {cookies_added} cookies aplicadas exitosamente")
            if cookies_failed > 0:
                print(f"[!] {cookies_failed} cookies fallaron al aplicarse")
            
            # Verificar que al menos las cookies importantes se aplicaron
            if cookies_added == 0:
                print("[!] ERROR CRÍTICO: No se pudo aplicar ninguna cookie")
                print("[!] Esto significa que las cookies no funcionarán")
                print("[!] Verifica el formato de las cookies en el archivo pickle")
                if IS_DOCKER:
                    print("[!] Saliendo... Por favor, verifica las cookies")
                    exit(0)
            
            # Refrescar para que las cookies tomen efecto
            print("[+] Refrescando página para aplicar cookies...")
            driver.refresh()
            time.sleep(5)  # Esperar a que cargue con las cookies
            
            # Verificar si estamos logueados
            current_url = driver.current_url
            page_title = driver.title.lower()
            
            # Verificar si estamos en la página de login
            if "login" in current_url.lower() or "login" in page_title:
                print("[!] Advertencia: Las cookies no funcionaron, todavía estamos en la página de login")
                print(f"[!] URL actual: {current_url[:80]}")
                print("[!] Las cookies pueden estar expiradas o ser inválidas")
                print("[!] Verificando cookies importantes...")
                
                # Verificar cookies importantes
                all_cookies = driver.get_cookies()
                cookie_names = [c.get('name', '') for c in all_cookies]
                important_cookies = ['li_at', 'JSESSIONID', 'li_rm']
                found_important = [name for name in important_cookies if name in cookie_names]
                
                if not found_important:
                    print("[!] No se encontraron cookies importantes (li_at, JSESSIONID, li_rm)")
                    print("[!] Las cookies exportadas pueden no ser válidas")
                
                if IS_DOCKER:
                    print("[!] En Docker, necesitas cookies válidas y recientes")
                    print("[!] Por favor, exporta nuevas cookies desde tu navegador")
                    print("[!] Saliendo... (no se reiniciará automáticamente)")
                    exit(0)  # Salir con código 0 para evitar reinicio
                else:
                    print("[!] Por favor, inicia sesión manualmente")
                    input("[+] Presiona Enter cuando hayas iniciado sesión...")
                    # Guardar nuevas cookies
                    if is_session_active(driver):
                        cookies = driver.get_cookies()
                        with open(COOKIES_FILE, 'wb') as f:
                            pickle.dump(cookies, f)
                        print("[+] Nuevas cookies guardadas")
            else:
                print("[+] Cookies cargadas exitosamente - Sesión activa verificada")
                print(f"[+] URL actual: {current_url[:80]}")
                
                # Ahora navegar a la URL de búsqueda después de verificar login
                print("[+] Navegando a la página de búsqueda...")
                # Obtener keywords desde variable de entorno o usar default
                keywords_str = os.environ.get('LINKEDIN_KEYWORDS', 'real estate')
                keywords = [k.strip() for k in keywords_str.split(',')]
                keyword_num = 0
                keyword = keywords[keyword_num] if keywords else "real estate"
                
                url = f"https://www.linkedin.com/search/results/people/?keywords={keyword.replace(' ', '+')}"
                print(f"[+] URL de búsqueda: {url}")
                driver.get(url)
                time.sleep(8)  # Esperar más tiempo a que cargue la página de búsqueda
                
                # Verificar que estamos en la página correcta
                current_url_after = driver.current_url
                if "login" in current_url_after.lower():
                    print("[!] ERROR: Después de navegar a búsqueda, redirigió a login")
                    print("[!] Las cookies pueden no estar funcionando correctamente")
                    print(f"[!] URL final: {current_url_after[:100]}")
                    if IS_DOCKER:
                        print("[!] Saliendo... Por favor, verifica las cookies")
                        exit(0)
                else:
                    print(f"[+] Navegación exitosa a búsqueda: {current_url_after[:80]}")
        else:
            raise Exception("La sesión se perdió al refrescar")
            
    except Exception as e:
        print(f"[!] Error cargando cookies: {e}")
        if not is_session_active(driver):
            print("[!] Chrome se cerró. Por favor, ejecuta el script nuevamente.")
            exit(1)
        
        # En Docker, no podemos usar input() - esperar tiempo razonable o salir
        if IS_DOCKER:
            print("[!] Modo Docker detectado - no se puede hacer login interactivo")
            print("[!] Por favor, sube las cookies manualmente al volumen /data/cookies/cookies.pkl")
            print("[!] O ejecuta el contenedor de forma interactiva para hacer login inicial")
            print("[!] Saliendo...")
            exit(1)
        else:
            print("[!] Por favor, inicia sesión manualmente en LinkedIn")
            input("[+] Presiona Enter cuando hayas iniciado sesión...")
            # Guardar cookies para próxima vez
            if is_session_active(driver):
                cookies = driver.get_cookies()
                with open(COOKIES_FILE, 'wb') as f:
                    pickle.dump(cookies, f)
                print("[+] Cookies guardadas para próxima ejecución")
            else:
                print("[!] No se pudieron guardar cookies - Chrome se cerró")
else:
    print("[!] No se encontró archivo de cookies.")
    
    # Verificar sesión antes de continuar
    if not is_session_active(driver):
        print("[!] Chrome se cerró. Por favor, ejecuta el script nuevamente.")
        exit(1)
    
    # En Docker, no podemos usar input() - manejar de forma diferente
    if IS_DOCKER:
        print("[!] Modo Docker detectado - no se puede hacer login interactivo")
        print("[!] INSTRUCCIONES PARA DOCKER:")
        print("    1. Ejecuta el contenedor de forma interactiva para hacer login inicial:")
        print("       docker-compose exec linkin bash")
        print("       python3 main.py")
        print("    2. O sube las cookies manualmente:")
        print("       - Exporta cookies desde tu navegador")
        print("       - Cópialas a /data/cookies/cookies.pkl en el volumen")
        print("[!] Saliendo... El contenedor se reiniciará automáticamente.")
        print("[!] Una vez que tengas las cookies, el script funcionará correctamente.")
        exit(0)  # Salir con código 0 para que Docker no lo considere error
    else:
        input("[+] Presiona Enter cuando hayas iniciado sesión en LinkedIn...")
        
        # Guardar cookies
        if is_session_active(driver):
            cookies = driver.get_cookies()
            with open(COOKIES_FILE, 'wb') as f:
                pickle.dump(cookies, f)
            print("[+] Cookies guardadas para próxima ejecución")
        else:
            print("[!] No se pudieron guardar cookies - Chrome se cerró")
# Verificar que estamos logueados antes de continuar
print("[+] Verificando sesión antes de buscar leads...")
current_url = driver.current_url
if "login" in current_url.lower():
    print("[!] ERROR: Todavía estamos en la página de login")
    print("[!] Las cookies no funcionaron correctamente")
    if IS_DOCKER:
        print("[!] Saliendo... Por favor, verifica las cookies")
        exit(0)
    else:
        print("[!] Por favor, inicia sesión manualmente")
        input("[+] Presiona Enter cuando hayas iniciado sesión...")

# Esperar un momento antes de buscar leads
cnt = 0
time.sleep(4.5)
flag = True
page_no = 1
found_lead = 0

# Intentar encontrar leads con manejo de errores mejorado
try:
    print("[+] Buscando leads en la página...")
    all_leads = wait.until(EC.presence_of_all_elements_located((By.XPATH,"//li[@class='reusable-search__result-container']//span[@class='entity-result__title-line entity-result__title-line--2-lines ']//a")))
except Exception as e:
    print(f"[!] ERROR: No se pudieron encontrar leads en la página")
    print(f"[!] Detalles: {e}")
    print(f"[!] URL actual: {driver.current_url[:100]}")
    print(f"[!] Título: {driver.title[:50]}")
    
    # Verificar si estamos en login
    if "login" in driver.current_url.lower():
        print("[!] El problema es que todavía estamos en la página de login")
        print("[!] Las cookies no están funcionando correctamente")
        if IS_DOCKER:
            print("[!] Saliendo... Por favor, actualiza las cookies")
            exit(0)
    
    # Si no es login, puede ser otro problema
    print("[!] Puede ser que:")
    print("    - LinkedIn cambió su estructura HTML")
    print("    - La página no cargó completamente")
    print("    - LinkedIn está bloqueando el acceso")
    print("[!] Saliendo...")
    if IS_DOCKER:
        exit(0)
    else:
        raise
try:
    driver.find_element(By.XPATH,"(//button[@class='msg-overlay-bubble-header__control msg-overlay-bubble-header__control--new-convo-btn artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view'])[2]").click()
except:pass
print(f"Found [{len(all_leads)}] Leads on Page No # [{page_no}]")
for i in range(500000000000):
    cnt += 1
    lead_name = wait.until(EC.presence_of_element_located((By.XPATH,f"(//li[@class='reusable-search__result-container']//span[@class='entity-result__title-line entity-result__title-line--2-lines ']//a)[{cnt}]"))).text
    if "LinkedIn" not in str(lead_name):
        headline = driver.find_element(By.XPATH,f"(//li[@class='reusable-search__result-container']//div[@class='entity-result__primary-subtitle t-14 t-black t-normal'])[{cnt}]").text
        profile_url = driver.find_element(By.XPATH,f"(//li[@class='reusable-search__result-container']//span[@class='entity-result__title-line entity-result__title-line--2-lines ']//a)[{cnt}]").get_attribute('href')
        lead_name = str(lead_name).split(' ')
        lead_name = f"{lead_name[0]} {lead_name[1]}".replace('View','').replace('\n','')
        driver.execute_script(f"window.open('{profile_url}');")
        time.sleep(1)
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(2)
        driver.refresh()
        time.sleep(2)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH,"//div[@class='KLM_extension_company_product_name']//span[1]")))
        except:pass
        try:
            wait.until(EC.presence_of_element_located((By.ID,"KLMUnlockProfileInformation"))).click()
            time.sleep(2)
        except:
            try:
                time.sleep(2)
                wait.until(EC.presence_of_element_located((By.ID,"KLMUnlockProfileInformation"))).click()
                time.sleep(2)
            except:
                try:
                    time.sleep(1)
                    wait.until(EC.presence_of_element_located((By.ID,"KLMUnlockProfileInformation"))).click()
                    time.sleep(2)
                except:
                    try:
                        time.sleep(2)
                        wait.until(EC.presence_of_element_located((By.ID,"KLMUnlockProfileInformation"))).click()
                        time.sleep(2)
                    except:pass
        try:
            # Extraer todos los emails y teléfonos disponibles
            emails, phone_numbers = extract_all_contact_data(driver, wait)
            
            if emails or phone_numbers:
                print("Name : ", lead_name)
                print("Headline : ", headline)
                print("Linkedin URL : ", profile_url)
                
                # Mostrar todos los emails encontrados
                for idx, email in enumerate(emails, 1):
                    print(f"Email [{idx}] : ", email)
                
                # Mostrar todos los teléfonos encontrados
                for idx, phone in enumerate(phone_numbers, 1):
                    print(f"Phone Number [{idx}] : ", phone)
                
                # Enviar emails a todos los encontrados
                for email in emails:
                    if email:
                        try:
                            send_email(email, lead_name)
                        except Exception as e:
                            print(f"[!] Error enviando email a {email}: {e}")
                
                # Preparar fila para CSV (rellenar hasta max_emails y max_phones)
                csv_row = [lead_name, headline, profile_url]
                # Agregar emails (rellenar con '' si hay menos)
                for i in range(max_emails):
                    csv_row.append(emails[i] if i < len(emails) else '')
                # Agregar teléfonos (rellenar con '' si hay menos)
                for i in range(max_phones):
                    csv_row.append(phone_numbers[i] if i < len(phone_numbers) else '')
                
                # Guardar en CSV
                with open(OUTPUT_CSV, 'a', newline='', encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(csv_row)
                
                found_lead += 1
                print(f"[+] Encontrados [{found_lead}] LEADs")
                print("-----------------------------------------------------")
            else:
                print(f"[!] No se encontraron datos de contacto para {lead_name}")

        except Exception as e:
            print(f"[!] Error procesando perfil: {e}")
            pass
        # time.sleep(500000)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    if cnt == len(all_leads):
        last_lead = driver.find_element(By.XPATH,f"(//li[@class='reusable-search__result-container']//div[@class='entity-result__primary-subtitle t-14 t-black t-normal'])[{cnt}]")
        driver.execute_script("arguments[0].scrollIntoView();", last_lead)
        time.sleep(2)
        wait.until(EC.presence_of_element_located((By.XPATH,'//button[@aria-label="Next"]'))).click()
        page_no += 1 
        print(f"Found [{len(all_leads)}] Leads on Page No # [{page_no}]")       
        time.sleep(2)
        
        cnt = 0 
