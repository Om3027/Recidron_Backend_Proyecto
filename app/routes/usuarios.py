import pymysql
from fastapi import APIRouter, HTTPException
from app.models import get_connection
from app.validators import UsuarioCreate, UsuarioUpdate
from app.routes.utils import error_404

router_usuarios = APIRouter(prefix="/usuarios", tags=[" Usuarios"])

@router_usuarios.get("/", summary="Listar todos los usuarios")
def listar_usuarios():
    """Consulta todos los usuarios (sin mostrar contraseñas)."""
    conn = get_connection()
    usuarios = conn.execute(
        "SELECT id, nombre, email, activo, rol_id, creado_en FROM usuarios ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(u) for u in usuarios]

@router_usuarios.post("/", status_code=201, summary="Registrar un usuario")
def crear_usuario(usuario: UsuarioCreate):
    """Registra un nuevo usuario en el sistema."""
    conn = get_connection()
    if not conn.execute("SELECT id FROM roles WHERE id = %s", (usuario.rol_id,)).fetchone():
        conn.close(); raise HTTPException(status_code=404, detail="El rol no existe")
    try:
        cursor = conn.execute(
            "INSERT INTO usuarios (nombre, email, password, rol_id) VALUES (%s, %s, %s, %s)",
            (usuario.nombre, usuario.email, usuario.password, usuario.rol_id)
        )
        conn.commit(); nuevo_id = cursor.lastrowid; conn.close()
        return {"id": nuevo_id, "nombre": usuario.nombre, "email": usuario.email, "rol_id": usuario.rol_id}
    except pymysql.err.IntegrityError:
        conn.close()
        raise HTTPException(status_code=422, detail="El email ya está registrado")

@router_usuarios.get("/{id}", summary="Obtener un usuario por ID")
def obtener_usuario(id: int):
    """Retorna los datos de un usuario específico."""
    conn = get_connection()
    u = conn.execute(
        "SELECT id, nombre, email, activo, rol_id, creado_en FROM usuarios WHERE id = %s", (id,)
    ).fetchone()
    conn.close()
    if not u: error_404("Usuario", id)
    return dict(u)

@router_usuarios.put("/{id}", summary="Actualizar un usuario")
def actualizar_usuario(id: int, datos: UsuarioUpdate):
    """Modifica los datos de un usuario. Solo actualiza los campos enviados."""
    conn = get_connection()
    if not conn.execute("SELECT id FROM usuarios WHERE id = %s", (id,)).fetchone():
        conn.close(); error_404("Usuario", id)
    campos = {k: v for k, v in datos.dict().items() if v is not None}
    if campos:
        set_clause = ", ".join([f"{k} = %s" for k in campos])
        conn.execute(f"UPDATE usuarios SET {set_clause} WHERE id = %s", list(campos.values()) + [id])
        conn.commit()
    conn.close()
    return {"mensaje": f"Usuario {id} actualizado", "campos": list(campos.keys())}

@router_usuarios.delete("/{id}", summary="Desactivar un usuario")
def eliminar_usuario(id: int):
    """Desactiva un usuario (soft delete — conserva historial de reportes)."""
    conn = get_connection()
    if not conn.execute("SELECT id FROM usuarios WHERE id = %s", (id,)).fetchone():
        conn.close(); error_404("Usuario", id)
    conn.execute("UPDATE usuarios SET activo = 0 WHERE id = %s", (id,))
    conn.commit(); conn.close()
    return {"mensaje": f"Usuario {id} desactivado exitosamente"}
