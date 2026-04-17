from fastapi import APIRouter, HTTPException
from app import models
from app.validators import ReporteCreate, ReporteUpdate
from app.routes.utils import error_404

router_reportes = APIRouter(prefix="/reportes", tags=[" Reportes"])

@router_reportes.get("/", summary="Listar todos los reportes")
def listar_reportes():
    """Consulta todos los reportes de residuos registrados."""
    return models.get_all_reports()

@router_reportes.post("/", status_code=201, summary="Crear un reporte")
def crear_reporte(reporte: ReporteCreate):
    """Registra un nuevo reporte de residuo."""
    # Verificaciones de llaves foráneas usando los nuevos modelos
    if not models.get_user_by_id(reporte.usuario_id):
        raise HTTPException(status_code=404, detail=f"Usuario con id {reporte.usuario_id} no existe")
    if not models.get_type_by_id(reporte.tipo_residuo_id):
        raise HTTPException(status_code=404, detail=f"TipoResiduo con id {reporte.tipo_residuo_id} no existe")
    if not models.get_material_by_id(reporte.material_id):
        raise HTTPException(status_code=404, detail=f"Material con id {reporte.material_id} no existe")
    if not models.get_zone_by_id(reporte.zona_id):
        raise HTTPException(status_code=404, detail=f"Zona con id {reporte.zona_id} no existe")
    if not models.get_size_by_id(reporte.tamano_id):
        raise HTTPException(status_code=404, detail=f"Tamano con id {reporte.tamano_id} no existe")

    nuevo_id = models.create_report(
        reporte.descripcion, reporte.usuario_id, reporte.tipo_residuo_id,
        reporte.material_id, reporte.zona_id, reporte.tamano_id
    )
    return {"id": nuevo_id, **reporte.dict()}

@router_reportes.get("/{id}", summary="Obtener reporte por ID")
def obtener_reporte(id: int):
    """Retorna un reporte específico con todos sus detalles."""
    r = models.get_report_by_id(id)
    if not r: error_404("Reporte", id)
    return r

@router_reportes.put("/{id}", summary="Actualizar reporte")
def actualizar_reporte(id: int, datos: ReporteUpdate):
    """Modifica los datos de un reporte existente."""
    if not models.get_report_by_id(id):
        error_404("Reporte", id)
    campos = {k: v for k, v in datos.dict().items() if v is not None}
    if campos:
        models.update_report(id, campos)
    return {"mensaje": f"Reporte {id} actualizado", "campos": list(campos.keys())}

@router_reportes.delete("/{id}", summary="Eliminar reporte")
def eliminar_reporte(id: int):
    """Elimina un reporte de residuo."""
    if not models.get_report_by_id(id):
        error_404("Reporte", id)
    models.delete_report(id)
    return {"mensaje": f"Reporte {id} eliminado exitosamente"}
