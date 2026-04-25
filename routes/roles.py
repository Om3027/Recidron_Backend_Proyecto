from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db
from servicios import ServicioRoles
from validators import RolCreate
from routes.auth import verificar_permiso

router_roles = APIRouter(prefix="/roles", tags=[" Roles"])


@router_roles.get("/", summary="Listar roles")
def listar_roles(
    usuario_auth: dict = Depends(verificar_permiso("usuarios:leer")),
    db: Session = Depends(get_db),
):
    """Lista todos los roles disponibles."""
    return ServicioRoles(db).listar_todos()


@router_roles.post("/", status_code=201, summary="Crear un rol")
def crear_rol(
    rol: RolCreate,
    usuario_auth: dict = Depends(verificar_permiso("catalogos:gestionar")),
    db: Session = Depends(get_db),
):
    """Crea un nuevo rol en el sistema con auditoría."""
    return ServicioRoles(db).crear(rol.nombre_rol, usuario_auth["id"])


@router_roles.get("/{id}", summary="Obtener rol por ID")
def obtener_rol(
    id: int,
    usuario_auth: dict = Depends(verificar_permiso("usuarios:leer")),
    db: Session = Depends(get_db),
):
    """Retorna un rol específico."""
    return ServicioRoles(db).obtener_por_id(id)
