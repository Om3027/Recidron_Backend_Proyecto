from .security import create_security_tables
from .project import create_project_tables

def create_tables(cursor):
    """
    Crea todas las tablas de la base de datos con el nuevo esquema RBAC y Soft-Delete.
    """
    # 1. Crear tablas de seguridad
    create_security_tables(cursor)
    
    # 2. Crear tablas del proyecto
    create_project_tables(cursor)

__all__ = ["create_tables"]
