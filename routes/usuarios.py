from fastapi import APIRouter, HTTPException, Depends
from models import get_connection
from routes.auth import check_permission, get_optional_user, get_current_user
from routes.utils import error_404, registrar_log
import mysql.connector
import uuid
from datetime import datetime, timedelta
from validators import UsuarioCreate, UsuarioUpdate, UsuarioLogin

router_usuarios = APIRouter(prefix="/usuarios", tags=[" Usuarios"])

@router_usuarios.get("/", summary="Listar todos los usuarios")
def listar_usuarios(user_auth: dict = Depends(check_permission("usuarios:leer"))):
    """Consulta todos los usuarios activos (sin mostrar contraseñas)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, email, codigo_estudiantil, es_activo, rol_id, creado_en FROM usuarios WHERE es_activo = 1 ORDER BY id")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return usuarios

@router_usuarios.post("/", status_code=201, summary="Registrar un usuario")
def crear_usuario(usuario: UsuarioCreate, user_auth: dict = Depends(get_optional_user)):
    """
    Registra un nuevo usuario. 
    - Si no hay token (público): se fuerza rol_id = 2 (Autor/Estudiante).
    - Si hay token de admin: se permite elegir cualquier rol.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Lógica de Roles (Flexible pero segura)
    final_rol_id = 2  # Por defecto Estudiante
    es_registro_admin = False

    if user_auth:
        # Verificar si el usuario logueado tiene permiso para asignar roles
        # Reutilizamos la lógica de check_permission pero manualmente aquí para no romper el flujo
        cursor.execute("""
            SELECT COUNT(*) FROM rol_permisos rp
            JOIN permisos p ON rp.permiso_id = p.id
            WHERE rp.rol_id = %s AND p.nombre_permiso = 'usuarios:crear'
        """, (user_auth['rol_id'],))
        
        if cursor.fetchone()['COUNT(*)'] > 0:
            es_registro_admin = True
            if usuario.rol_id:
                final_rol_id = usuario.rol_id
            # Si es admin, puede asignar rol 1 o el que quiera

    # Validar que el rol existe en la DB
    cursor.execute("SELECT id FROM roles WHERE id = %s", (final_rol_id,))
    if not cursor.fetchone():
        cursor.close(); conn.close()
        raise HTTPException(status_code=404, detail="El rol especificado no existe")
        
    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password, codigo_estudiantil, rol_id) VALUES (%s, %s, %s, %s, %s)",
            (usuario.nombre, usuario.email, usuario.password, usuario.codigo_estudiantil, final_rol_id)
        )
        nuevo_id = cursor.lastrowid
        conn.commit()
        
        # Auditoría
        # Si es público, se registra que el usuario se creó solo
        log_admin_id = user_auth['id'] if es_registro_admin else nuevo_id
        detalles_log = f"Usuario {nuevo_id} registrado por Admin" if es_registro_admin else f"Auto-registro de nuevo usuario"
        
        registrar_log(log_admin_id, "CREAR", "usuarios", detalles_log, v_nuevo=usuario.dict())
        
        cursor.close()
        conn.close()
        return {
            "id": nuevo_id, 
            "nombre": usuario.nombre, 
            "email": usuario.email, 
            "codigo_estudiantil": usuario.codigo_estudiantil,
            "rol_id": final_rol_id
        }
    except mysql.connector.Error as err:
        cursor.close()
        conn.close()
        if err.errno == 1062: # Duplicate entry
            raise HTTPException(status_code=422, detail="El email ya está registrado")
        raise HTTPException(status_code=500, detail="Error interno al crear usuario")

