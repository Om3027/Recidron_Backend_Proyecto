from fastapi import APIRouter, HTTPException
from app.services.pgc_service import TipoResiduoService
from app.validators import TipoResiduoCreate
from app.routes.utils import error_404
from sqlalchemy.exc import IntegrityError

router_tipos = APIRouter(prefix="/tipos-residuo", tags=[" Tipos de Residuo"])

@router_tipos.get("/", summary="Listar tipos de residuo")
def listar_tipos():
    service = TipoResiduoService()
    tipos = service.get_all()
    return [{k: v for k, v in t.__dict__.items() if k != '_sa_instance_state'} for t in tipos]

@router_tipos.post("/", status_code=201, summary="Crear tipo de residuo")
def crear_tipo(tipo: TipoResiduoCreate):
    service = TipoResiduoService()
    try:
        nuevo = service.create(tipo.dict())
        return {"id": nuevo.id, "nombre_tipo": nuevo.nombre_tipo}
    except IntegrityError:
        raise HTTPException(status_code=422, detail="El tipo ya existe")

@router_tipos.get("/{id}", summary="Obtener tipo de residuo por ID")
def obtener_tipo(id: int):
    service = TipoResiduoService()
    t = service.get_by_id(id)
    if not t: error_404("TipoResiduo", id)
    return {k: v for k, v in t.__dict__.items() if k != '_sa_instance_state'}

@router_tipos.put("/{id}", summary="Actualizar tipo de residuo")
def actualizar_tipo(id: int, tipo: TipoResiduoCreate):
    service = TipoResiduoService()
    if not service.get_by_id(id):
        error_404("TipoResiduo", id)
    service.update(id, tipo.dict())
    return {"id": id, "nombre_tipo": tipo.nombre_tipo}

@router_tipos.delete("/{id}", summary="Eliminar tipo de residuo")
def eliminar_tipo(id: int):
    service = TipoResiduoService()
    if not service.get_by_id(id):
        error_404("TipoResiduo", id)
    service.delete(id)
    return {"mensaje": f"TipoResiduo {id} eliminado exitosamente"}
