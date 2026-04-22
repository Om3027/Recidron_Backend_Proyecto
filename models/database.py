import os
import mysql.connector
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de la base de datos (Aiven Cloud)
DB_CONFIG = {
    'host':      os.getenv('DB_HOST'),
    'port':      os.getenv('DB_PORT', 16491),
    'user':      os.getenv('DB_USER'),
    'password':  os.getenv('DB_PASSWORD'),
    'database':  os.getenv('DB_NAME'),
    # Aiven requiere SSL por defecto.
}

def get_connection():
    """
    Crea y retorna una conexión a la base de datos MySQL en Aiven Cloud.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        raise
