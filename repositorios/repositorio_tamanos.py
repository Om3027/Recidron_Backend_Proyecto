from sqlalchemy.orm import Session
from models import Tamano


class RepositorioTamanos:
    """
    Capa de acceso a datos para la tabla `tamanos`.
    Solo contiene consultas SQLAlchemy — sin lógica de negocio.
    """

    def __init__(self, db: Session):
        self.db = db

    def obtener_todos_activos(self) -> list[Tamano]:
        return self.db.query(Tamano).filter(Tamano.es_activo == True).order_by(Tamano.id).all()

    def obtener_activo_por_id(self, tamano_id: int) -> Tamano | None:
        return self.db.query(Tamano).filter(Tamano.id == tamano_id, Tamano.es_activo == True).first()

    def crear(self, nombre_tamano: str) -> Tamano:
        nuevo = Tamano(nombre_tamano=nombre_tamano)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def actualizar_nombre(self, tamano: Tamano, nombre_tamano: str) -> Tamano:
        tamano.nombre_tamano = nombre_tamano
        self.db.commit()
        return tamano

    def desactivar(self, tamano: Tamano) -> None:
        tamano.es_activo = False
        self.db.commit()
