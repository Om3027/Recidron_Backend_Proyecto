import os
import mysql.connector
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

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

# --- Configuración de SQLAlchemy ---

# Construir la URL de conexión para SQLAlchemy usando el driver mysqlconnector
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Crear el engine (motor de conexión)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_recycle=3600,  # Reciclar conexiones cada hora para evitar caídas por inactividad
    echo=False          # Cambiar a True si deseas ver las consultas SQL generadas en consola
)

# Fábrica de sesiones para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base declarativa de la cual heredarán todos los modelos
Base = declarative_base()

def get_db():
    """
    Generador de sesiones para inyección de dependencias en FastAPI.
    Proporciona una sesión por request y la cierra automáticamente.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
