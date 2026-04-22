from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import get_db, Reporte, User, TipoResiduo, ZonaCampus, Material
from .auth import check_permission
from datetime import datetime, timedelta

# Router para manejar todas las consultas estadísticas del sistema
router_stats = APIRouter(prefix="/stats", tags=["Estadísticas"])

@router_stats.get("/dashboard", dependencies=[Depends(check_permission("reportes:leer"))])
def obtener_estadisticas_dashboard(db: Session = Depends(get_db)):
    """
    Breve descripción: Obtiene KPIs globales (conteo de reportes y usuarios) y 
    la distribución por tipo y zona para alimentar los gráficos del administrador.
    """
    try:
        # Conteos básicos (KPIs)
        total_reportes = db.query(Reporte).filter(Reporte.es_activo == True).count()
        total_usuarios = db.query(User).filter(User.es_activo == True).count()
        
        # Gráfico de Dona: Por tipo de residuo
        dist_tipos = db.query(TipoResiduo.nombre_tipo.label('label'), func.count(Reporte.id).label('value')) \
            .outerjoin(Reporte, (TipoResiduo.id == Reporte.tipo_residuo_id) & (Reporte.es_activo == True)) \
            .filter(TipoResiduo.es_activo == True) \
            .group_by(TipoResiduo.id, TipoResiduo.nombre_tipo) \
            .all()
        
        # Gráfico de Barras: Por zona del campus
        dist_zonas = db.query(ZonaCampus.nombre_zona.label('label'), func.count(Reporte.id).label('value')) \
            .outerjoin(Reporte, (ZonaCampus.id == Reporte.zona_id) & (Reporte.es_activo == True)) \
            .filter(ZonaCampus.es_activo == True) \
            .group_by(ZonaCampus.id, ZonaCampus.nombre_zona) \
            .all()

        # Gráfico de Barras Horizontales: Por material
        dist_materiales = db.query(Material.nombre_material.label('label'), func.count(Reporte.id).label('value')) \
            .outerjoin(Reporte, (Material.id == Reporte.material_id) & (Reporte.es_activo == True)) \
            .filter(Material.es_activo == True) \
            .group_by(Material.id, Material.nombre_material) \
            .order_by(func.count(Reporte.id).desc()) \
            .limit(5) \
            .all()

        return {
            "total_reportes": total_reportes,
            "usuarios_activos": total_usuarios,
            "distribucion_tipos": [{"label": r.label, "value": r.value} for r in dist_tipos],
            "distribucion_zonas": [{"label": r.label, "value": r.value} for r in dist_zonas],
            "distribucion_materiales": [{"label": r.label, "value": r.value} for r in dist_materiales]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular estadísticas: {str(e)}")

@router_stats.get("/tendencia", dependencies=[Depends(check_permission("reportes:leer"))])
def obtener_tendencia_reportes(db: Session = Depends(get_db)):
    """
    Breve descripción: Obtiene el conteo de reportes diarios de los últimos 30 días 
    para alimentar el gráfico de líneas (tendencia histórica).
    """
    try:
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # SQLAlchemy func.date may vary by dialect, func.date() works in MySQL
        tendencia = db.query(func.date(Reporte.fecha_reporte).label('fecha'), func.count(Reporte.id).label('cantidad')) \
            .filter(Reporte.es_activo == True, Reporte.fecha_reporte >= thirty_days_ago) \
            .group_by(func.date(Reporte.fecha_reporte)) \
            .order_by(func.date(Reporte.fecha_reporte).asc()) \
            .all()
            
        return [{"fecha": t.fecha, "cantidad": t.cantidad} for t in tendencia]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
