from fastapi import APIRouter, HTTPException, Depends
from models import get_connection
from validators import RolCreate
from routes.utils import error_404, registrar_log
from routes.auth import check_permission
import mysql.connector

router_roles = APIRouter(prefix="/roles", tags=[" Roles"])

@router_roles.get("/", summary="Listar roles")
def listar_roles(user_auth: dict = Depends(check_permission("usuarios:leer"))):
    """Lista todos los roles disponibles."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM roles ORDER BY id")
    roles = cursor.fetchall()
    cursor.close()
    conn.close()
    return roles

@router_roles.post("/", status_code=201, summary="Crear un rol")
def crear_rol(rol: RolCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar"))):
    """Crea un nuevo rol en el sistema con auditoría."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("INSERT INTO roles (nombre_rol) VALUES (%s)", (rol.nombre_rol,))
        nuevo_id = cursor.lastrowid
        conn.commit()
        registrar_log(user_auth['id'], "CREAR", "roles", f"Rol {nuevo_id} creado: {rol.nombre_rol}")
        cursor.close()
        conn.close()
        return {"id": nuevo_id, "nombre_rol": rol.nombre_rol}
    except mysql.connector.Error as err:
        cursor.close(); conn.close()
        if err.errno == 1062:
            raise HTTPException(status_code=422, detail="El rol ya existe")
        raise HTTPException(status_code=500, detail="Error al crear rol")

@router_roles.get("/{id}", summary="Obtener rol por ID")
def obtener_rol(id: int, user_auth: dict = Depends(check_permission("usuarios:leer"))):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM roles WHERE id = %s", (id,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    if not r: error_404("Rol", id)
    return r
