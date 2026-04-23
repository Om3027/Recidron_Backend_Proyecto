from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Role


class RepositorioRoles:
    """
    Capa de acceso a datos para la tabla `roles`.
    Solo contiene consultas SQLAlchemy — sin lógica de negocio.
    """

    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self) -> list[Role]:
        return self.db.query(Role).order_by(Role.id).all()

    def obtener_por_id(self, rol_id: int) -> Role | None:
        return self.db.query(Role).filter(Role.id == rol_id).first()

    def obtener_por_nombre(self, nombre: str) -> Role | None:
        return self.db.query(Role).filter(Role.nombre_rol == nombre).first()

    def crear(self, nombre_rol: str) -> Role:
        nuevo = Role(nombre_rol=nombre_rol)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo
