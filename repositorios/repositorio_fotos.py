from sqlalchemy.orm import Session
from models.project import FotoReporte

class RepositorioFotos:
    """
    Maneja las operaciones de base de datos para la entidad FotoReporte.
    """
    def __init__(self, db: Session):
        self.db = db

    def obtener_por_reporte(self, reporte_id: int):
        """Busca la foto asociada a un reporte por su ID."""
        return self.db.query(FotoReporte).filter(FotoReporte.reporte_id == reporte_id).first()

    def guardar_o_actualizar(self, reporte_id: int, url: str):
        """
        Guarda una nueva foto o actualiza la URL si el reporte ya tiene una.
        Implementa la relación 1:1.
        """
        foto = self.obtener_por_reporte(reporte_id)
        if foto:
            foto.url = url
        else:
            foto = FotoReporte(reporte_id=reporte_id, url=url)
            self.db.add(foto)
            
        self.db.commit()
        self.db.refresh(foto)
        return foto
