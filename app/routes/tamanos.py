from fastapi import APIRouter, HTTPException
from app.services.pgc_service import TamanoService
from app.validators import TamanoCreate
from app.routes.utils import error_404
from sqlalchemy.exc import IntegrityError

router_tamanos = APIRouter(prefix="/tamanos", tags=[" Tamaños"])

@router_tamanos.get("/", summary="Listar tamaños")
def listar_tamanos():
    service = TamanoService()
    tamanos = service.get_all()
    return [{k: v for k, v in t.__dict__.items() if k != '_sa_instance_state'} for t in tamanos]

@router_tamanos.post("/", status_code=201, summary="Crear tamaño")
def crear_tamano(tamano: TamanoCreate):
    service = TamanoService()
    try:
        nuevo = service.create(tamano.dict())
        return {"id": nuevo.id, "nombre_tamano": nuevo.nombre_tamano}
    except IntegrityError:
        raise HTTPException(status_code=422, detail="El tamaño ya existe")

@router_tamanos.get("/{id}", summary="Obtener tamaño por ID")
def obtener_tamano(id: int):
    service = TamanoService()
    t = service.get_by_id(id)
    if not t: error_404("Tamano", id)
    return {k: v for k, v in t.__dict__.items() if k != '_sa_instance_state'}

@router_tamanos.put("/{id}", summary="Actualizar tamaño")
def actualizar_tamano(id: int, tamano: TamanoCreate):
    service = TamanoService()
    if not service.get_by_id(id):
        error_404("Tamano", id)
    service.update(id, tamano.dict())
    return {"id": id, "nombre_tamano": tamano.nombre_tamano}

@router_tamanos.delete("/{id}", summary="Eliminar tamaño")
def eliminar_tamano(id: int):
    service = TamanoService()
    if not service.get_by_id(id):
        error_404("Tamano", id)
    service.delete(id)
    return {"mensaje": f"Tamano {id} eliminado exitosamente"}
