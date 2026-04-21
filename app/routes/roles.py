from fastapi import APIRouter, HTTPException
from app.services.seguridad_service import RoleService
from app.validators import RolCreate
from app.routes.utils import error_404
from sqlalchemy.exc import IntegrityError

router_roles = APIRouter(prefix="/roles", tags=[" Roles"])

@router_roles.get("/", summary="Listar todos los roles")
def listar_roles():
    """Consulta y retorna todos los roles del sistema."""
    service = RoleService()
    roles = service.get_all()
    return [{k: v for k, v in r.__dict__.items() if k != '_sa_instance_state'} for r in roles]

@router_roles.post("/", status_code=201, summary="Crear un rol")
def crear_rol(rol: RolCreate):
    """Registra un nuevo rol en el sistema."""
    service = RoleService()
    try:
        nuevo_rol = service.create(rol.dict())
        return {"id": nuevo_rol.id, "nombre_rol": nuevo_rol.nombre_rol}
    except IntegrityError:
        raise HTTPException(status_code=422, detail="El rol ya existe")

@router_roles.get("/{id}", summary="Obtener un rol por ID")
def obtener_rol(id: int):
    """Retorna un rol específico. Error 404 si no existe."""
    service = RoleService()
    rol = service.get_by_id(id)
    if not rol: error_404("Rol", id)
    return {k: v for k, v in rol.__dict__.items() if k != '_sa_instance_state'}

@router_roles.put("/{id}", summary="Actualizar un rol")
def actualizar_rol(id: int, rol: RolCreate):
    """Modifica el nombre de un rol existente."""
    service = RoleService()
    if not service.get_by_id(id):
        error_404("Rol", id)
    service.update(id, rol.dict())
    return {"id": id, "nombre_rol": rol.nombre_rol}

@router_roles.delete("/{id}", summary="Eliminar un rol")
def eliminar_rol(id: int):
    """Elimina un rol del sistema."""
    service = RoleService()
    if not service.get_by_id(id):
        error_404("Rol", id)
    service.delete(id)
    return {"mensaje": f"Rol {id} eliminado exitosamente"}
