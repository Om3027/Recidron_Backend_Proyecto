from fastapi import APIRouter, HTTPException
from app.services.reportes_service import GeolocalizacionService, ReporteService
from app.validators import GeoCreate, GeoUpdate
from app.routes.utils import error_404
from sqlalchemy.exc import IntegrityError

router_geos = APIRouter(prefix="/geolocalizaciones", tags=[" Geolocalizaciones"])

@router_geos.get("/", summary="Listar geolocalizaciones")
def listar_geos():
    """Consulta todas las coordenadas GPS registradas."""
    service = GeolocalizacionService()
    geos = service.get_all()
    return [{k: v for k, v in g.__dict__.items() if k != '_sa_instance_state'} for g in geos]

@router_geos.post("/", status_code=201, summary="Registrar geolocalización")
def crear_geo(geo: GeoCreate):
    """Registra las coordenadas GPS de un reporte."""
    reporte_service = ReporteService()
    geo_service = GeolocalizacionService()
    
    if not reporte_service.get_by_id(geo.reporte_id):
        raise HTTPException(status_code=404, detail="El reporte no existe")
    try:
        nueva_geo = geo_service.create(geo.dict())
        return {"id": nueva_geo.id, **geo.dict()}
    except IntegrityError:
        raise HTTPException(status_code=422, detail="Este reporte ya tiene geolocalización")

@router_geos.get("/{id}", summary="Obtener geolocalización por ID")
def obtener_geo(id: int):
    service = GeolocalizacionService()
    g = service.get_by_id(id)
    if not g: error_404("Geolocalizacion", id)
    return {k: v for k, v in g.__dict__.items() if k != '_sa_instance_state'}

@router_geos.put("/{id}", summary="Actualizar geolocalización")
def actualizar_geo(id: int, datos: GeoUpdate):
    service = GeolocalizacionService()
    if not service.get_by_id(id):
        error_404("Geolocalizacion", id)
    campos = {k: v for k, v in datos.dict().items() if v is not None}
    if campos:
        service.update(id, campos)
    return {"mensaje": f"Geolocalizacion {id} actualizada"}

@router_geos.delete("/{id}", summary="Eliminar geolocalización")
def eliminar_geo(id: int):
    service = GeolocalizacionService()
    if not service.get_by_id(id):
        error_404("Geolocalizacion", id)
    service.delete(id)
    return {"mensaje": f"Geolocalizacion {id} eliminada exitosamente"}
