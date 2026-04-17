import pymysql
from fastapi import APIRouter, HTTPException
from app import models
from app.validators import TamanoCreate
from app.routes.utils import error_404

router_tamanos = APIRouter(prefix="/tamanos", tags=[" Tamaños"])

@router_tamanos.get("/", summary="Listar tamaños")
def listar_tamanos():
    return models.get_all_sizes()

@router_tamanos.post("/", status_code=201, summary="Crear tamaño")
def crear_tamano(tamano: TamanoCreate):
    try:
        nuevo_id = models.create_size(tamano.nombre_tamano)
        return {"id": nuevo_id, "nombre_tamano": tamano.nombre_tamano}
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=422, detail="El tamaño ya existe")

@router_tamanos.get("/{id}", summary="Obtener tamaño por ID")
def obtener_tamano(id: int):
    t = models.get_size_by_id(id)
    if not t: error_404("Tamano", id)
    return t

@router_tamanos.put("/{id}", summary="Actualizar tamaño")
def actualizar_tamano(id: int, tamano: TamanoCreate):
    if not models.get_size_by_id(id):
        error_404("Tamano", id)
    models.update_size(id, tamano.nombre_tamano)
    return {"id": id, "nombre_tamano": tamano.nombre_tamano}

@router_tamanos.delete("/{id}", summary="Eliminar tamaño")
def eliminar_tamano(id: int):
    if not models.get_size_by_id(id):
        error_404("Tamano", id)
    models.delete_size(id)
    return {"mensaje": f"Tamano {id} eliminado exitosamente"}
