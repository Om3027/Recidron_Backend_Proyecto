from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from models import get_db, Session as SesionModel, User, Role
from datetime import datetime

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """
    Extrae el token del header Authorization y valida la sesión.
    Retorna los datos del usuario si es válida.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    
    # El token suele venir como 'Bearer <token>'
    token = authorization.replace("Bearer ", "").strip()
    
    # Buscar sesión activa que no haya expirado
    sesion = db.query(SesionModel).join(User).join(Role).filter(
        SesionModel.token == token,
        SesionModel.activa == True,
        SesionModel.expira_en > datetime.now(),
        User.es_activo == True
    ).first()
    
    if not sesion or not sesion.usuario:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")
    
    user = {
        'id': sesion.usuario.id,
        'nombre': sesion.usuario.nombre,
        'email': sesion.usuario.email,
        'rol_id': sesion.usuario.rol_id,
        'nombre_rol': sesion.usuario.rol.nombre_rol
    }
    
    return user

def get_optional_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """
    Intenta obtener el usuario si hay un token, pero no lanza error si no lo hay.
    Útil para endpoints que son públicos pero tienen funciones extra si eres admin.
    """
    if not authorization:
        return None
    try:
        return get_current_user(authorization, db)
    except HTTPException:
        return None

def check_permission(permission_required: str):
    """
    Dependencia que verifica si el usuario actual tiene un permiso específico.
    """
    def permission_checker(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
        from models import Permission
        
        has_permission = db.query(Role).join(Role.permisos).filter(
            Role.id == user['rol_id'],
            Permission.nombre_permiso == permission_required
        ).first()
        
        if not has_permission:
            raise HTTPException(
                status_code=403, 
                detail=f"No tienes permiso para realizar esta acción ({permission_required})"
            )
        
        return user
    
    return permission_checker
