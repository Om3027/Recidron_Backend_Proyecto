from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import get_db, TipoResiduo
from validators import TipoResiduoCreate
from routes.utils import error_404, registrar_log
from routes.auth import check_permission

router_tipos = APIRouter(prefix="/tipos_residuo", tags=[" Tipos de Residuo"])

@router_tipos.get("/", summary="Listar tipos de residuo")
def listar_tipos(user_auth: dict = Depends(check_permission("reportes:leer")), db: Session = Depends(get_db)):
    """Lista tipos de residuo activos."""
    tipos = db.query(TipoResiduo).filter(TipoResiduo.es_activo == True).order_by(TipoResiduo.id).all()
    return tipos

@router_tipos.post("/", status_code=201, summary="Crear tipo de residuo")
def crear_tipo(tipo: TipoResiduoCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar")), db: Session = Depends(get_db)):
    """Crea un nuevo tipo de residuo con auditoría."""
    try:
        nuevo_tipo = TipoResiduo(nombre_tipo=tipo.nombre_tipo)
        db.add(nuevo_tipo)
        db.commit()
        db.refresh(nuevo_tipo)
        
        registrar_log(user_auth['id'], "CREAR", "tipos_residuo", f"Tipo de residuo {nuevo_tipo.id} creado", v_nuevo=tipo.dict(), db=db)
        
        return {"id": nuevo_tipo.id, "nombre_tipo": nuevo_tipo.nombre_tipo}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=422, detail="El tipo de residuo ya existe")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear tipo de residuo")

@router_tipos.get("/{id}", summary="Obtener tipo de residuo por ID")
def obtener_tipo(id: int, user_auth: dict = Depends(check_permission("reportes:leer")), db: Session = Depends(get_db)):
    t = db.query(TipoResiduo).filter(TipoResiduo.id == id, TipoResiduo.es_activo == True).first()
    if not t: error_404("Tipo de Residuo", id)
    return t

@router_tipos.put("/{id}", summary="Actualizar tipo de residuo")
def actualizar_tipo(id: int, tipo: TipoResiduoCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar")), db: Session = Depends(get_db)):
    """Actualiza un tipo de residuo con auditoría."""
    t = db.query(TipoResiduo).filter(TipoResiduo.id == id, TipoResiduo.es_activo == True).first()
    if not t:
        error_404("Tipo de Residuo", id)
        
    v_anterior = {"nombre_tipo": t.nombre_tipo}
    t.nombre_tipo = tipo.nombre_tipo
    db.commit()
    
    registrar_log(user_auth['id'], "ACTUALIZAR", "tipos_residuo", f"Tipo de residuo {id} actualizado", 
                  v_anterior=v_anterior, v_nuevo=tipo.dict(), db=db)
    
    return {"id": id, "nombre_tipo": tipo.nombre_tipo}

@router_tipos.delete("/{id}", summary="Eliminar tipo de residuo (Soft-Delete)")
def eliminar_tipo(id: int, user_auth: dict = Depends(check_permission("catalogos:gestionar")), db: Session = Depends(get_db)):
    """Desactiva un tipo de residuo (soft-delete)."""
    t = db.query(TipoResiduo).filter(TipoResiduo.id == id, TipoResiduo.es_activo == True).first()
    if not t:
        error_404("Tipo de Residuo", id)
        
    t.es_activo = False
    db.commit()
    
    registrar_log(user_auth['id'], "ELIMINAR", "tipos_residuo", f"Tipo de residuo {id} desactivado (soft-delete)", db=db)
    
    return {"mensaje": f"Tipo de residuo {id} desactivado exitosamente"}
