from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db
from servicios import ServicioCatalogos
from validators import TipoResiduoCreate
from routes.auth import verificar_permiso

router_tipos = APIRouter(prefix="/tipos_residuo", tags=[" Tipos de Residuo"])


@router_tipos.get("/", summary="Listar tipos de residuo")
def listar_tipos(
    usuario_auth: dict = Depends(verificar_permiso("reportes:leer")),
    db: Session = Depends(get_db),
):
    """Lista tipos de residuo activos."""
    return ServicioCatalogos(db).listar_tipos()


@router_tipos.post("/", status_code=201, summary="Crear tipo de residuo")
def crear_tipo(
    tipo: TipoResiduoCreate,
    usuario_auth: dict = Depends(verificar_permiso("catalogos:gestionar")),
    db: Session = Depends(get_db),
):
    """Crea un nuevo tipo de residuo con auditoría."""
    return ServicioCatalogos(db).crear_tipo(tipo.nombre_tipo, usuario_auth["id"])


@router_tipos.get("/{id}", summary="Obtener tipo de residuo por ID")
def obtener_tipo(
    id: int,
    usuario_auth: dict = Depends(verificar_permiso("reportes:leer")),
    db: Session = Depends(get_db),
):
    """Retorna un tipo de residuo específico activo."""
    return ServicioCatalogos(db).obtener_tipo(id)


@router_tipos.put("/{id}", summary="Actualizar tipo de residuo")
def actualizar_tipo(
    id: int,
    tipo: TipoResiduoCreate,
    usuario_auth: dict = Depends(verificar_permiso("catalogos:gestionar")),
    db: Session = Depends(get_db),
):
    """Actualiza un tipo de residuo con auditoría."""
    return ServicioCatalogos(db).actualizar_tipo(id, tipo.nombre_tipo, usuario_auth["id"])


@router_tipos.delete("/{id}", summary="Eliminar tipo de residuo (Soft-Delete)")
def desactivar_tipo(
    id: int,
    usuario_auth: dict = Depends(verificar_permiso("catalogos:gestionar")),
    db: Session = Depends(get_db),
):
    """Desactiva un tipo de residuo (soft-delete)."""
    return ServicioCatalogos(db).desactivar_tipo(id, usuario_auth["id"])
