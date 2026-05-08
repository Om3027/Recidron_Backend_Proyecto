from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from models import get_db
from servicios import ServicioUsuarios, ServicioSesiones
from validators import UsuarioCreate, UsuarioUpdate, UsuarioLogin, PerfilUpdate, PasswordRecoverRequest, PasswordResetRequest
from routes.auth import verificar_permiso, obtener_usuario_opcional, obtener_usuario_actual

router_usuarios = APIRouter(prefix="/usuarios", tags=[" Usuarios"])


@router_usuarios.get("/", summary="Listar todos los usuarios")
def listar_usuarios(
    usuario_auth: dict = Depends(verificar_permiso("usuarios:leer")),
    db: Session = Depends(get_db),
):
    """Consulta todos los usuarios activos (sin mostrar contraseñas)."""
    return ServicioUsuarios(db).listar_todos()


@router_usuarios.post("/", status_code=201, summary="Registrar un usuario")
def registrar_usuario(
    usuario: UsuarioCreate,
    usuario_auth: dict | None = Depends(obtener_usuario_opcional),
    db: Session = Depends(get_db),
):
    """
    Registra un nuevo usuario.
    - Sin token (público): se fuerza rol_id = 2 (Autor/Estudiante).
    - Con token de admin: se permite elegir cualquier rol.
    """
    return ServicioUsuarios(db).registrar(usuario.dict(), usuario_auth)


@router_usuarios.get("/me", summary="Obtener mi propio perfil")
def obtener_perfil_propio(
    usuario_auth: dict = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """Retorna los datos del usuario autenticado actualmente."""
    return ServicioUsuarios(db).obtener_perfil_propio(usuario_auth["id"])


@router_usuarios.get("/soporte", summary="Obtener contactos de soporte (Administradores)")
def obtener_contactos_soporte(
    usuario_auth: dict | None = Depends(obtener_usuario_opcional),
    db: Session = Depends(get_db),
):
    """Retorna los administradores dependiendo del rol del solicitante."""
    return ServicioUsuarios(db).obtener_soporte(usuario_auth)


@router_usuarios.put("/me", summary="Editar mi propio perfil y seguridad")
def editar_perfil_propio(
    datos: PerfilUpdate,
    usuario_auth: dict = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """
    El propio usuario puede editar su nombre, email y codigo_estudiantil.
    Para cambiar la contraseña debe enviar nueva_password y confirmar_password
    con el mismo valor y un mínimo de 8 caracteres.
    """
    return ServicioUsuarios(db).actualizar_perfil_propio(usuario_auth["id"], datos.dict())


@router_usuarios.get("/{id}", summary="Obtener un usuario por ID")
def obtener_usuario(
    id: int,
    usuario_auth: dict = Depends(verificar_permiso("usuarios:leer")),
    db: Session = Depends(get_db),
):
    """Retorna los datos de un usuario específico activo."""
    return ServicioUsuarios(db).obtener_por_id(id)


@router_usuarios.put("/{id}", summary="Actualizar un usuario")
def actualizar_usuario(
    id: int,
    datos: UsuarioUpdate,
    usuario_auth: dict = Depends(verificar_permiso("usuarios:editar")),
    db: Session = Depends(get_db),
):
    """Modifica los datos de un usuario activo con auditoría."""
    return ServicioUsuarios(db).actualizar(id, datos.dict(), usuario_auth["id"])


@router_usuarios.delete("/{id}", summary="Desactivar un usuario (Soft-Delete)")
def desactivar_usuario(
    id: int,
    usuario_auth: dict = Depends(verificar_permiso("usuarios:eliminar")),
    db: Session = Depends(get_db),
):
    """Desactiva un usuario (soft delete)."""
    return ServicioUsuarios(db).desactivar(id, usuario_auth["id"])


@router_usuarios.post("/login", summary="Iniciar sesión")
def iniciar_sesion(datos: UsuarioLogin, db: Session = Depends(get_db)):
    """
    Verifica las credenciales (email y password), genera un token de sesión único
    y lo guarda en la base de datos para su validación posterior.
    """
    return ServicioSesiones(db).iniciar_sesion(datos.email, datos.password)


@router_usuarios.post("/recover", summary="Solicitar recuperación de contraseña")
def solicitar_recuperacion(
    datos: PasswordRecoverRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Recibe el email, genera un token temporal de 15 minutos y encola el envío 
    del correo electrónico con un enlace profundo (Deep Link).
    """
    return ServicioUsuarios(db).solicitar_recuperacion(datos.email, background_tasks)


@router_usuarios.post("/reset-password", summary="Restablecer contraseña")
def restablecer_password(
    datos: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Verifica la validez del token recibido desde el Deep Link,
    actualiza la contraseña del usuario y anula el token.
    """
    return ServicioUsuarios(db).restablecer_password(datos.token, datos.nueva_password)
