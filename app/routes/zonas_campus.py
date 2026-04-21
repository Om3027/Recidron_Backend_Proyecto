from fastapi import APIRouter, HTTPException
from app.services.pgc_service import ZonaCampusService
from app.validators import ZonaCampusCreate
from app.routes.utils import error_404
from sqlalchemy.exc import IntegrityError

router_zonas = APIRouter(prefix="/zonas", tags=[" Zonas del Campus"])

@router_zonas.get("/", summary="Listar zonas del campus")
def listar_zonas():
    service = ZonaCampusService()
    zonas = service.get_all()
    return [{k: v for k, v in z.__dict__.items() if k != '_sa_instance_state'} for z in zonas]

@router_zonas.post("/", status_code=201, summary="Crear zona")
def crear_zona(zona: ZonaCampusCreate):
    service = ZonaCampusService()
    try:
        nuevo = service.create(zona.dict())
        return {"id": nuevo.id, "nombre_zona": nuevo.nombre_zona}
    except IntegrityError:
        raise HTTPException(status_code=422, detail="La zona ya existe")

@router_zonas.get("/{id}", summary="Obtener zona por ID")
def obtener_zona(id: int):
    service = ZonaCampusService()
    z = service.get_by_id(id)
    if not z: error_404("ZonaCampus", id)
    return {k: v for k, v in z.__dict__.items() if k != '_sa_instance_state'}

@router_zonas.put("/{id}", summary="Actualizar zona")
def actualizar_zona(id: int, zona: ZonaCampusCreate):
    service = ZonaCampusService()
    if not service.get_by_id(id):
        error_404("ZonaCampus", id)
    service.update(id, zona.dict())
    return {"id": id, "nombre_zona": zona.nombre_zona}

@router_zonas.delete("/{id}", summary="Eliminar zona")
def eliminar_zona(id: int):
    service = ZonaCampusService()
    if not service.get_by_id(id):
        error_404("ZonaCampus", id)
    service.delete(id)
    return {"mensaje": f"Zona {id} eliminada exitosamente"}
