from fastapi import APIRouter, HTTPException, Depends
from models import get_connection
from routes.auth import check_permission

router_logs = APIRouter(prefix="/logs", tags=[" Logs de Auditoría"])

@router_logs.get("/", summary="Listar logs de auditoría")
def listar_logs(user_auth: dict = Depends(check_permission("audit:leer"))):
    """Retorna todos los registros de auditoría (solo para administradores)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM logs_auditoria ORDER BY fecha DESC")
    logs = cursor.fetchall()
    cursor.close()
    conn.close()
    return logs

@router_logs.get("/{id}", summary="Obtener log por ID")
def obtener_log(id: int, user_auth: dict = Depends(check_permission("audit:leer"))):
    """Retorna un log específico con detalles de cambios."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM logs_auditoria WHERE id = %s", (id,))
    log = cursor.fetchone()
    cursor.close()
    conn.close()
    if not log:
        raise HTTPException(status_code=404, detail="Log no encontrado")
    return log
