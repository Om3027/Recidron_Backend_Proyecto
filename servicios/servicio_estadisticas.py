from fastapi import HTTPException
from sqlalchemy.orm import Session
from repositorios import RepositorioEstadisticas


class ServicioEstadisticas:
    """
    Capa de negocio para estadísticas del dashboard.
    Orquesta las consultas usando el repositorio de estadísticas.
    """

    def __init__(self, db: Session):
        self.repositorio_estadisticas = RepositorioEstadisticas(db)

    def obtener_dashboard(self) -> dict:
        try:
            total_reportes = self.repositorio_estadisticas.contar_reportes_activos()
            total_usuarios = self.repositorio_estadisticas.contar_usuarios_activos()
            dist_tipos     = self.repositorio_estadisticas.distribucion_por_tipo_residuo()
            dist_zonas     = self.repositorio_estadisticas.distribucion_por_zona_campus()
            dist_mats      = self.repositorio_estadisticas.distribucion_por_material()

            return {
                "total_reportes":          total_reportes,
                "usuarios_activos":        total_usuarios,
                "distribucion_tipos":      [{"label": r.label, "value": r.value} for r in dist_tipos],
                "distribucion_zonas":      [{"label": r.label, "value": r.value} for r in dist_zonas],
                "distribucion_materiales": [{"label": r.label, "value": r.value} for r in dist_mats],
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al calcular estadísticas: {str(e)}")

    def obtener_tendencia(self) -> list:
        try:
            tendencia = self.repositorio_estadisticas.tendencia_ultimos_30_dias()
            return [{"fecha": t.fecha, "cantidad": t.cantidad} for t in tendencia]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
