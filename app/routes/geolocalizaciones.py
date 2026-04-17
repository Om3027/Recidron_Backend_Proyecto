import pymysql
from fastapi import APIRouter, HTTPException
from app import models
from app.validators import GeoCreate, GeoUpdate
from app.routes.utils import error_404

router_geos = APIRouter(prefix="/geolocalizaciones", tags=[" Geolocalizaciones"])

@router_geos.get("/", summary="Listar geolocalizaciones")
def listar_geos():
    """Consulta todas las coordenadas GPS registradas."""
    return models.get_all_geos()

@router_geos.post("/", status_code=201, summary="Registrar geolocalización")
def crear_geo(geo: GeoCreate):
    """Registra las coordenadas GPS de un reporte."""
    if not models.get_report_by_id(geo.reporte_id):
        raise HTTPException(status_code=404, detail="El reporte no existe")
    try:
        nuevo_id = models.create_geo(geo.latitud, geo.longitud, geo.altitud, geo.precision_gps, geo.reporte_id)
        return {"id": nuevo_id, **geo.dict()}
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=422, detail="Este reporte ya tiene geolocalización")

@router_geos.get("/{id}", summary="Obtener geolocalización por ID")
def obtener_geo(id: int):
    g = models.get_geo_by_id(id)
    if not g: error_404("Geolocalizacion", id)
    return g

@router_geos.put("/{id}", summary="Actualizar geolocalización")
def actualizar_geo(id: int, datos: GeoUpdate):
    if not models.get_geo_by_id(id):
        error_404("Geolocalizacion", id)
    campos = {k: v for k, v in datos.dict().items() if v is not None}
    if campos:
        models.update_geo(id, campos)
    return {"mensaje": f"Geolocalizacion {id} actualizada"}

@router_geos.delete("/{id}", summary="Eliminar geolocalización")
def eliminar_geo(id: int):
    if not models.get_geo_by_id(id):
        error_404("Geolocalizacion", id)
    models.delete_geo(id)
    return {"mensaje": f"Geolocalizacion {id} eliminada exitosamente"}
