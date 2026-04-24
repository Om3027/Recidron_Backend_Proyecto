from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db
from servicios import ServicioEstadisticas
from routes.auth import verificar_permiso

router_stats = APIRouter(prefix="/stats", tags=["Estadísticas"])


@router_stats.get("/dashboard", dependencies=[Depends(verificar_permiso("reportes:leer"))])
def obtener_estadisticas_dashboard(db: Session = Depends(get_db)):
    """Obtiene KPIs globales y distribuciones para el dashboard del administrador."""
    return ServicioEstadisticas(db).obtener_dashboard()


@router_stats.get("/tendencia", dependencies=[Depends(verificar_permiso("reportes:leer"))])
def obtener_tendencia_reportes(db: Session = Depends(get_db)):
    """Obtiene el conteo de reportes diarios de los últimos 30 días."""
    return ServicioEstadisticas(db).obtener_tendencia()
