from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from models import get_db
from servicios import ServicioEstadisticas, ServicioReportes
from routes.auth import verificar_permiso
from utils.pdf_export import generar_pdf_resumen

router_stats = APIRouter(prefix="/stats", tags=["Estadísticas"])


@router_stats.get("/dashboard", dependencies=[Depends(verificar_permiso("reportes:leer"))])
def obtener_estadisticas_dashboard(db: Session = Depends(get_db)):
    """Obtiene KPIs globales y distribuciones para el dashboard del administrador."""
    return ServicioEstadisticas(db).obtener_dashboard()


@router_stats.get("/tendencia", dependencies=[Depends(verificar_permiso("reportes:leer"))])
def obtener_tendencia_reportes(db: Session = Depends(get_db)):
    """Obtiene el conteo de reportes diarios de los últimos 30 días."""
    return ServicioEstadisticas(db).obtener_tendencia()


@router_stats.get("/exportar/pdf", summary="Exportar resumen del dashboard a PDF")
def exportar_dashboard_pdf(usuario: dict = Depends(verificar_permiso("reportes:leer")), db: Session = Depends(get_db)):
    stats = ServicioEstadisticas(db).obtener_dashboard()
    trends = ServicioEstadisticas(db).obtener_tendencia()
    recent_reports = ServicioReportes(db).listar_todos(skip=0, limit=5)
    
    pdf_buffer = generar_pdf_resumen(stats, trends, recent_reports, usuario)
    
    return Response(
        content=pdf_buffer.getvalue(), 
        media_type="application/pdf", 
        headers={"Content-Disposition": "attachment; filename=resumen_recidron.pdf"}
    )
