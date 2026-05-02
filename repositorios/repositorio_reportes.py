from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from models import Reporte, Material


class RepositorioReportes:
    """
    Capa de acceso a datos para la tabla `reportes`.
    Incluye eager loading para evitar el problema de N+1 queries.
    Solo contiene consultas SQLAlchemy — sin lógica de negocio.
    """

    def __init__(self, db: Session):
        self.db = db

    def obtener_todos_activos(self, skip: int = 0, limit: int = 10) -> list[Reporte]:
        """Trae todos los reportes activos junto con sus catálogos en una sola consulta SQL con paginación."""
        return (
            self.db.query(Reporte)
            .options(
                joinedload(Reporte.tipo_residuo),
                joinedload(Reporte.material),
                joinedload(Reporte.zona),
                joinedload(Reporte.tamano),
            )
            .filter(Reporte.es_activo == True)
            .order_by(Reporte.fecha_reporte.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def obtener_activo_por_id(self, reporte_id: int) -> Reporte | None:
        return (
            self.db.query(Reporte)
            .filter(Reporte.id == reporte_id, Reporte.es_activo == True)
            .first()
        )

    def crear(self, descripcion: str | None, usuario_id: int, tipo_residuo_id: int,
              material_id: int, zona_id: int, tamano_id: int) -> Reporte:
        nuevo = Reporte(
            descripcion=descripcion,
            usuario_id=usuario_id,
            tipo_residuo_id=tipo_residuo_id,
            material_id=material_id,
            zona_id=zona_id,
            tamano_id=tamano_id,
        )
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def actualizar(self, reporte: Reporte, campos: dict) -> Reporte:
        for k, v in campos.items():
            setattr(reporte, k, v)
        self.db.commit()
        return reporte

    def desactivar(self, reporte: Reporte) -> None:
        reporte.es_activo = False
        self.db.commit()

    # ── Consultas para estadísticas propias del usuario ──────────────────────

    def contar_por_usuario(self, usuario_id: int) -> int:
        return (
            self.db.query(Reporte)
            .filter(Reporte.usuario_id == usuario_id, Reporte.es_activo == True)
            .count()
        )

    def material_mas_frecuente_por_usuario(self, usuario_id: int):
        return (
            self.db.query(
                Material.nombre_material.label("material"),
                func.count(Reporte.id).label("cantidad"),
            )
            .join(Reporte, Material.id == Reporte.material_id)
            .filter(Reporte.usuario_id == usuario_id, Reporte.es_activo == True)
            .group_by(Material.id, Material.nombre_material)
            .order_by(func.count(Reporte.id).desc())
            .first()
        )

    def contar_zonas_distintas_por_usuario(self, usuario_id: int) -> int:
        return (
            self.db.query(func.count(func.distinct(Reporte.zona_id)))
            .filter(Reporte.usuario_id == usuario_id, Reporte.es_activo == True)
            .scalar()
        )
