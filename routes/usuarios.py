from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import get_db, User, Role, Session as SesionModel
from routes.auth import check_permission, get_optional_user, get_current_user
from routes.utils import error_404, registrar_log
import uuid
from datetime import datetime, timedelta
from validators import UsuarioCreate, UsuarioUpdate, UsuarioLogin
from utils.security import get_password_hash, verify_password

router_usuarios = APIRouter(prefix="/usuarios", tags=[" Usuarios"])

@router_usuarios.get("/", summary="Listar todos los usuarios")
def listar_usuarios(user_auth: dict = Depends(check_permission("usuarios:leer")), db: Session = Depends(get_db)):
    """Consulta todos los usuarios activos (sin mostrar contraseñas)."""
    usuarios = db.query(User).filter(User.es_activo == True).order_by(User.id).all()
    return [{"id": u.id, "nombre": u.nombre, "email": u.email, "codigo_estudiantil": u.codigo_estudiantil, "es_activo": u.es_activo, "rol_id": u.rol_id, "creado_en": u.creado_en} for u in usuarios]

@router_usuarios.post("/", status_code=201, summary="Registrar un usuario")
def crear_usuario(usuario: UsuarioCreate, user_auth: dict = Depends(get_optional_user), db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario. 
    - Si no hay token (público): se fuerza rol_id = 2 (Autor/Estudiante).
    - Si hay token de admin: se permite elegir cualquier rol.
    """
    final_rol_id = 2  # Por defecto Estudiante
    es_registro_admin = False

    if user_auth:
        from models import Permission
        has_permission = db.query(Role).join(Role.permisos).filter(
            Role.id == user_auth['rol_id'],
            Permission.nombre_permiso == 'usuarios:crear'
        ).first()
        
        if has_permission:
            es_registro_admin = True
            if usuario.rol_id:
                final_rol_id = usuario.rol_id

    rol_exists = db.query(Role).filter(Role.id == final_rol_id).first()
    if not rol_exists:
        raise HTTPException(status_code=404, detail="El rol especificado no existe")
        
    try:
        hashed_password = get_password_hash(usuario.password)
        nuevo_usuario = User(
            nombre=usuario.nombre,
            email=usuario.email,
            password=hashed_password,
            codigo_estudiantil=usuario.codigo_estudiantil,
            rol_id=final_rol_id
        )
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        log_admin_id = user_auth['id'] if es_registro_admin else nuevo_usuario.id
        detalles_log = f"Usuario {nuevo_usuario.id} registrado por Admin" if es_registro_admin else f"Auto-registro de nuevo usuario"
        
        registrar_log(log_admin_id, "CREAR", "usuarios", detalles_log, v_nuevo=usuario.dict(), db=db)
        
        return {
            "id": nuevo_usuario.id, 
            "nombre": usuario.nombre, 
            "email": usuario.email, 
            "codigo_estudiantil": usuario.codigo_estudiantil,
            "rol_id": final_rol_id
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=422, detail="El email ya está registrado")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno al crear usuario")

@router_usuarios.get("/me", summary="Obtener mi propio perfil")
def obtener_perfil_propio(user_auth: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retorna los datos del usuario autenticado actualmente."""
    u = db.query(User).filter(User.id == user_auth['id']).first()
    return {"id": u.id, "nombre": u.nombre, "email": u.email, "codigo_estudiantil": u.codigo_estudiantil, "rol_id": u.rol_id, "creado_en": u.creado_en}

@router_usuarios.get("/{id}", summary="Obtener un usuario por ID")
def obtener_usuario(id: int, user_auth: dict = Depends(check_permission("usuarios:leer")), db: Session = Depends(get_db)):
    """Retorna los datos de un usuario específico activo."""
    u = db.query(User).filter(User.id == id, User.es_activo == True).first()
    if not u: error_404("Usuario", id)
    return {"id": u.id, "nombre": u.nombre, "email": u.email, "codigo_estudiantil": u.codigo_estudiantil, "es_activo": u.es_activo, "rol_id": u.rol_id, "creado_en": u.creado_en}

@router_usuarios.put("/{id}", summary="Actualizar un usuario")
def actualizar_usuario(id: int, datos: UsuarioUpdate, user_auth: dict = Depends(check_permission("usuarios:editar")), db: Session = Depends(get_db)):
    """Modifica los datos de un usuario activo con auditoría."""
    usuario = db.query(User).filter(User.id == id, User.es_activo == True).first()
    if not usuario:
        error_404("Usuario", id)
        
    v_anterior = {"nombre": usuario.nombre, "email": usuario.email, "codigo_estudiantil": usuario.codigo_estudiantil, "rol_id": usuario.rol_id}
        
    campos = {k: v for k, v in datos.dict().items() if v is not None}
    
    if "password" in campos:
        campos["password"] = get_password_hash(campos["password"])

    if campos:
        for k, v in campos.items():
            setattr(usuario, k, v)
        db.commit()
        
        log_campos = {k: v for k, v in campos.items() if k != "password"}
        registrar_log(user_auth['id'], "ACTUALIZAR", "usuarios", f"Usuario {id} modificado", 
                      v_anterior=v_anterior, v_nuevo=log_campos, db=db)
                      
    return {"mensaje": f"Usuario {id} actualizado", "campos": list(campos.keys())}

@router_usuarios.delete("/{id}", summary="Desactivar un usuario (Soft-Delete)")
def eliminar_usuario(id: int, user_auth: dict = Depends(check_permission("usuarios:eliminar")), db: Session = Depends(get_db)):
    """Desactiva un usuario (soft delete)."""
    usuario = db.query(User).filter(User.id == id, User.es_activo == True).first()
    if not usuario:
        error_404("Usuario", id)
        
    usuario.es_activo = False
    db.commit()
    
    registrar_log(user_auth['id'], "ELIMINAR", "usuarios", f"Usuario {id} desactivado (soft-delete)", db=db)
    
    return {"mensaje": f"Usuario {id} desactivado exitosamente"}

@router_usuarios.post("/login", summary="Iniciar sesión real")
def iniciar_sesion(datos: UsuarioLogin, db: Session = Depends(get_db)):
    """
    Breve descripción: Verifica las credenciales (email y password), genera un 
    token de sesión único y lo guarda en MySQL Aiven para su validación posterior.
    """
    user = db.query(User).filter(User.email == datos.email, User.es_activo == True).first()
    
    if not user or not verify_password(datos.password, user.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    token = str(uuid.uuid4())
    vencimiento = datetime.now() + timedelta(hours=24)
    
    try:
        nueva_sesion = SesionModel(
            usuario_id=user.id,
            token=token,
            expira_en=vencimiento
        )
        db.add(nueva_sesion)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear sesión en la nube")
    
    registrar_log(user.id, "LOGIN", "sesiones", f"Acceso exitoso al sistema", db=db)
    
    return {
        "id": user.id,
        "token": token,
        "email": user.email,
        "nombre": user.nombre,
        "rol": user.rol.nombre_rol
    }
