from fastapi import APIRouter, HTTPException
from app.services.pgc_service import MaterialService
from app.validators import MaterialCreate
from app.routes.utils import error_404
from sqlalchemy.exc import IntegrityError

router_materiales = APIRouter(prefix="/materiales", tags=[" Materiales"])

@router_materiales.get("/", summary="Listar materiales")
def listar_materiales():
    service = MaterialService()
    mats = service.get_all()
    return [{k: v for k, v in m.__dict__.items() if k != '_sa_instance_state'} for m in mats]

@router_materiales.post("/", status_code=201, summary="Crear material")
def crear_material(material: MaterialCreate):
    service = MaterialService()
    try:
        nuevo = service.create(material.dict())
        return {"id": nuevo.id, "nombre_material": nuevo.nombre_material}
    except IntegrityError:
        raise HTTPException(status_code=422, detail="El material ya existe")

@router_materiales.get("/{id}", summary="Obtener material por ID")
def obtener_material(id: int):
    service = MaterialService()
    m = service.get_by_id(id)
    if not m: error_404("Material", id)
    return {k: v for k, v in m.__dict__.items() if k != '_sa_instance_state'}

@router_materiales.put("/{id}", summary="Actualizar material")
def actualizar_material(id: int, material: MaterialCreate):
    service = MaterialService()
    if not service.get_by_id(id):
        error_404("Material", id)
    service.update(id, material.dict())
    return {"id": id, "nombre_material": material.nombre_material}

@router_materiales.delete("/{id}", summary="Eliminar material")
def eliminar_material(id: int):
    service = MaterialService()
    if not service.get_by_id(id):
        error_404("Material", id)
    service.delete(id)
    return {"mensaje": f"Material {id} eliminado exitosamente"}
