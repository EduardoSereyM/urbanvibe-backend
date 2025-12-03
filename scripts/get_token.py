"""
Script para obtener un token JWT de autenticación
Usa el endpoint /api/v1/auth/login del backend
"""
import requests
import json
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
API_URL = os.getenv("API_URL", "http://localhost:8000")
LOGIN_ENDPOINT = f"{API_URL}/api/v1/auth/login"

# Credenciales de prueba
EMAIL = "local@urbanvibe.cl"
PASSWORD = "password123"

def get_auth_token():
    """
    Obtiene un token JWT usando el endpoint de login
    """
    print("=" * 70)
    print("OBTENIENDO TOKEN DE AUTENTICACIÓN")
    print("=" * 70)
    print(f"\nEndpoint: {LOGIN_ENDPOINT}")
    print(f"Email: {EMAIL}")
    
    try:
        # Hacer request al endpoint de login
        response = requests.post(
            LOGIN_ENDPOINT,
            json={
                "email": EMAIL,
                "password": PASSWORD
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            
            if token:
                print("\n✅ Token obtenido exitosamente!")
                print("\n" + "=" * 70)
                print("TOKEN:")
                print("=" * 70)
                print(token)
                print("=" * 70)
                
                # Guardar en archivo para fácil acceso
                with open("token.txt", "w") as f:
                    f.write(token)
                print("\n💾 Token guardado en: token.txt")
                
                # Mostrar comando curl de ejemplo
                print("\n" + "=" * 70)
                print("EJEMPLO DE USO CON CURL:")
                print("=" * 70)
                print(f'curl -H "Authorization: Bearer {token}" \\')
                print(f'     {API_URL}/api/v1/venues-admin/me/venues')
                print("=" * 70)
                
                return token
            else:
                print("\n❌ Error: No se encontró access_token en la respuesta")
                print(f"Respuesta: {json.dumps(data, indent=2)}")
                return None
        else:
            print(f"\n❌ Error al hacer login: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar al servidor")
        print(f"Verifica que el servidor esté corriendo en {API_URL}")
        return None
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        return None

if __name__ == "__main__":
    token = get_auth_token()
    
    if not token:
        print("\n" + "=" * 70)
        print("ALTERNATIVA: Usar modo DEMO")
        print("=" * 70)
        print("\nSi el servidor está en modo DEMO, puedes usar:")
        print('TOKEN="demo"')
        print(f'curl -H "Authorization: Bearer demo" \\')
        print(f'     {API_URL}/api/v1/venues-admin/me/venues')
        print("=" * 70)
