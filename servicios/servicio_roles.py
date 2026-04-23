from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from repositorios import RepositorioRoles, RepositorioLogs


class ServicioRoles:
    """
    Capa de negocio para roles.
    Orquesta las operaciones usando los repositorios correspondientes.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repositorio_roles = RepositorioRoles(db)
        self.repositorio_logs  = RepositorioLogs(db)

    def listar_todos(self) -> list:
        return self.repositorio_roles.obtener_todos()

    def obtener_por_id(self, rol_id: int):
        rol = self.repositorio_roles.obtener_por_id(rol_id)
        if not rol:
            raise HTTPException(status_code=404, detail=f"Rol con id {rol_id} no encontrado")
        return rol

    def crear(self, nombre_rol: str, usuario_id: int) -> dict:
        try:
            nuevo = self.repositorio_roles.crear(nombre_rol)
            self.repositorio_logs.registrar(
                usuario_id, "CREAR", "roles",
                f"Rol {nuevo.id} creado: {nuevo.nombre_rol}"
            )
            return {"id": nuevo.id, "nombre_rol": nuevo.nombre_rol}
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=422, detail="El rol ya existe")
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Error al crear el rol")
