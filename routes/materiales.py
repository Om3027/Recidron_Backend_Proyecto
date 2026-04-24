from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db
from servicios import ServicioCatalogos
from validators import MaterialCreate
from routes.auth import verificar_permiso

router_materiales = APIRouter(prefix="/materiales", tags=[" Materiales"])


@router_materiales.get("/", summary="Listar materiales")
def listar_materiales(
    usuario_auth: dict = Depends(verificar_permiso("reportes:leer")),
    db: Session = Depends(get_db),
):
    """Lista materiales activos."""
    return ServicioCatalogos(db).listar_materiales()


@router_materiales.post("/", status_code=201, summary="Crear material")
def crear_material(
    material: MaterialCreate,
    usuario_auth: dict = Depends(verificar_permiso("catalogos:gestionar")),
    db: Session = Depends(get_db),
):
    """Crea un nuevo material con auditoría."""
    return ServicioCatalogos(db).crear_material(material.nombre_material, usuario_auth["id"])


@router_materiales.get("/{id}", summary="Obtener material por ID")
def obtener_material(
    id: int,
    usuario_auth: dict = Depends(verificar_permiso("reportes:leer")),
    db: Session = Depends(get_db),
):
    """Retorna un material específico activo."""
    return ServicioCatalogos(db).obtener_material(id)


@router_materiales.put("/{id}", summary="Actualizar material")
def actualizar_material(
    id: int,
    material: MaterialCreate,
    usuario_auth: dict = Depends(verificar_permiso("catalogos:gestionar")),
    db: Session = Depends(get_db),
):
    """Actualiza un material con auditoría."""
    return ServicioCatalogos(db).actualizar_material(id, material.nombre_material, usuario_auth["id"])


@router_materiales.delete("/{id}", summary="Eliminar material (Soft-Delete)")
def desactivar_material(
    id: int,
    usuario_auth: dict = Depends(verificar_permiso("catalogos:gestionar")),
    db: Session = Depends(get_db),
):
    """Desactiva un material (soft-delete)."""
    return ServicioCatalogos(db).desactivar_material(id, usuario_auth["id"])
