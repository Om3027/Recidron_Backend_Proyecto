from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import get_db, Session as SesionModel, User
from validators import SesionCreate
from routes.utils import error_404, registrar_log
from routes.auth import check_permission

router_sesiones = APIRouter(prefix="/sesiones", tags=[" Sesiones"])

@router_sesiones.get("/", summary="Listar todas las sesiones")
def listar_sesiones(user_auth: dict = Depends(check_permission("audit:leer")), db: Session = Depends(get_db)):
    """Consulta todas las sesiones registradas (solo para auditores/admin)."""
    sesiones = db.query(SesionModel).order_by(SesionModel.id).all()
    return sesiones

@router_sesiones.post("/", status_code=201, summary="Registrar una sesión")
def crear_sesion(sesion: SesionCreate, db: Session = Depends(get_db)):
    """Registra una nueva sesión activa para un usuario (Login)."""
    usuario = db.query(User).filter(User.id == sesion.usuario_id, User.es_activo == True).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="El usuario no existe o está inactivo")
        
    try:
        nueva_sesion = SesionModel(
            usuario_id=sesion.usuario_id,
            token=sesion.token,
            expira_en=sesion.expira_en
        )
        db.add(nueva_sesion)
        db.commit()
        db.refresh(nueva_sesion)
        
        # Auditoría de inicio de sesión
        registrar_log(sesion.usuario_id, "LOGIN", "sesiones", f"Usuario inicio sesión (id_sesion: {nueva_sesion.id})", db=db)
        
        return {"id": nueva_sesion.id, **sesion.dict()}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=422, detail="El token ya existe")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear sesión")

@router_sesiones.get("/{id}", summary="Obtener una sesión por ID")
def obtener_sesion(id: int, user_auth: dict = Depends(check_permission("audit:leer")), db: Session = Depends(get_db)):
    """Retorna una sesión específica."""
    s = db.query(SesionModel).filter(SesionModel.id == id).first()
    if not s: error_404("Sesion", id)
    return s

@router_sesiones.delete("/{id}", summary="Cerrar una sesión")
def eliminar_sesion(id: int, db: Session = Depends(get_db)):
    """Cierra (desactiva) una sesión del sistema (Logout)."""
    sesion = db.query(SesionModel).filter(SesionModel.id == id, SesionModel.activa == True).first()
    if not sesion:
        error_404("Sesion", id)
        
    # Usamos soft-delete para sesiones también: marcada como inactiva
    sesion.activa = False
    db.commit()
    
    registrar_log(sesion.usuario_id, "LOGOUT", "sesiones", f"Sesión {id} cerrada", db=db)
    
    return {"mensaje": f"Sesion {id} cerrada exitosamente"}
