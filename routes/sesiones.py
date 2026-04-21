from fastapi import APIRouter, HTTPException, Depends
from models import get_connection
from validators import SesionCreate
from routes.utils import error_404, registrar_log
from routes.auth import check_permission
import mysql.connector

router_sesiones = APIRouter(prefix="/sesiones", tags=[" Sesiones"])

@router_sesiones.get("/", summary="Listar todas las sesiones")
def listar_sesiones(user_auth: dict = Depends(check_permission("audit:leer"))):
    """Consulta todas las sesiones registradas (solo para auditores/admin)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sesiones ORDER BY id")
    sesiones = cursor.fetchall()
    cursor.close()
    conn.close()
    return sesiones

@router_sesiones.post("/", status_code=201, summary="Registrar una sesión")
def crear_sesion(sesion: SesionCreate):
    """Registra una nueva sesión activa para un usuario (Login)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM usuarios WHERE id = %s AND es_activo = 1", (sesion.usuario_id,))
    if not cursor.fetchone():
        cursor.close(); conn.close()
        raise HTTPException(status_code=404, detail="El usuario no existe o está inactivo")
        
    try:
        query = "INSERT INTO sesiones (usuario_id, token, expira_en) VALUES (%s, %s, %s)"
        cursor.execute(query, (sesion.usuario_id, sesion.token, sesion.expira_en))
        nuevo_id = cursor.lastrowid
        conn.commit()
        
        # Auditoría de inicio de sesión
        registrar_log(sesion.usuario_id, "LOGIN", "sesiones", f"Usuario inicio sesión (id_sesion: {nuevo_id})")
        
        cursor.close()
        conn.close()
        return {"id": nuevo_id, **sesion.dict()}
    except mysql.connector.Error as err:
        cursor.close()
        conn.close()
        if err.errno == 1062:
            raise HTTPException(status_code=422, detail="El token ya existe")
        raise HTTPException(status_code=500, detail="Error al crear sesión")

@router_sesiones.get("/{id}", summary="Obtener una sesión por ID")
def obtener_sesion(id: int, user_auth: dict = Depends(check_permission("audit:leer"))):
    """Retorna una sesión específica."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sesiones WHERE id = %s", (id,))
    s = cursor.fetchone()
    cursor.close()
    conn.close()
    if not s: error_404("Sesion", id)
    return s

@router_sesiones.delete("/{id}", summary="Cerrar una sesión")
def eliminar_sesion(id: int):
    """Cierra (desactiva) una sesión del sistema (Logout)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, usuario_id FROM sesiones WHERE id = %s AND activa = 1", (id,))
    sesion = cursor.fetchone()
    if not sesion:
        cursor.close(); conn.close(); error_404("Sesion", id)
        
    # Usamos soft-delete para sesiones también: marcada como inactiva
    cursor.execute("UPDATE sesiones SET activa = 0 WHERE id = %s", (id,))
    conn.commit()
    
    registrar_log(sesion['usuario_id'], "LOGOUT", "sesiones", f"Sesión {id} cerrada")
    
    cursor.close()
    conn.close()
    return {"mensaje": f"Sesion {id} cerrada exitosamente"}
