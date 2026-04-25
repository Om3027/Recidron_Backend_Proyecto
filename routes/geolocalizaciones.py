from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db
from servicios import ServicioGeolocalizaciones
from validators import GeoCreate, GeoUpdate
from routes.auth import verificar_permiso

router_geos = APIRouter(prefix="/geos", tags=[" Geolocalizaciones"])


@router_geos.get("/", summary="Listar geolocalizaciones")
def listar_geos(usuario_auth: dict = Depends(verificar_permiso("reportes:leer")), db: Session = Depends(get_db)):
    """Lista coordenadas GPS de reportes activos."""
    return ServicioGeolocalizaciones(db).listar_todas()


@router_geos.post("/", status_code=201, summary="Registrar geolocalización")
def crear_geo(geo: GeoCreate, usuario_auth: dict = Depends(verificar_permiso("reportes:crear")), db: Session = Depends(get_db)):
    """Asocia coordenadas GPS a un reporte con auditoría."""
    return ServicioGeolocalizaciones(db).crear(geo.dict(), usuario_auth["id"])


@router_geos.get("/{id}", summary="Obtener geolocalización por ID")
def obtener_geo(id: int, usuario_auth: dict = Depends(verificar_permiso("reportes:leer")), db: Session = Depends(get_db)):
    return ServicioGeolocalizaciones(db).obtener_por_id(id)


@router_geos.put("/{id}", summary="Actualizar geolocalización")
def actualizar_geo(id: int, datos: GeoUpdate, usuario_auth: dict = Depends(verificar_permiso("reportes:editar")), db: Session = Depends(get_db)):
    """Actualiza coordenadas GPS con auditoría."""
    return ServicioGeolocalizaciones(db).actualizar(id, datos.dict(), usuario_auth["id"])


@router_geos.delete("/{id}", summary="Eliminar geolocalización")
def eliminar_geo(id: int, usuario_auth: dict = Depends(verificar_permiso("reportes:eliminar")), db: Session = Depends(get_db)):
    """Elimina físicamente la geolocalización."""
    return ServicioGeolocalizaciones(db).eliminar(id, usuario_auth["id"])
