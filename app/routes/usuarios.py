from fastapi import APIRouter, HTTPException
from app.services.seguridad_service import UserService, RoleService
from app.validators import UsuarioCreate, UsuarioUpdate
from app.routes.utils import error_404
from sqlalchemy.exc import IntegrityError

router_usuarios = APIRouter(prefix="/usuarios", tags=[" Usuarios"])

@router_usuarios.get("/", summary="Listar todos los usuarios")
def listar_usuarios():
    """Consulta todos los usuarios."""
    service = UserService()
    usuarios = service.get_all()
    # Limpieza manual si el servicio no lo hace
    res = []
    for u in usuarios:
        d = u.__dict__.copy()
        d.pop('password', None)
        d.pop('_sa_instance_state', None)
        res.append(d)
    return res

@router_usuarios.post("/", status_code=201, summary="Registrar un usuario")
def crear_usuario(usuario: UsuarioCreate):
    """Registra un nuevo usuario en el sistema."""
    role_service = RoleService()
    user_service = UserService()
    
    if not role_service.get_by_id(usuario.rol_id):
        raise HTTPException(status_code=404, detail="El rol no existe")
    try:
        nuevo_usuario = user_service.create(usuario.dict())
        return {
            "id": nuevo_usuario.id,
            "nombre": nuevo_usuario.nombre,
            "email": nuevo_usuario.email,
            "rol_id": nuevo_usuario.rol_id
        }
    except IntegrityError:
        raise HTTPException(status_code=422, detail="El email ya está registrado")

@router_usuarios.get("/{id}", summary="Obtener un usuario por ID")
def obtener_usuario(id: int):
    """Retorna los datos de un usuario específico."""
    service = UserService()
    u = service.get_by_id(id)
    if not u: error_404("Usuario", id)
    d = u.__dict__.copy()
    d.pop('password', None)
    d.pop('_sa_instance_state', None)
    return d

@router_usuarios.put("/{id}", summary="Actualizar un usuario")
def actualizar_usuario(id: int, datos: UsuarioUpdate):
    """Modifica los datos de un usuario. Solo actualiza los campos enviados."""
    service = UserService()
    if not service.get_by_id(id):
        error_404("Usuario", id)
    campos = {k: v for k, v in datos.dict().items() if v is not None}
    if campos:
        service.update(id, campos)
    return {"mensaje": f"Usuario {id} actualizado", "campos": list(campos.keys())}

@router_usuarios.delete("/{id}", summary="Desactivar un usuario")
def eliminar_usuario(id: int):
    """Desactiva un usuario (soft delete)."""
    service = UserService()
    if not service.get_by_id(id):
        error_404("Usuario", id)
    service.deactivate(id)
    return {"mensaje": f"Usuario {id} desactivado exitosamente"}
