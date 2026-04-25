from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db
from servicios import ServicioCatalogos
from validators import ZonaCampusCreate
from routes.auth import verificar_permiso

router_zonas = APIRouter(prefix="/zonas", tags=[" Zonas del Campus"])


@router_zonas.get("/", summary="Listar zonas del campus")
def listar_zonas(
    usuario_auth: dict = Depends(verificar_permiso("reportes:leer")),
    db: Session = Depends(get_db),
):
    """Lista zonas activas."""
    return ServicioCatalogos(db).listar_zonas()


@router_zonas.post("/", status_code=201, summary="Crear zona")
def crear_zona(
    zona: ZonaCampusCreate,
    usuario_auth: dict = Depends(verificar_permiso("catalogos:gestionar")),
    db: Session = Depends(get_db),
):
    """Crea una nueva zona del campus con auditoría."""
    return ServicioCatalogos(db).crear_zona(zona.nombre_zona, usuario_auth["id"])


@router_zonas.get("/{id}", summary="Obtener zona por ID")
def obtener_zona(
    id: int,
    usuario_auth: dict = Depends(verificar_permiso("reportes:leer")),
    db: Session = Depends(get_db),
):
    """Retorna una zona específica activa."""
    return ServicioCatalogos(db).obtener_zona(id)


@router_zonas.put("/{id}", summary="Actualizar zona")
def actualizar_zona(
    id: int,
    zona: ZonaCampusCreate,
    usuario_auth: dict = Depends(verificar_permiso("catalogos:gestionar")),
    db: Session = Depends(get_db),
):
    """Actualiza una zona con auditoría."""
    return ServicioCatalogos(db).actualizar_zona(id, zona.nombre_zona, usuario_auth["id"])


@router_zonas.delete("/{id}", summary="Eliminar zona (Soft-Delete)")
def desactivar_zona(
    id: int,
    usuario_auth: dict = Depends(verificar_permiso("catalogos:gestionar")),
    db: Session = Depends(get_db),
):
    """Desactiva una zona (soft-delete)."""
    return ServicioCatalogos(db).desactivar_zona(id, usuario_auth["id"])
