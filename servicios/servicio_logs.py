from fastapi import HTTPException
from sqlalchemy.orm import Session
from repositorios import RepositorioLogs


class ServicioLogs:
    """
    Capa de negocio para logs de auditoría.
    Orquesta las operaciones usando el repositorio correspondiente.
    """

    def __init__(self, db: Session):
        self.repositorio_logs = RepositorioLogs(db)

    def listar_todos(self) -> list:
        return self.repositorio_logs.obtener_todos()

    def obtener_por_id(self, log_id: int):
        log = self.repositorio_logs.obtener_por_id(log_id)
        if not log:
            raise HTTPException(status_code=404, detail="Log de auditoría no encontrado")
        return log
