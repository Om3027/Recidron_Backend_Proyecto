from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import get_db, ZonaCampus
from validators import ZonaCampusCreate
from routes.utils import error_404, registrar_log
from routes.auth import check_permission

router_zonas = APIRouter(prefix="/zonas", tags=[" Zonas del Campus"])

@router_zonas.get("/", summary="Listar zonas del campus")
def listar_zonas(user_auth: dict = Depends(check_permission("reportes:leer")), db: Session = Depends(get_db)):
    """Lista zonas activas."""
    zonas = db.query(ZonaCampus).filter(ZonaCampus.es_activo == True).order_by(ZonaCampus.id).all()
    return zonas

@router_zonas.post("/", status_code=201, summary="Crear zona")
def crear_zona(zona: ZonaCampusCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar")), db: Session = Depends(get_db)):
    """Crea una nueva zona con auditoría."""
    try:
        nueva_zona = ZonaCampus(nombre_zona=zona.nombre_zona)
        db.add(nueva_zona)
        db.commit()
        db.refresh(nueva_zona)
        
        registrar_log(user_auth['id'], "CREAR", "zonas_campus", f"Zona {nueva_zona.id} creada", v_nuevo=zona.dict(), db=db)
        
        return {"id": nueva_zona.id, "nombre_zona": nueva_zona.nombre_zona}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=422, detail="La zona ya existe")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear zona")

@router_zonas.get("/{id}", summary="Obtener zona por ID")
def obtener_zona(id: int, user_auth: dict = Depends(check_permission("reportes:leer")), db: Session = Depends(get_db)):
    z = db.query(ZonaCampus).filter(ZonaCampus.id == id, ZonaCampus.es_activo == True).first()
    if not z: error_404("Zona", id)
    return z

@router_zonas.put("/{id}", summary="Actualizar zona")
def actualizar_zona(id: int, zona: ZonaCampusCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar")), db: Session = Depends(get_db)):
    """Actualiza una zona con auditoría."""
    z = db.query(ZonaCampus).filter(ZonaCampus.id == id, ZonaCampus.es_activo == True).first()
    if not z:
        error_404("Zona", id)
        
    v_anterior = {"nombre_zona": z.nombre_zona}
    z.nombre_zona = zona.nombre_zona
    db.commit()
    
    registrar_log(user_auth['id'], "ACTUALIZAR", "zonas_campus", f"Zona {id} actualizada", 
                  v_anterior=v_anterior, v_nuevo=zona.dict(), db=db)
    
    return {"id": id, "nombre_zona": zona.nombre_zona}

@router_zonas.delete("/{id}", summary="Eliminar zona (Soft-Delete)")
def eliminar_zona(id: int, user_auth: dict = Depends(check_permission("catalogos:gestionar")), db: Session = Depends(get_db)):
    """Desactiva una zona (soft-delete)."""
    z = db.query(ZonaCampus).filter(ZonaCampus.id == id, ZonaCampus.es_activo == True).first()
    if not z:
        error_404("Zona", id)
        
    z.es_activo = False
    db.commit()
    
    registrar_log(user_auth['id'], "ELIMINAR", "zonas_campus", f"Zona {id} desactivada (soft-delete)", db=db)
    
    return {"mensaje": f"Zona {id} desactivada exitosamente"}
