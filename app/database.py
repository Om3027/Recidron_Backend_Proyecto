import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cargar variables de entorno (usando .env.test como en el código original)
load_dotenv(dotenv_path='.env.test')

DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_PORT = os.getenv('DATABASE_PORT')

# Construir URL de conexión para SQLAlchemy (usando pymysql como driver)
# Formato: mysql+pymysql://user:password@host:port/dbname
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# Crear el motor (Engine)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Clase para crear sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para heredar en los modelos de SQLAlchemy
Base = declarative_base()

def get_db():
    """Dependencia para obtener una sesión de base de datos en las rutas."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
