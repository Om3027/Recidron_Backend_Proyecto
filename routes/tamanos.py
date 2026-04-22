from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import get_db, Tamano
from validators import TamanoCreate
from routes.utils import error_404, registrar_log
from routes.auth import check_permission

router_tamanos = APIRouter(prefix="/tamanos", tags=[" Tamaños"])

@router_tamanos.get("/", summary="Listar tamaños")
def listar_tamanos(user_auth: dict = Depends(check_permission("reportes:leer")), db: Session = Depends(get_db)):
    """Lista tamaños activos."""
    tams = db.query(Tamano).filter(Tamano.es_activo == True).order_by(Tamano.id).all()
    return tams

@router_tamanos.post("/", status_code=201, summary="Crear tamaño")
def crear_tamano(tamano: TamanoCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar")), db: Session = Depends(get_db)):
    """Crea un nuevo tamaño con auditoría."""
    try:
        nuevo_tamano = Tamano(nombre_tamano=tamano.nombre_tamano)
        db.add(nuevo_tamano)
        db.commit()
        db.refresh(nuevo_tamano)
        
        registrar_log(user_auth['id'], "CREAR", "tamanos", f"Tamaño {nuevo_tamano.id} creado", v_nuevo=tamano.dict(), db=db)
        
        return {"id": nuevo_tamano.id, "nombre_tamano": nuevo_tamano.nombre_tamano}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=422, detail="El tamaño ya existe")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear tamaño")

@router_tamanos.get("/{id}", summary="Obtener tamaño por ID")
def obtener_tamano(id: int, user_auth: dict = Depends(check_permission("reportes:leer")), db: Session = Depends(get_db)):
    t = db.query(Tamano).filter(Tamano.id == id, Tamano.es_activo == True).first()
    if not t: error_404("Tamaño", id)
    return t

@router_tamanos.put("/{id}", summary="Actualizar tamaño")
def actualizar_tamano(id: int, tamano: TamanoCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar")), db: Session = Depends(get_db)):
    """Actualiza un tamaño con auditoría."""
    t = db.query(Tamano).filter(Tamano.id == id, Tamano.es_activo == True).first()
    if not t:
        error_404("Tamaño", id)
        
    v_anterior = {"nombre_tamano": t.nombre_tamano}
    t.nombre_tamano = tamano.nombre_tamano
    db.commit()
    
    registrar_log(user_auth['id'], "ACTUALIZAR", "tamanos", f"Tamaño {id} actualizado", 
                  v_anterior=v_anterior, v_nuevo=tamano.dict(), db=db)
    
    return {"id": id, "nombre_tamano": tamano.nombre_tamano}

@router_tamanos.delete("/{id}", summary="Eliminar tamaño (Soft-Delete)")
def eliminar_tamano(id: int, user_auth: dict = Depends(check_permission("catalogos:gestionar")), db: Session = Depends(get_db)):
    """Desactiva un tamaño (soft-delete)."""
    t = db.query(Tamano).filter(Tamano.id == id, Tamano.es_activo == True).first()
    if not t:
        error_404("Tamaño", id)
        
    t.es_activo = False
    db.commit()
    
    registrar_log(user_auth['id'], "ELIMINAR", "tamanos", f"Tamaño {id} desactivado (soft-delete)", db=db)
    
    return {"mensaje": f"Tamaño {id} desactivado exitosamente"}
