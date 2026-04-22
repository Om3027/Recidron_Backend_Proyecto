from .database import get_connection, DB_CONFIG, engine, SessionLocal, Base, get_db
# Remove raw SQL imports since SQLAlchemy handles it now
from .seeders import run_seeders
from .security import Role, Permission, User, Session, AuditLog
from .project import TipoResiduo, Material, ZonaCampus, Tamano, Reporte, Geolocalizacion

def init_db():
    """
    Inicializa la base de datos en MySQL con el nuevo esquema RBAC y Soft-Delete.
    Sincroniza las tablas usando SQLAlchemy ORM.
    """
    # 1. Crear tablas con SQLAlchemy
    Base.metadata.create_all(bind=engine)

    # 2. Seeders (Datos iniciales)
    try:
        db = SessionLocal()
        run_seeders(db)
        db.close()
    except Exception as e:
        print(f"Error corriendo seeders (puede que ya existan): {e}")

    print('[ OK ] MySQL - Base de datos sincronizada correctamente.')

__all__ = [
    "get_connection", "init_db", "DB_CONFIG", 
    "engine", "SessionLocal", "Base", "get_db",
    "Role", "Permission", "User", "Session", "AuditLog",
    "TipoResiduo", "Material", "ZonaCampus", "Tamano", "Reporte", "Geolocalizacion"
]