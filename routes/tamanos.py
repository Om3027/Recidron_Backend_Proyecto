from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db
from servicios import ServicioCatalogos
from validators import TamanoCreate
from routes.auth import verificar_permiso

router_tamanos = APIRouter(prefix="/tamanos", tags=[" Tamaños"])


@router_tamanos.get("/", summary="Listar tamaños")
def listar_tamanos(
    usuario_auth: dict = Depends(verificar_permiso("reportes:leer")),
    db: Session = Depends(get_db),
):
    """Lista tamaños activos."""
    return ServicioCatalogos(db).listar_tamanos()


@router_tamanos.post("/", status_code=201, summary="Crear tamaño")
def crear_tamano(
    tamano: TamanoCreate,
    usuario_auth: dict = Depends(verificar_permiso("catalogos:gestionar")),
    db: Session = Depends(get_db),
):
    """Crea un nuevo tamaño con auditoría."""
    return ServicioCatalogos(db).crear_tamano(tamano.nombre_tamano, usuario_auth["id"])


@router_tamanos.get("/{id}", summary="Obtener tamaño por ID")
def obtener_tamano(
    id: int,
    usuario_auth: dict = Depends(verificar_permiso("reportes:leer")),
    db: Session = Depends(get_db),
):
    """Retorna un tamaño específico activo."""
    return ServicioCatalogos(db).obtener_tamano(id)


@router_tamanos.put("/{id}", summary="Actualizar tamaño")
def actualizar_tamano(
    id: int,
    tamano: TamanoCreate,
    usuario_auth: dict = Depends(verificar_permiso("catalogos:gestionar")),
    db: Session = Depends(get_db),
):
    """Actualiza un tamaño con auditoría."""
    return ServicioCatalogos(db).actualizar_tamano(id, tamano.nombre_tamano, usuario_auth["id"])


@router_tamanos.delete("/{id}", summary="Eliminar tamaño (Soft-Delete)")
def desactivar_tamano(
    id: int,
    usuario_auth: dict = Depends(verificar_permiso("catalogos:gestionar")),
    db: Session = Depends(get_db),
):
    """Desactiva un tamaño (soft-delete)."""
    return ServicioCatalogos(db).desactivar_tamano(id, usuario_auth["id"])
