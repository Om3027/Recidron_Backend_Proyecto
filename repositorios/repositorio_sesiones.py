from datetime import datetime
from sqlalchemy.orm import Session
from models import Session as SesionModel, User, Role


class RepositorioSesiones:
    """
    Capa de acceso a datos para la tabla `sesiones`.
    Solo contiene consultas SQLAlchemy — sin lógica de negocio.
    """

    def __init__(self, db: Session):
        self.db = db

    def obtener_todas(self) -> list[SesionModel]:
        return self.db.query(SesionModel).order_by(SesionModel.id).all()

    def obtener_por_id(self, sesion_id: int) -> SesionModel | None:
        return self.db.query(SesionModel).filter(SesionModel.id == sesion_id).first()

    def obtener_activa_por_id(self, sesion_id: int) -> SesionModel | None:
        return self.db.query(SesionModel).filter(
            SesionModel.id == sesion_id, SesionModel.activa == True
        ).first()

    def obtener_por_token(self, token: str) -> SesionModel | None:
        """Busca una sesión válida y no expirada, con usuario y rol cargados."""
        return (
            self.db.query(SesionModel)
            .join(User)
            .join(Role)
            .filter(
                SesionModel.token == token,
                SesionModel.activa == True,
                SesionModel.expira_en > datetime.now(),
                User.es_activo == True,
            )
            .first()
        )

    def crear(self, usuario_id: int, token: str, expira_en: datetime) -> SesionModel:
        nueva = SesionModel(
            usuario_id=usuario_id,
            token=token,
            expira_en=expira_en,
        )
        self.db.add(nueva)
        self.db.commit()
        self.db.refresh(nueva)
        return nueva

    def cerrar_sesion(self, sesion: SesionModel) -> None:
        sesion.activa = False
        self.db.commit()
