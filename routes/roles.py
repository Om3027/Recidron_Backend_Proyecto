import sqlite3
from fastapi import APIRouter, HTTPException
from models import get_connection
from validators import RolCreate
from routes.utils import error_404

router_roles = APIRouter(prefix="/roles", tags=[" Roles"])

@router_roles.get("/", summary="Listar todos los roles")
def listar_roles():
    """Consulta y retorna todos los roles del sistema."""
    conn = get_connection()
    roles = conn.execute("SELECT * FROM roles ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in roles]

@router_roles.post("/", status_code=201, summary="Crear un rol")
def crear_rol(rol: RolCreate):
    """Registra un nuevo rol en el sistema."""
    conn = get_connection()
    try:
        cursor = conn.execute("INSERT INTO roles (nombre_rol) VALUES (?)", (rol.nombre_rol,))
        conn.commit()
        nuevo_id = cursor.lastrowid
        conn.close()
        return {"id": nuevo_id, "nombre_rol": rol.nombre_rol}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=422, detail="El rol ya existe")

@router_roles.get("/{id}", summary="Obtener un rol por ID")
def obtener_rol(id: int):
    """Retorna un rol específico. Error 404 si no existe."""
    conn = get_connection()
    rol = conn.execute("SELECT * FROM roles WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not rol: error_404("Rol", id)
    return dict(rol)

@router_roles.put("/{id}", summary="Actualizar un rol")
def actualizar_rol(id: int, rol: RolCreate):
    """Modifica el nombre de un rol existente."""
    conn = get_connection()
    if not conn.execute("SELECT id FROM roles WHERE id = ?", (id,)).fetchone():
        conn.close(); error_404("Rol", id)
    conn.execute("UPDATE roles SET nombre_rol = ? WHERE id = ?", (rol.nombre_rol, id))
    conn.commit(); conn.close()
    return {"id": id, "nombre_rol": rol.nombre_rol}

@router_roles.delete("/{id}", summary="Eliminar un rol")
def eliminar_rol(id: int):
    """Elimina un rol del sistema."""
    conn = get_connection()
    if not conn.execute("SELECT id FROM roles WHERE id = ?", (id,)).fetchone():
        conn.close(); error_404("Rol", id)
    conn.execute("DELETE FROM roles WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return {"mensaje": f"Rol {id} eliminado exitosamente"}
