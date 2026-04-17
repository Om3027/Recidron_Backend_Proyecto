import pymysql
from fastapi import APIRouter, HTTPException
from app import models
from app.validators import MaterialCreate
from app.routes.utils import error_404

router_materiales = APIRouter(prefix="/materiales", tags=[" Materiales"])

@router_materiales.get("/", summary="Listar materiales")
def listar_materiales():
    return models.get_all_materials()

@router_materiales.post("/", status_code=201, summary="Crear material")
def crear_material(material: MaterialCreate):
    try:
        nuevo_id = models.create_material(material.nombre_material)
        return {"id": nuevo_id, "nombre_material": material.nombre_material}
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=422, detail="El material ya existe")

@router_materiales.get("/{id}", summary="Obtener material por ID")
def obtener_material(id: int):
    m = models.get_material_by_id(id)
    if not m: error_404("Material", id)
    return m

@router_materiales.put("/{id}", summary="Actualizar material")
def actualizar_material(id: int, material: MaterialCreate):
    if not models.get_material_by_id(id):
        error_404("Material", id)
    models.update_material(id, material.nombre_material)
    return {"id": id, "nombre_material": material.nombre_material}

@router_materiales.delete("/{id}", summary="Eliminar material")
def eliminar_material(id: int):
    if not models.get_material_by_id(id):
        error_404("Material", id)
    models.delete_material(id)
    return {"mensaje": f"Material {id} eliminado exitosamente"}
