from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from models import get_db
from servicios import ServicioReportes
from validators import ReporteCreate, ReporteUpdate
from routes.auth import verificar_permiso
from utils.pdf_export import generar_pdf_reportes

router_reportes = APIRouter(prefix="/reportes", tags=[" Reportes"])


@router_reportes.get("/", summary="Listar todos los reportes")
def listar_reportes(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), usuario: dict = Depends(verificar_permiso("reportes:leer")), db: Session = Depends(get_db)):
    """Consulta todos los reportes activos con nombres de catálogos y paginación."""
    return ServicioReportes(db).listar_todos(skip=skip, limit=limit)


@router_reportes.post("/", status_code=201, summary="Crear un reporte")
def crear_reporte(reporte: ReporteCreate, usuario: dict = Depends(verificar_permiso("reportes:crear")), db: Session = Depends(get_db)):
    """Registra un nuevo reporte de residuo con auditoría."""
    return ServicioReportes(db).crear(reporte.dict(), usuario["id"])


@router_reportes.get("/stats/my", summary="Estadísticas de mis reportes")
def obtener_mis_estadisticas(usuario: dict = Depends(verificar_permiso("reportes:leer")), db: Session = Depends(get_db)):
    """Retorna un resumen de la actividad del usuario autenticado."""
    return ServicioReportes(db).mis_estadisticas(usuario["id"])


@router_reportes.get("/exportar/pdf", summary="Exportar reportes a PDF")
def exportar_reportes_pdf(usuario: dict = Depends(verificar_permiso("reportes:leer")), db: Session = Depends(get_db)):
    """Genera y descarga un archivo PDF con todos los reportes del sistema."""
    # Obtenemos un límite amplio para la exportación
    reportes = ServicioReportes(db).listar_todos(skip=0, limit=1000)
    
    pdf_buffer = generar_pdf_reportes(reportes, usuario)
    
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": "attachment; filename=reportes_recidron.pdf"}
    )


@router_reportes.get("/{id}", summary="Obtener reporte por ID")
def obtener_reporte(id: int, usuario: dict = Depends(verificar_permiso("reportes:leer")), db: Session = Depends(get_db)):
    """Retorna un reporte específico que esté activo."""
    return ServicioReportes(db).obtener_por_id(id)


@router_reportes.put("/{id}", summary="Actualizar reporte")
def actualizar_reporte(id: int, datos: ReporteUpdate, usuario: dict = Depends(verificar_permiso("reportes:editar")), db: Session = Depends(get_db)):
    """Modifica los datos de un reporte activo con auditoría."""
    return ServicioReportes(db).actualizar(id, datos.dict(), usuario["id"])


@router_reportes.delete("/{id}", summary="Eliminar reporte (Soft-Delete)")
def desactivar_reporte(id: int, usuario: dict = Depends(verificar_permiso("reportes:eliminar")), db: Session = Depends(get_db)):
    """Realiza un borrado lógico del reporte."""
    return ServicioReportes(db).desactivar(id, usuario["id"])


@router_reportes.post("/{id}/foto", summary="Subir o actualizar foto del reporte")
def subir_foto_reporte(id: int, file: UploadFile = File(...), usuario: dict = Depends(verificar_permiso("reportes:crear")), db: Session = Depends(get_db)):
    """Sube una imagen a Cloudinary y la asocia al reporte (1:1)."""
    archivo_bytes = file.file.read()
    return ServicioReportes(db).agregar_o_actualizar_foto(id, archivo_bytes, usuario["id"])
