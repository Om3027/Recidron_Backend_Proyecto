from fastapi import APIRouter
from app.models import get_connection
from app.validators import LogCreate
from app.routes.utils import error_404

router_logs = APIRouter(prefix="/logs", tags=[" Logs Auditoría"])

@router_logs.get("/", summary="Listar todos los logs")
def listar_logs():
    """Consulta todos los registros de auditoría del sistema."""
    conn = get_connection()
    logs = conn.execute("SELECT * FROM logs_auditoria ORDER BY fecha DESC").fetchall()
    conn.close()
    return [dict(l) for l in logs]

@router_logs.post("/", status_code=201, summary="Registrar un log")
def crear_log(log: LogCreate):
    """Registra una nueva acción de auditoría."""
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO logs_auditoria (usuario_id, accion, tabla, descripcion) VALUES (%s, %s, %s, %s)",
        (log.usuario_id, log.accion, log.tabla, log.descripcion)
    )
    conn.commit(); nuevo_id = cursor.lastrowid; conn.close()
    return {"id": nuevo_id, **log.dict()}

@router_logs.get("/{id}", summary="Obtener un log por ID")
def obtener_log(id: int):
    """Retorna un registro de auditoría específico."""
    conn = get_connection()
    log = conn.execute("SELECT * FROM logs_auditoria WHERE id = %s", (id,)).fetchone()
    conn.close()
    if not log: error_404("Log", id)
    return dict(log)

@router_logs.put("/{id}", summary="Actualizar un log")
def actualizar_log(id: int, log: LogCreate):
    """Modifica un registro de auditoría existente."""
    conn = get_connection()
    if not conn.execute("SELECT id FROM logs_auditoria WHERE id = %s", (id,)).fetchone():
        conn.close(); error_404("Log", id)
    conn.execute(
        "UPDATE logs_auditoria SET usuario_id=%s, accion=%s, tabla=%s, descripcion=%s WHERE id=%s",
        (log.usuario_id, log.accion, log.tabla, log.descripcion, id)
    )
    conn.commit(); conn.close()
    return {"id": id, **log.dict()}

@router_logs.delete("/{id}", summary="Eliminar un log")
def eliminar_log(id: int):
    """Elimina un registro de auditoría."""
    conn = get_connection()
    if not conn.execute("SELECT id FROM logs_auditoria WHERE id = %s", (id,)).fetchone():
        conn.close(); error_404("Log", id)
    conn.execute("DELETE FROM logs_auditoria WHERE id = %s", (id,))
    conn.commit(); conn.close()
    return {"mensaje": f"Log {id} eliminado exitosamente"}
