from fastapi import HTTPException
from models import SessionLocal, AuditLog
import json

def error_404(recurso: str, id: int):
    """Lanza error 404 estándar cuando no se encuentra un registro."""
    raise HTTPException(status_code=404, detail=f"{recurso} con id {id} no encontrado")

def registrar_log(usuario_id: int, accion: str, recurso: str, detalles: str = None, v_anterior: dict = None, v_nuevo: dict = None, db = None):
    """
    Registra una acción en la tabla de auditoría logs_auditoria.
    Permite guardar el estado anterior y nuevo para trazabilidad administrativa.
    """
    session = db or SessionLocal()
    try:
        nuevo_log = AuditLog(
            usuario_id=usuario_id,
            accion=accion,
            recurso=recurso,
            detalles=detalles,
            valor_anterior=json.dumps(v_anterior, default=str) if v_anterior else None,
            valor_nuevo=json.dumps(v_nuevo, default=str) if v_nuevo else None
        )
        session.add(nuevo_log)
        session.commit()
    finally:
        if not db:
            session.close()
