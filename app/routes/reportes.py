from fastapi import APIRouter, HTTPException
from app.services.reportes_service import ReporteService
from app.services.seguridad_service import UserService
from app.services.pgc_service import TipoResiduoService, MaterialService, ZonaCampusService, TamanoService
from app.validators import ReporteCreate, ReporteUpdate
from app.routes.utils import error_404

router_reportes = APIRouter(prefix="/reportes", tags=[" Reportes"])

@router_reportes.get("/", summary="Listar todos los reportes")
def listar_reportes():
    """Consulta todos los reportes de residuos registrados."""
    service = ReporteService()
    reportes = service.get_all()
    return [{k: v for k, v in r.__dict__.items() if k != '_sa_instance_state'} for r in reportes]

@router_reportes.post("/", status_code=201, summary="Crear un reporte")
def crear_reporte(reporte: ReporteCreate):
    """Registra un nuevo reporte de residuo."""
    user_service = UserService()
    tipo_service = TipoResiduoService()
    mat_service = MaterialService()
    zona_service = ZonaCampusService()
    tam_service = TamanoService()
    reporte_service = ReporteService()

    if not user_service.get_by_id(reporte.usuario_id):
        raise HTTPException(status_code=404, detail=f"Usuario con id {reporte.usuario_id} no existe")
    if not tipo_service.get_by_id(reporte.tipo_residuo_id):
        raise HTTPException(status_code=404, detail=f"TipoResiduo con id {reporte.tipo_residuo_id} no existe")
    if not mat_service.get_by_id(reporte.material_id):
        raise HTTPException(status_code=404, detail=f"Material con id {reporte.material_id} no existe")
    if not zona_service.get_by_id(reporte.zona_id):
        raise HTTPException(status_code=404, detail=f"Zona con id {reporte.zona_id} no existe")
    if not tam_service.get_by_id(reporte.tamano_id):
        raise HTTPException(status_code=404, detail=f"Tamano con id {reporte.tamano_id} no existe")

    nuevo_reporte = reporte_service.create(reporte.dict())
    return {"id": nuevo_reporte.id, **reporte.dict()}

@router_reportes.get("/{id}", summary="Obtener reporte por ID")
def obtener_reporte(id: int):
    """Retorna un reporte específico con todos sus detalles."""
    service = ReporteService()
    r = service.get_by_id(id)
    if not r: error_404("Reporte", id)
    return {k: v for k, v in r.__dict__.items() if k != '_sa_instance_state'}

@router_reportes.put("/{id}", summary="Actualizar reporte")
def actualizar_reporte(id: int, datos: ReporteUpdate):
    """Modifica los datos de un reporte existente."""
    service = ReporteService()
    if not service.get_by_id(id):
        error_404("Reporte", id)
    campos = {k: v for k, v in datos.dict().items() if v is not None}
    if campos:
        service.update(id, campos)
    return {"mensaje": f"Reporte {id} actualizado", "campos": list(campos.keys())}

@router_reportes.delete("/{id}", summary="Eliminar reporte")
def eliminar_reporte(id: int):
    """Elimina un reporte de residuo."""
    service = ReporteService()
    if not service.get_by_id(id):
        error_404("Reporte", id)
    service.delete(id)
    return {"mensaje": f"Reporte {id} eliminado exitosamente"}
