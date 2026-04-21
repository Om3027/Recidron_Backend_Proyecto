from fastapi import Header, HTTPException, Depends
from models import get_connection

def get_current_user(authorization: str = Header(None)):
    """
    Extrae el token del header Authorization y valida la sesión.
    Retorna los datos del usuario si es válida.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    
    # El token suele venir como 'Bearer <token>'
    token = authorization.replace("Bearer ", "").strip()
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Buscar sesión activa que no haya expirado
    query = """
        SELECT u.id, u.nombre, u.email, u.rol_id, r.nombre_rol 
        FROM sesiones s
        JOIN usuarios u ON s.usuario_id = u.id
        JOIN roles r ON u.rol_id = r.id
        WHERE s.token = %s AND s.activa = 1 AND s.expira_en > NOW()
        AND u.es_activo = 1
    """
    cursor.execute(query, (token,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")
    
    return user

def get_optional_user(authorization: str = Header(None)):
    """
    Intenta obtener el usuario si hay un token, pero no lanza error si no lo hay.
    Útil para endpoints que son públicos pero tienen funciones extra si eres admin.
    """
    if not authorization:
        return None
    try:
        return get_current_user(authorization)
    except HTTPException:
        return None

def check_permission(permission_required: str):
    """
    Dependencia que verifica si el usuario actual tiene un permiso específico.
    """
    def permission_checker(user: dict = Depends(get_current_user)):
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT COUNT(*) 
            FROM rol_permisos rp
            JOIN permisos p ON rp.permiso_id = p.id
            WHERE rp.rol_id = %s AND p.nombre_permiso = %s
        """
        cursor.execute(query, (user['rol_id'], permission_required))
        has_permission = cursor.fetchone()[0] > 0
        
        cursor.close()
        conn.close()
        
        if not has_permission:
            raise HTTPException(
                status_code=403, 
                detail=f"No tienes permiso para realizar esta acción ({permission_required})"
            )
        
        return user
    
    return permission_checker
