from fastapi import APIRouter, HTTPException
from app.services.seguridad_service import SessionService, UserService
from app.validators import SesionCreate
from app.routes.utils import error_404
from sqlalchemy.exc import IntegrityError

router_sesiones = APIRouter(prefix="/sesiones", tags=[" Sesiones"])

@router_sesiones.get("/", summary="Listar todas las sesiones")
def listar_sesiones():
    """Consulta todas las sesiones registradas en el sistema."""
    service = SessionService()
    sesiones = service.get_all()
    return [{k: v for k, v in s.__dict__.items() if k != '_sa_instance_state'} for s in sesiones]

@router_sesiones.post("/", status_code=201, summary="Registrar una sesión")
def crear_sesion(sesion: SesionCreate):
    """Registra una nueva sesión activa para un usuario."""
    user_service = UserService()
    session_service = SessionService()
    
    if not user_service.get_by_id(sesion.usuario_id):
        raise HTTPException(status_code=404, detail="El usuario no existe")
    try:
        nueva_sesion = session_service.create(sesion.dict())
        return {"id": nueva_sesion.id, **sesion.dict()}
    except IntegrityError:
        raise HTTPException(status_code=422, detail="El token ya existe")

@router_sesiones.get("/{id}", summary="Obtener una sesión por ID")
def obtener_sesion(id: int):
    """Retorna una sesión específica."""
    service = SessionService()
    s = service.get_by_id(id)
    if not s: error_404("Sesion", id)
    return {k: v for k, v in s.__dict__.items() if k != '_sa_instance_state'}

@router_sesiones.put("/{id}", summary="Actualizar una sesión")
def actualizar_sesion(id: int, sesion: SesionCreate):
    """Actualiza los datos de una sesión existente."""
    service = SessionService()
    if not service.get_by_id(id):
        error_404("Sesion", id)
    service.update(id, sesion.dict())
    return {"id": id, **sesion.dict()}

@router_sesiones.delete("/{id}", summary="Cerrar una sesión")
def eliminar_sesion(id: int):
    """Cierra/elimina una sesión del sistema."""
    service = SessionService()
    if not service.get_by_id(id):
        error_404("Sesion", id)
    service.delete(id)
    return {"mensaje": f"Sesion {id} eliminada exitosamente"}
