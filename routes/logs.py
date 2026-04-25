from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db
from servicios import ServicioLogs
from routes.auth import verificar_permiso

router_logs = APIRouter(prefix="/logs", tags=[" Logs de Auditoría"])


@router_logs.get("/", summary="Listar logs de auditoría")
def listar_logs(
    usuario_auth: dict = Depends(verificar_permiso("audit:leer")),
    db: Session = Depends(get_db),
):
    """Retorna todos los registros de auditoría (solo para administradores)."""
    return ServicioLogs(db).listar_todos()


@router_logs.get("/{id}", summary="Obtener log por ID")
def obtener_log(
    id: int,
    usuario_auth: dict = Depends(verificar_permiso("audit:leer")),
    db: Session = Depends(get_db),
):
    """Retorna un log específico con detalles de cambios."""
    return ServicioLogs(db).obtener_por_id(id)
