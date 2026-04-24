from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db
from servicios import ServicioSesiones
from validators import SesionCreate
from routes.auth import verificar_permiso

router_sesiones = APIRouter(prefix="/sesiones", tags=[" Sesiones"])


@router_sesiones.get("/", summary="Listar todas las sesiones")
def listar_sesiones(
    usuario_auth: dict = Depends(verificar_permiso("audit:leer")),
    db: Session = Depends(get_db),
):
    """Consulta todas las sesiones registradas (solo para auditores/admin)."""
    return ServicioSesiones(db).listar_todas()


@router_sesiones.post("/", status_code=201, summary="Registrar una sesión manualmente")
def crear_sesion(sesion: SesionCreate, db: Session = Depends(get_db)):
    """Registra una nueva sesión activa para un usuario."""
    return ServicioSesiones(db).crear_manual(sesion.usuario_id, sesion.token, sesion.expira_en)


@router_sesiones.get("/{id}", summary="Obtener una sesión por ID")
def obtener_sesion(
    id: int,
    usuario_auth: dict = Depends(verificar_permiso("audit:leer")),
    db: Session = Depends(get_db),
):
    """Retorna una sesión específica."""
    return ServicioSesiones(db).obtener_por_id(id)


@router_sesiones.delete("/{id}", summary="Cerrar una sesión")
def cerrar_sesion(id: int, db: Session = Depends(get_db)):
    """Cierra (desactiva) una sesión del sistema (Logout)."""
    return ServicioSesiones(db).cerrar_sesion(id)
