from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import get_db, AuditLog
from routes.auth import check_permission

router_logs = APIRouter(prefix="/logs", tags=[" Logs de Auditoría"])

@router_logs.get("/", summary="Listar logs de auditoría")
def listar_logs(user_auth: dict = Depends(check_permission("audit:leer")), db: Session = Depends(get_db)):
    """Retorna todos los registros de auditoría (solo para administradores)."""
    logs = db.query(AuditLog).order_by(AuditLog.fecha.desc()).all()
    return logs

@router_logs.get("/{id}", summary="Obtener log por ID")
def obtener_log(id: int, user_auth: dict = Depends(check_permission("audit:leer")), db: Session = Depends(get_db)):
    """Retorna un log específico con detalles de cambios."""
    log = db.query(AuditLog).filter(AuditLog.id == id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log no encontrado")
    return log
