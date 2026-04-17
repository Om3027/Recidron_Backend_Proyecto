import pymysql
from fastapi import APIRouter, HTTPException
from app import models
from app.validators import RolCreate
from app.routes.utils import error_404

router_roles = APIRouter(prefix="/roles", tags=[" Roles"])

@router_roles.get("/", summary="Listar todos los roles")
def listar_roles():
    """Consulta y retorna todos los roles del sistema."""
    return models.get_all_roles()

@router_roles.post("/", status_code=201, summary="Crear un rol")
def crear_rol(rol: RolCreate):
    """Registra un nuevo rol en el sistema."""
    try:
        nuevo_id = models.create_role(rol.nombre_rol)
        return {"id": nuevo_id, "nombre_rol": rol.nombre_rol}
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=422, detail="El rol ya existe")

@router_roles.get("/{id}", summary="Obtener un rol por ID")
def obtener_rol(id: int):
    """Retorna un rol específico. Error 404 si no existe."""
    rol = models.get_role_by_id(id)
    if not rol: error_404("Rol", id)
    return rol

@router_roles.put("/{id}", summary="Actualizar un rol")
def actualizar_rol(id: int, rol: RolCreate):
    """Modifica el nombre de un rol existente."""
    if not models.get_role_by_id(id):
        error_404("Rol", id)
    models.update_role(id, rol.nombre_rol)
    return {"id": id, "nombre_rol": rol.nombre_rol}

@router_roles.delete("/{id}", summary="Eliminar un rol")
def eliminar_rol(id: int):
    """Elimina un rol del sistema."""
    if not models.get_role_by_id(id):
        error_404("Rol", id)
    models.delete_role(id)
    return {"mensaje": f"Rol {id} eliminado exitosamente"}
