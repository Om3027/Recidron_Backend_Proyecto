from sqlalchemy.orm import Session
from models import Geolocalizacion, Reporte


class RepositorioGeolocalizaciones:
    """
    Capa de acceso a datos para la tabla `geolocalizaciones`.
    Solo contiene consultas SQLAlchemy — sin lógica de negocio.
    """

    def __init__(self, db: Session):
        self.db = db

    def obtener_todas_activas(self) -> list[Geolocalizacion]:
        return (
            self.db.query(Geolocalizacion)
            .join(Reporte)
            .filter(Reporte.es_activo == True)
            .all()
        )

    def obtener_por_id(self, geo_id: int) -> Geolocalizacion | None:
        return self.db.query(Geolocalizacion).filter(Geolocalizacion.id == geo_id).first()

    def crear(self, latitud: float, longitud: float, reporte_id: int,
              altitud: float | None = None, precision: float | None = None) -> Geolocalizacion:
        nueva = Geolocalizacion(
            latitud=latitud,
            longitud=longitud,
            altitud=altitud,
            precision=precision,
            reporte_id=reporte_id,
        )
        self.db.add(nueva)
        self.db.commit()
        self.db.refresh(nueva)
        return nueva

    def actualizar(self, geo: Geolocalizacion, campos: dict) -> Geolocalizacion:
        for k, v in campos.items():
            setattr(geo, k, v)
        self.db.commit()
        return geo

    def eliminar(self, geo: Geolocalizacion) -> None:
        self.db.delete(geo)
        self.db.commit()
