from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import get_db, Material
from validators import MaterialCreate
from routes.utils import error_404, registrar_log
from routes.auth import check_permission

router_materiales = APIRouter(prefix="/materiales", tags=[" Materiales"])

@router_materiales.get("/", summary="Listar materiales")
def listar_materiales(user_auth: dict = Depends(check_permission("reportes:leer")), db: Session = Depends(get_db)):
    """Lista materiales activos."""
    mats = db.query(Material).filter(Material.es_activo == True).order_by(Material.id).all()
    return mats

@router_materiales.post("/", status_code=201, summary="Crear material")
def crear_material(material: MaterialCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar")), db: Session = Depends(get_db)):
    """Crea un nuevo tipo de material con auditoría."""
    try:
        nuevo_material = Material(nombre_material=material.nombre_material)
        db.add(nuevo_material)
        db.commit()
        db.refresh(nuevo_material)
        
        registrar_log(user_auth['id'], "CREAR", "materiales", f"Material {nuevo_material.id} creado", v_nuevo=material.dict(), db=db)
        
        return {"id": nuevo_material.id, "nombre_material": nuevo_material.nombre_material}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=422, detail="El material ya existe")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear material")

@router_materiales.get("/{id}", summary="Obtener material por ID")
def obtener_material(id: int, user_auth: dict = Depends(check_permission("reportes:leer")), db: Session = Depends(get_db)):
    m = db.query(Material).filter(Material.id == id, Material.es_activo == True).first()
    if not m: error_404("Material", id)
    return m

@router_materiales.put("/{id}", summary="Actualizar material")
def actualizar_material(id: int, material: MaterialCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar")), db: Session = Depends(get_db)):
    """Actualiza un material con auditoría."""
    m = db.query(Material).filter(Material.id == id, Material.es_activo == True).first()
    if not m:
        error_404("Material", id)
        
    v_anterior = {"nombre_material": m.nombre_material}
    m.nombre_material = material.nombre_material
    db.commit()
    
    registrar_log(user_auth['id'], "ACTUALIZAR", "materiales", f"Material {id} actualizado", 
                  v_anterior=v_anterior, v_nuevo=material.dict(), db=db)
    
    return {"id": id, "nombre_material": material.nombre_material}

@router_materiales.delete("/{id}", summary="Eliminar material (Soft-Delete)")
def eliminar_material(id: int, user_auth: dict = Depends(check_permission("catalogos:gestionar")), db: Session = Depends(get_db)):
    """Desactiva un material (soft-delete)."""
    m = db.query(Material).filter(Material.id == id, Material.es_activo == True).first()
    if not m:
        error_404("Material", id)
        
    m.es_activo = False
    db.commit()
    
    registrar_log(user_auth['id'], "ELIMINAR", "materiales", f"Material {id} desactivado (soft-delete)", db=db)
    
    return {"mensaje": f"Material {id} desactivado exitosamente"}
