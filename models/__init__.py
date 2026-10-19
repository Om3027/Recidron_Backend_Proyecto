from sqlalchemy import inspect, text
from .database import get_connection, DB_CONFIG, engine, SessionLocal, Base, get_db
# Remove raw SQL imports since SQLAlchemy handles it now
from .seeders import run_seeders
from .security import Role, Permission, User, Session, AuditLog
from .project import TipoResiduo, Material, ZonaCampus, Tamano, Reporte, Geolocalizacion, FotoReporte, TipoSubzona, SubzonaCampus

def init_db():
    """
    Inicializa la base de datos en MySQL con el nuevo esquema RBAC y Soft-Delete.
    Sincroniza las tablas usando SQLAlchemy ORM.
    """
    # 1. Crear tablas con SQLAlchemy
    Base.metadata.create_all(bind=engine)

    # 1.1 Verificar y sincronizar columnas añadidas a tablas existentes
    try:
        insp = inspect(engine)
        if "reportes" in insp.get_table_names():
            cols = [c["name"] for c in insp.get_columns("reportes")]
            if "subzona_id" not in cols:
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE reportes ADD COLUMN subzona_id INT NULL, ADD CONSTRAINT fk_reportes_subzona FOREIGN KEY (subzona_id) REFERENCES subzonas_campus(id) ON DELETE SET NULL;"))
                    conn.commit()
                print("[ OK ] Columna subzona_id agregada a tabla reportes.")
    except Exception as e:
        print(f"Error verificando columnas en reportes: {e}")

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
    "TipoResiduo", "Material", "ZonaCampus", "Tamano", "Reporte", "Geolocalizacion", "FotoReporte",
    "TipoSubzona", "SubzonaCampus"
]