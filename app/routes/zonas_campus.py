import pymysql
from fastapi import APIRouter, HTTPException
from app import models
from app.validators import ZonaCampusCreate
from app.routes.utils import error_404

router_zonas = APIRouter(prefix="/zonas", tags=[" Zonas del Campus"])

@router_zonas.get("/", summary="Listar zonas del campus")
def listar_zonas():
    return models.get_all_zones()

@router_zonas.post("/", status_code=201, summary="Crear zona")
def crear_zona(zona: ZonaCampusCreate):
    try:
        nuevo_id = models.create_zone(zona.nombre_zona)
        return {"id": nuevo_id, "nombre_zona": zona.nombre_zona}
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=422, detail="La zona ya existe")

@router_zonas.get("/{id}", summary="Obtener zona por ID")
def obtener_zona(id: int):
    z = models.get_zone_by_id(id)
    if not z: error_404("ZonaCampus", id)
    return z

@router_zonas.put("/{id}", summary="Actualizar zona")
def actualizar_zona(id: int, zona: ZonaCampusCreate):
    if not models.get_zone_by_id(id):
        error_404("ZonaCampus", id)
    models.update_zone(id, zona.nombre_zona)
    return {"id": id, "nombre_zona": zona.nombre_zona}

@router_zonas.delete("/{id}", summary="Eliminar zona")
def eliminar_zona(id: int):
    if not models.get_zone_by_id(id):
        error_404("ZonaCampus", id)
    models.delete_zone(id)
    return {"mensaje": f"Zona {id} eliminada exitosamente"}
