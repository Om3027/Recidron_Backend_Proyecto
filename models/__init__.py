from .database import get_connection, DB_CONFIG, engine, SessionLocal, Base, get_db
from .schemas import create_tables
from .migrations import run_migrations
from .seeders import run_seeders
from .security import Role, Permission, User, Session, AuditLog
from .project import TipoResiduo, Material, ZonaCampus, Tamano, Reporte, Geolocalizacion

def init_db():
    """
    Inicializa la base de datos en MySQL con el nuevo esquema RBAC y Soft-Delete.
    Sincroniza las tablas necesarias para la migración desde SQLite.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Crear tablas
    create_tables(cursor)

    # 2. Migraciones
    run_migrations(cursor)

    # 3. Seeders (Datos iniciales)
    run_seeders(cursor)

    conn.commit()
    cursor.close()
    conn.close()
    print('[ OK ] MySQL - Base de datos sincronizada correctamente.')

__all__ = [
    "get_connection", "init_db", "DB_CONFIG", 
    "engine", "SessionLocal", "Base", "get_db",
    "Role", "Permission", "User", "Session", "AuditLog",
    "TipoResiduo", "Material", "ZonaCampus", "Tamano", "Reporte", "Geolocalizacion"
]