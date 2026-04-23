from sqlalchemy.orm import Session
from models import Material


class RepositorioMateriales:
    """
    Capa de acceso a datos para la tabla `materiales`.
    Solo contiene consultas SQLAlchemy — sin lógica de negocio.
    """

    def __init__(self, db: Session):
        self.db = db

    def obtener_todos_activos(self) -> list[Material]:
        return self.db.query(Material).filter(Material.es_activo == True).order_by(Material.id).all()

    def obtener_activo_por_id(self, material_id: int) -> Material | None:
        return self.db.query(Material).filter(Material.id == material_id, Material.es_activo == True).first()

    def crear(self, nombre_material: str) -> Material:
        nuevo = Material(nombre_material=nombre_material)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def actualizar_nombre(self, material: Material, nombre_material: str) -> Material:
        material.nombre_material = nombre_material
        self.db.commit()
        return material

    def desactivar(self, material: Material) -> None:
        material.es_activo = False
        self.db.commit()
