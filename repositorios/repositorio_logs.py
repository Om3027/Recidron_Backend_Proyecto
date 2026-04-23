import json
from sqlalchemy.orm import Session
from models import AuditLog


class RepositorioLogs:
    """
    Capa de acceso a datos para la tabla `logs_auditoria`.
    Solo contiene consultas SQLAlchemy — sin lógica de negocio.
    """

    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self) -> list[AuditLog]:
        return self.db.query(AuditLog).order_by(AuditLog.fecha.desc()).all()

    def obtener_por_id(self, log_id: int) -> AuditLog | None:
        return self.db.query(AuditLog).filter(AuditLog.id == log_id).first()

    def registrar(
        self,
        usuario_id: int | None,
        accion: str,
        recurso: str,
        detalles: str | None = None,
        valor_anterior: dict | None = None,
        valor_nuevo: dict | None = None,
    ) -> AuditLog:
        nuevo = AuditLog(
            usuario_id=usuario_id,
            accion=accion,
            recurso=recurso,
            detalles=detalles,
            valor_anterior=json.dumps(valor_anterior, default=str) if valor_anterior else None,
            valor_nuevo=json.dumps(valor_nuevo, default=str) if valor_nuevo else None,
        )
        self.db.add(nuevo)
        self.db.commit()
        return nuevo
