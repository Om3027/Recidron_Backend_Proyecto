import pymysql
from fastapi import APIRouter, HTTPException
from app import models
from app.validators import TipoResiduoCreate
from app.routes.utils import error_404

router_tipos = APIRouter(prefix="/tipos-residuo", tags=[" Tipos de Residuo"])

@router_tipos.get("/", summary="Listar tipos de residuo")
def listar_tipos():
    return models.get_all_types()

@router_tipos.post("/", status_code=201, summary="Crear tipo de residuo")
def crear_tipo(tipo: TipoResiduoCreate):
    try:
        nuevo_id = models.create_type(tipo.nombre_tipo)
        return {"id": nuevo_id, "nombre_tipo": tipo.nombre_tipo}
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=422, detail="El tipo ya existe")

@router_tipos.get("/{id}", summary="Obtener tipo de residuo por ID")
def obtener_tipo(id: int):
    t = models.get_type_by_id(id)
    if not t: error_404("TipoResiduo", id)
    return t

@router_tipos.put("/{id}", summary="Actualizar tipo de residuo")
def actualizar_tipo(id: int, tipo: TipoResiduoCreate):
    if not models.get_type_by_id(id):
        error_404("TipoResiduo", id)
    models.update_type(id, tipo.nombre_tipo)
    return {"id": id, "nombre_tipo": tipo.nombre_tipo}

@router_tipos.delete("/{id}", summary="Eliminar tipo de residuo")
def eliminar_tipo(id: int):
    if not models.get_type_by_id(id):
        error_404("TipoResiduo", id)
    models.delete_type(id)
    return {"mensaje": f"TipoResiduo {id} eliminado exitosamente"}
