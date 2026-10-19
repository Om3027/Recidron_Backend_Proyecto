from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from models import get_db
from servicios import ServicioSubzonas
from validators import SubzonaCampusCreate
from routes.auth import verificar_permiso

router_subzonas = APIRouter(tags=["📍 Subzonas del Campus"])


@router_subzonas.get("/subzonas", summary="Listar subzonas del campus")
def listar_subzonas(
    zona_id: Optional[int] = Query(None, description="Filtrar por ID de la zona o edificio padre"),
    tipo_id: Optional[int] = Query(None, description="Filtrar por tipo de subzona (Aula, Oficina, etc.)"),
    piso: Optional[str] = Query(None, description="Filtrar por nivel o piso (1, 2, 3, PB, Exterior)"),
    usuario_auth: dict = Depends(verificar_permiso("reportes:leer")),
    db: Session = Depends(get_db),
):
    """
    Retorna el listado de subzonas activas del campus con filtros opcionales en cascada.
    """
    return ServicioSubzonas(db).listar_subzonas(zona_id=zona_id, tipo_id=tipo_id, piso=piso)


@router_subzonas.get("/subzonas/{id}", summary="Obtener subzona por ID")
def obtener_subzona(
    id: int,
    usuario_auth: dict = Depends(verificar_permiso("reportes:leer")),
    db: Session = Depends(get_db),
):
    """
    Retorna los detalles de una subzona específica activa.
    """
    return ServicioSubzonas(db).obtener_subzona(id)


@router_subzonas.post("/subzonas", status_code=201, summary="Crear subzona")
def crear_subzona(
    subzona: SubzonaCampusCreate,
    usuario_auth: dict = Depends(verificar_permiso("catalogos:gestionar")),
    db: Session = Depends(get_db),
):
    """
    Crea una nueva subzona vinculada a un edificio del campus (requiere permiso de gestión de catálogos).
    """
    return ServicioSubzonas(db).crear_subzona(subzona.model_dump(), usuario_auth["id"])


@router_subzonas.get("/tipos-subzona", summary="Listar catálogo de tipos de subzona")
def listar_tipos_subzona(
    usuario_auth: dict = Depends(verificar_permiso("reportes:leer")),
    db: Session = Depends(get_db),
):
    """
    Retorna la lista oficial de tipos de subzona (Aula, Oficina, Baño, Laboratorio, Área Común, Servicio).
    """
    return ServicioSubzonas(db).listar_tipos()
