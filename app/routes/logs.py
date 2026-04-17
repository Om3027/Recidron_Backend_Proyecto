from fastapi import APIRouter
from app import models
from app.validators import LogCreate
from app.routes.utils import error_404

router_logs = APIRouter(prefix="/logs", tags=[" Logs Auditoría"])

@router_logs.get("/", summary="Listar todos los logs")
def listar_logs():
    """Consulta todos los registros de auditoría del sistema."""
    return models.get_all_logs()

@router_logs.post("/", status_code=201, summary="Registrar un log")
def crear_log(log: LogCreate):
    """Registra una nueva acción de auditoría."""
    nuevo_id = models.create_log(log.usuario_id, log.accion, log.tabla, log.descripcion)
    return {"id": nuevo_id, **log.dict()}

@router_logs.get("/{id}", summary="Obtener un log por ID")
def obtener_log(id: int):
    """Retorna un registro de auditoría específico."""
    log = models.get_log_by_id(id)
    if not log: error_404("Log", id)
    return log

@router_logs.put("/{id}", summary="Actualizar un log")
def actualizar_log(id: int, log: LogCreate):
    """Modifica un registro de auditoría existente."""
    if not models.get_log_by_id(id):
        error_404("Log", id)
    models.update_log(id, log.usuario_id, log.accion, log.tabla, log.descripcion)
    return {"id": id, **log.dict()}

@router_logs.delete("/{id}", summary="Eliminar un log")
def eliminar_log(id: int):
    """Elimina un registro de auditoría."""
    if not models.get_log_by_id(id):
        error_404("Log", id)
    models.delete_log(id)
    return {"mensaje": f"Log {id} eliminado exitosamente"}
