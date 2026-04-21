from fastapi import APIRouter
from app.services.seguridad_service import LogAuditoriaService
from app.validators import LogCreate
from app.routes.utils import error_404

router_logs = APIRouter(prefix="/logs", tags=[" Logs Auditoría"])

@router_logs.get("/", summary="Listar todos los logs")
def listar_logs():
    """Consulta todos los registros de auditoría del sistema."""
    service = LogAuditoriaService()
    logs = service.get_all()
    return [{k: v for k, v in l.__dict__.items() if k != '_sa_instance_state'} for l in logs]

@router_logs.post("/", status_code=201, summary="Registrar un log")
def crear_log(log: LogCreate):
    """Registra una nueva acción de auditoría."""
    service = LogAuditoriaService()
    nuevo_log = service.create(log.dict())
    return {"id": nuevo_log.id, **log.dict()}

@router_logs.get("/{id}", summary="Obtener un log por ID")
def obtener_log(id: int):
    """Retorna un registro de auditoría específico."""
    service = LogAuditoriaService()
    log = service.get_by_id(id)
    if not log: error_404("Log", id)
    return {k: v for k, v in log.__dict__.items() if k != '_sa_instance_state'}

@router_logs.put("/{id}", summary="Actualizar un log")
def actualizar_log(id: int, log: LogCreate):
    """Modifica un registro de auditoría existente."""
    service = LogAuditoriaService()
    if not service.get_by_id(id):
        error_404("Log", id)
    service.update(id, log.dict())
    return {"id": id, **log.dict()}

@router_logs.delete("/{id}", summary="Eliminar un log")
def eliminar_log(id: int):
    """Elimina un registro de auditoría."""
    service = LogAuditoriaService()
    if not service.get_by_id(id):
        error_404("Log", id)
    service.delete(id)
    return {"mensaje": f"Log {id} eliminado exitosamente"}
