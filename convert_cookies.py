#!/usr/bin/env python3
"""
Script para convertir cookies JSON de LinkedIn a formato pickle
Uso: python3 convert_cookies.py <archivo.json> [output.pkl]
"""

import json
import pickle
import sys
from pathlib import Path

def convert_json_to_pickle(json_file, output_file=None):
    """
    Convierte un archivo JSON de cookies a formato pickle
    
    Args:
        json_file: Ruta al archivo JSON de cookies
        output_file: Ruta de salida (opcional, por defecto cookies.pkl en la misma carpeta)
    """
    json_path = Path(json_file)
    
    if not json_path.exists():
        print(f"[!] Error: El archivo {json_file} no existe")
        return False
    
    # Determinar archivo de salida
    if output_file:
        output_path = Path(output_file)
    else:
        # Por defecto, usar cookies.pkl en la misma carpeta
        output_path = json_path.parent / "cookies.pkl"
    
    try:
        # Leer archivo JSON
        print(f"[+] Leyendo archivo JSON: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)
        
        # El archivo puede ser un array de cookies o un objeto con un campo 'cookies'
        if isinstance(cookies_data, dict):
            if 'cookies' in cookies_data:
                cookies = cookies_data['cookies']
            elif 'www.linkedin.com' in cookies_data:
                # Formato de extensión de navegador
                cookies = cookies_data['www.linkedin.com']
            else:
                # Intentar encontrar cualquier array de cookies
                cookies = None
                for key, value in cookies_data.items():
                    if isinstance(value, list):
                        cookies = value
                        break
                if cookies is None:
                    print("[!] Error: No se encontró formato de cookies reconocido en el JSON")
                    print("[!] El archivo debe contener un array de cookies o un objeto con campo 'cookies'")
                    return False
        elif isinstance(cookies_data, list):
            cookies = cookies_data
        else:
            print("[!] Error: Formato de JSON no reconocido")
            return False
        
        print(f"[+] Encontradas {len(cookies)} cookies")
        
        # Validar que las cookies tienen el formato correcto
        if len(cookies) == 0:
            print("[!] Advertencia: No se encontraron cookies en el archivo")
            return False
        
        # Verificar que hay cookies importantes de LinkedIn
        cookie_names = [c.get('name', '') for c in cookies if isinstance(c, dict)]
        important_cookies = ['li_at', 'JSESSIONID', 'li_rm']
        found_important = [name for name in important_cookies if name in cookie_names]
        
        if found_important:
            print(f"[+] Cookies importantes encontradas: {', '.join(found_important)}")
        else:
            print("[!] Advertencia: No se encontraron cookies importantes de LinkedIn (li_at, JSESSIONID, etc.)")
        
        # Guardar como pickle
        print(f"[+] Guardando cookies en formato pickle: {output_path}")
        with open(output_path, 'wb') as f:
            pickle.dump(cookies, f)
        
        print(f"[+] ✅ Conversión exitosa!")
        print(f"[+] Archivo creado: {output_path}")
        print(f"[+] Total de cookies: {len(cookies)}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"[!] Error al leer JSON: {e}")
        return False
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 convert_cookies.py <archivo.json> [output.pkl]")
        print("\nEjemplo:")
        print("  python3 convert_cookies.py cookies/www.linkedin.com_json_sumpetrol.json")
        print("  python3 convert_cookies.py cookies/www.linkedin.com_json_sumpetrol.json cookies/cookies.pkl")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_json_to_pickle(json_file, output_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

