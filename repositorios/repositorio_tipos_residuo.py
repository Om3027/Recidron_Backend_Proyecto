from sqlalchemy.orm import Session
from models import TipoResiduo


class RepositorioTiposResiduo:
    """
    Capa de acceso a datos para la tabla `tipos_residuo`.
    Solo contiene consultas SQLAlchemy — sin lógica de negocio.
    """

    def __init__(self, db: Session):
        self.db = db

    def obtener_todos_activos(self) -> list[TipoResiduo]:
        return self.db.query(TipoResiduo).filter(TipoResiduo.es_activo == True).order_by(TipoResiduo.id).all()

    def obtener_activo_por_id(self, tipo_id: int) -> TipoResiduo | None:
        return self.db.query(TipoResiduo).filter(TipoResiduo.id == tipo_id, TipoResiduo.es_activo == True).first()

    def crear(self, nombre_tipo: str) -> TipoResiduo:
        nuevo = TipoResiduo(nombre_tipo=nombre_tipo)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def actualizar_nombre(self, tipo: TipoResiduo, nombre_tipo: str) -> TipoResiduo:
        tipo.nombre_tipo = nombre_tipo
        self.db.commit()
        return tipo

    def desactivar(self, tipo: TipoResiduo) -> None:
        tipo.es_activo = False
        self.db.commit()
