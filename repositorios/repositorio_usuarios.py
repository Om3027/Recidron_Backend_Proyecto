from sqlalchemy.orm import Session
from models import User, Role, Permission


class RepositorioUsuarios:
    """
    Capa de acceso a datos para la tabla `usuarios`.
    Solo contiene consultas SQLAlchemy — sin lógica de negocio.
    """

    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self) -> list[User]:
        return self.db.query(User).order_by(User.id).all()

    def obtener_todos_activos(self) -> list[User]:
        return self.db.query(User).filter(User.es_activo == True).order_by(User.id).all()

    def obtener_por_id(self, usuario_id: int) -> User | None:
        return self.db.query(User).filter(User.id == usuario_id).first()

    def obtener_activo_por_id(self, usuario_id: int) -> User | None:
        return self.db.query(User).filter(User.id == usuario_id, User.es_activo == True).first()

    def obtener_por_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def rol_tiene_permiso(self, rol_id: int, nombre_permiso: str) -> bool:
        resultado = (
            self.db.query(Role)
            .join(Role.permisos)
            .filter(Role.id == rol_id, Permission.nombre_permiso == nombre_permiso)
            .first()
        )
        return resultado is not None

    def crear(self, nombre: str, email: str, password_hash: str,
              rol_id: int, codigo_estudiantil: str | None = None) -> User:
        nuevo = User(
            nombre=nombre,
            email=email,
            password=password_hash,
            codigo_estudiantil=codigo_estudiantil,
            rol_id=rol_id,
        )
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def actualizar(self, usuario: User, campos: dict) -> User:
        for k, v in campos.items():
            setattr(usuario, k, v)
        self.db.commit()
        return usuario

    def desactivar(self, usuario: User) -> None:
        usuario.es_activo = False
        self.db.commit()
