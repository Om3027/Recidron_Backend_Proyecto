import pymysql
from fastapi import APIRouter, HTTPException
from app import models
from app.validators import SesionCreate
from app.routes.utils import error_404

router_sesiones = APIRouter(prefix="/sesiones", tags=[" Sesiones"])

@router_sesiones.get("/", summary="Listar todas las sesiones")
def listar_sesiones():
    """Consulta todas las sesiones registradas en el sistema."""
    return models.get_all_sessions()

@router_sesiones.post("/", status_code=201, summary="Registrar una sesión")
def crear_sesion(sesion: SesionCreate):
    """Registra una nueva sesión activa para un usuario."""
    if not models.get_user_by_id(sesion.usuario_id):
        raise HTTPException(status_code=404, detail="El usuario no existe")
    try:
        nuevo_id = models.create_session(sesion.usuario_id, sesion.token, sesion.expira_en)
        return {"id": nuevo_id, **sesion.dict()}
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=422, detail="El token ya existe")

@router_sesiones.get("/{id}", summary="Obtener una sesión por ID")
def obtener_sesion(id: int):
    """Retorna una sesión específica."""
    s = models.get_session_by_id(id)
    if not s: error_404("Sesion", id)
    return s

@router_sesiones.put("/{id}", summary="Actualizar una sesión")
def actualizar_sesion(id: int, sesion: SesionCreate):
    """Actualiza los datos de una sesión existente."""
    if not models.get_session_by_id(id):
        error_404("Sesion", id)
    models.update_session(id, sesion.usuario_id, sesion.token, sesion.expira_en)
    return {"id": id, **sesion.dict()}

@router_sesiones.delete("/{id}", summary="Cerrar una sesión")
def eliminar_sesion(id: int):
    """Cierra/elimina una sesión del sistema."""
    if not models.get_session_by_id(id):
        error_404("Sesion", id)
    models.delete_session(id)
    return {"mensaje": f"Sesion {id} eliminada exitosamente"}