@router_usuarios.get("/me", summary="Obtener mi propio perfil")
def obtener_perfil_propio(user_auth: dict = Depends(get_current_user)):
    """Retorna los datos del usuario autenticado actualmente."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, email, codigo_estudiantil, rol_id, creado_en FROM usuarios WHERE id = %s", (user_auth['id'],))
    u = cursor.fetchone()
    cursor.close()
    conn.close()
    return u

@router_usuarios.get("/{id}", summary="Obtener un usuario por ID")
def obtener_usuario(id: int, user_auth: dict = Depends(check_permission("usuarios:leer"))):
    """Retorna los datos de un usuario específico activo."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, email, codigo_estudiantil, es_activo, rol_id, creado_en FROM usuarios WHERE id = %s AND es_activo = 1", (id,))
    u = cursor.fetchone()
    cursor.close()
    conn.close()
    if not u: error_404("Usuario", id)
    return u

@router_usuarios.put("/{id}", summary="Actualizar un usuario")
def actualizar_usuario(id: int, datos: UsuarioUpdate, user_auth: dict = Depends(check_permission("usuarios:editar"))):
    """Modifica los datos de un usuario activo con auditoría."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM usuarios WHERE id = %s AND es_activo = 1", (id,))
    v_anterior = cursor.fetchone()
    if not v_anterior:
        cursor.close(); conn.close(); error_404("Usuario", id)
        
    campos = {k: v for k, v in datos.dict().items() if v is not None}
    if campos:
        set_clause = ", ".join([f"{k} = %s" for k in campos])
        cursor.execute(f"UPDATE usuarios SET {set_clause} WHERE id = %s", list(campos.values()) + [id])
        conn.commit()
        
        registrar_log(user_auth['id'], "ACTUALIZAR", "usuarios", f"Usuario {id} modificado", 
                      v_anterior=v_anterior, v_nuevo=campos)
                      
    cursor.close()
    conn.close()
    return {"mensaje": f"Usuario {id} actualizado", "campos": list(campos.keys())}

@router_usuarios.delete("/{id}", summary="Desactivar un usuario (Soft-Delete)")
def eliminar_usuario(id: int, user_auth: dict = Depends(check_permission("usuarios:eliminar"))):
    """Desactiva un usuario (soft delete)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM usuarios WHERE id = %s AND es_activo = 1", (id,))
    if not cursor.fetchone():
        cursor.close(); conn.close(); error_404("Usuario", id)
        
    cursor.execute("UPDATE usuarios SET es_activo = 0 WHERE id = %s", (id,))
    conn.commit()
    
    registrar_log(user_auth['id'], "ELIMINAR", "usuarios", f"Usuario {id} desactivado (soft-delete)")
    
    cursor.close()
    conn.close()
    return {"mensaje": f"Usuario {id} desactivado exitosamente"}


@router_usuarios.post("/login", summary="Iniciar sesión real")
def iniciar_sesion(datos: UsuarioLogin):
    """
    Breve descripción: Verifica las credenciales (email y password), genera un 
    token de sesión único y lo guarda en MySQL Aiven para su validación posterior.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Buscar usuario y su rol
    query = """
        SELECT u.id, u.nombre, u.email, u.password, r.nombre_rol 
        FROM usuarios u
        JOIN roles r ON u.rol_id = r.id
        WHERE u.email = %s AND u.es_activo = 1
    """
    cursor.execute(query, (datos.email,))
    user = cursor.fetchone()
    
    if not user or user['password'] != datos.password:
        cursor.close(); conn.close()
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    # 2. Token y Expiración (24 horas)
    token = str(uuid.uuid4())
    vencimiento = datetime.now() + timedelta(hours=24)
    
    # 3. Registrar sesión
    try:
        cursor.execute(
            "INSERT INTO sesiones (usuario_id, token, expira_en) VALUES (%s, %s, %s)",
            (user['id'], token, vencimiento)
        )
        conn.commit()
    except Exception as e:
        cursor.close(); conn.close()
        raise HTTPException(status_code=500, detail="Error al crear sesión en la nube")
    
    # 4. Auditoría
    registrar_log(user['id'], "LOGIN", "sesiones", f"Acceso exitoso al sistema")
    
    cursor.close()
    conn.close()
    
    return {
        "id": user['id'],
        "token": token,
        "email": user['email'],
        "nombre": user['nombre'],
        "rol": user['nombre_rol']
    }
