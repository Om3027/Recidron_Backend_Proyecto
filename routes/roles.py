from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import get_db, Role
from validators import RolCreate
from routes.utils import error_404, registrar_log
from routes.auth import check_permission

router_roles = APIRouter(prefix="/roles", tags=[" Roles"])

@router_roles.get("/", summary="Listar roles")
def listar_roles(user_auth: dict = Depends(check_permission("usuarios:leer")), db: Session = Depends(get_db)):
    """Lista todos los roles disponibles."""
    roles = db.query(Role).order_by(Role.id).all()
    return roles

@router_roles.post("/", status_code=201, summary="Crear un rol")
def crear_rol(rol: RolCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar")), db: Session = Depends(get_db)):
    """Crea un nuevo rol en el sistema con auditoría."""
    try:
        nuevo_rol = Role(nombre_rol=rol.nombre_rol)
        db.add(nuevo_rol)
        db.commit()
        db.refresh(nuevo_rol)
        
        registrar_log(user_auth['id'], "CREAR", "roles", f"Rol {nuevo_rol.id} creado: {nuevo_rol.nombre_rol}", db=db)
        
        return {"id": nuevo_rol.id, "nombre_rol": nuevo_rol.nombre_rol}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=422, detail="El rol ya existe")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear rol")

@router_roles.get("/{id}", summary="Obtener rol por ID")
def obtener_rol(id: int, user_auth: dict = Depends(check_permission("usuarios:leer")), db: Session = Depends(get_db)):
    r = db.query(Role).filter(Role.id == id).first()
    if not r: error_404("Rol", id)
    return r
