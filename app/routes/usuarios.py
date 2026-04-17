import pymysql
from fastapi import APIRouter, HTTPException
from app import models
from app.validators import UsuarioCreate, UsuarioUpdate
from app.routes.utils import error_404

router_usuarios = APIRouter(prefix="/usuarios", tags=[" Usuarios"])

@router_usuarios.get("/", summary="Listar todos los usuarios")
def listar_usuarios():
    """Consulta todos los usuarios (sin mostrar contraseñas)."""
    return models.get_all_users()

@router_usuarios.post("/", status_code=201, summary="Registrar un usuario")
def crear_usuario(usuario: UsuarioCreate):
    """Registra un nuevo usuario en el sistema."""
    if not models.get_role_by_id(usuario.rol_id):
        raise HTTPException(status_code=404, detail="El rol no existe")
    try:
        nuevo_id = models.create_user(usuario.nombre, usuario.email, usuario.password, usuario.rol_id)
        return {"id": nuevo_id, "nombre": usuario.nombre, "email": usuario.email, "rol_id": usuario.rol_id}
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=422, detail="El email ya está registrado")

@router_usuarios.get("/{id}", summary="Obtener un usuario por ID")
def obtener_usuario(id: int):
    """Retorna los datos de un usuario específico."""
    u = models.get_user_by_id(id)
    if not u: error_404("Usuario", id)
    return u

@router_usuarios.put("/{id}", summary="Actualizar un usuario")
def actualizar_usuario(id: int, datos: UsuarioUpdate):
    """Modifica los datos de un usuario. Solo actualiza los campos enviados."""
    if not models.get_user_by_id(id):
        error_404("Usuario", id)
    campos = {k: v for k, v in datos.dict().items() if v is not None}
    if campos:
        models.update_user(id, campos)
    return {"mensaje": f"Usuario {id} actualizado", "campos": list(campos.keys())}

@router_usuarios.delete("/{id}", summary="Desactivar un usuario")
def eliminar_usuario(id: int):
    """Desactiva un usuario (soft delete — conserva historial de reportes)."""
    if not models.get_user_by_id(id):
        error_404("Usuario", id)
    models.deactivate_user(id)
    return {"mensaje": f"Usuario {id} desactivado exitosamente"}
