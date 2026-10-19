from typing import Optional
from sqlalchemy.orm import Session, joinedload
from models import SubzonaCampus, TipoSubzona


class RepositorioSubzonas:
    """
    Capa de acceso a datos para las tablas `subzonas_campus` y `tipos_subzona`.
    Solo contiene consultas SQLAlchemy — sin lógica de negocio.
    """

    def __init__(self, db: Session):
        self.db = db

    def obtener_todas_activas(
        self,
        zona_id: Optional[int] = None,
        tipo_id: Optional[int] = None,
        piso: Optional[str] = None
    ) -> list[SubzonaCampus]:
        """Obtiene subzonas activas con carga impaciente (eager load) del tipo de subzona."""
        query = (
            self.db.query(SubzonaCampus)
            .options(joinedload(SubzonaCampus.tipo_subzona))
            .filter(SubzonaCampus.es_activo == True)
        )

        if zona_id is not None:
            query = query.filter(SubzonaCampus.zona_id == zona_id)
        if tipo_id is not None:
            query = query.filter(SubzonaCampus.tipo_subzona_id == tipo_id)
        if piso is not None and piso != "" and piso != "all":
            query = query.filter(SubzonaCampus.piso == piso)

        return query.order_by(SubzonaCampus.piso.asc(), SubzonaCampus.nombre_subzona.asc()).all()

    def obtener_activa_por_id(self, subzona_id: int) -> Optional[SubzonaCampus]:
        """Obtiene una subzona activa específica por su ID."""
        return (
            self.db.query(SubzonaCampus)
            .options(joinedload(SubzonaCampus.tipo_subzona))
            .filter(SubzonaCampus.id == subzona_id, SubzonaCampus.es_activo == True)
            .first()
        )

    def obtener_tipos_activos(self) -> list[TipoSubzona]:
        """Obtiene todos los tipos de subzona activos ordenados."""
        return (
            self.db.query(TipoSubzona)
            .filter(TipoSubzona.es_activo == True)
            .order_by(TipoSubzona.id.asc())
            .all()
        )

    def crear(self, nombre_subzona: str, zona_id: int, tipo_subzona_id: int, piso: str = "1") -> SubzonaCampus:
        """Inserta una nueva subzona en la base de datos."""
        nueva = SubzonaCampus(
            nombre_subzona=nombre_subzona,
            zona_id=zona_id,
            tipo_subzona_id=tipo_subzona_id,
            piso=piso,
        )
        self.db.add(nueva)
        self.db.commit()
        self.db.refresh(nueva)
        return nueva
