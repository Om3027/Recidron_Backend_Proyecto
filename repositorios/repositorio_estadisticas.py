from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Reporte, User, TipoResiduo, ZonaCampus, Material


class RepositorioEstadisticas:
    """
    Capa de acceso a datos para consultas estadísticas agregadas del sistema.
    Solo contiene consultas SQLAlchemy — sin lógica de negocio.
    """

    def __init__(self, db: Session):
        self.db = db

    def contar_reportes_activos(self) -> int:
        return self.db.query(Reporte).filter(Reporte.es_activo == True).count()

    def contar_usuarios_activos(self) -> int:
        return self.db.query(User).filter(User.es_activo == True).count()

    def distribucion_por_tipo_residuo(self):
        return (
            self.db.query(
                TipoResiduo.nombre_tipo.label("label"),
                func.count(Reporte.id).label("value"),
            )
            .outerjoin(Reporte, (TipoResiduo.id == Reporte.tipo_residuo_id) & (Reporte.es_activo == True))
            .filter(TipoResiduo.es_activo == True)
            .group_by(TipoResiduo.id, TipoResiduo.nombre_tipo)
            .all()
        )

    def distribucion_por_zona_campus(self):
        return (
            self.db.query(
                ZonaCampus.nombre_zona.label("label"),
                func.count(Reporte.id).label("value"),
            )
            .outerjoin(Reporte, (ZonaCampus.id == Reporte.zona_id) & (Reporte.es_activo == True))
            .filter(ZonaCampus.es_activo == True)
            .group_by(ZonaCampus.id, ZonaCampus.nombre_zona)
            .all()
        )

    def distribucion_por_material(self, limite: int = 5):
        return (
            self.db.query(
                Material.nombre_material.label("label"),
                func.count(Reporte.id).label("value"),
            )
            .outerjoin(Reporte, (Material.id == Reporte.material_id) & (Reporte.es_activo == True))
            .filter(Material.es_activo == True)
            .group_by(Material.id, Material.nombre_material)
            .order_by(func.count(Reporte.id).desc())
            .limit(limite)
            .all()
        )

    def tendencia_ultimos_30_dias(self):
        hace_30_dias = datetime.now() - timedelta(days=30)
        return (
            self.db.query(
                func.date(Reporte.fecha_reporte).label("fecha"),
                func.count(Reporte.id).label("cantidad"),
            )
            .filter(Reporte.es_activo == True, Reporte.fecha_reporte >= hace_30_dias)
            .group_by(func.date(Reporte.fecha_reporte))
            .order_by(func.date(Reporte.fecha_reporte).asc())
            .all()
        )
