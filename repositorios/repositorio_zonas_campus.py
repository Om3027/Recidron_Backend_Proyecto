from sqlalchemy.orm import Session
from models import ZonaCampus


class RepositorioZonasCampus:
    """
    Capa de acceso a datos para la tabla `zonas_campus`.
    Solo contiene consultas SQLAlchemy — sin lógica de negocio.
    """

    def __init__(self, db: Session):
        self.db = db

    def obtener_todas_activas(self) -> list[ZonaCampus]:
        return self.db.query(ZonaCampus).filter(ZonaCampus.es_activo == True).order_by(ZonaCampus.id).all()

    def obtener_activa_por_id(self, zona_id: int) -> ZonaCampus | None:
        return self.db.query(ZonaCampus).filter(ZonaCampus.id == zona_id, ZonaCampus.es_activo == True).first()

    def crear(self, nombre_zona: str) -> ZonaCampus:
        nueva = ZonaCampus(nombre_zona=nombre_zona)
        self.db.add(nueva)
        self.db.commit()
        self.db.refresh(nueva)
        return nueva

    def actualizar_nombre(self, zona: ZonaCampus, nombre_zona: str) -> ZonaCampus:
        zona.nombre_zona = nombre_zona
        self.db.commit()
        return zona

    def desactivar(self, zona: ZonaCampus) -> None:
        zona.es_activo = False
        self.db.commit()
