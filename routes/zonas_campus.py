from fastapi import APIRouter, HTTPException, Depends
from models import get_connection
from validators import ZonaCampusCreate
from routes.utils import error_404, registrar_log
from routes.auth import check_permission
import mysql.connector

router_zonas = APIRouter(prefix="/zonas", tags=[" Zonas del Campus"])

@router_zonas.get("/", summary="Listar zonas del campus")
def listar_zonas(user_auth: dict = Depends(check_permission("reportes:leer"))):
    """Lista zonas activas."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM zonas_campus WHERE es_activo = 1 ORDER BY id")
    zonas = cursor.fetchall()
    cursor.close()
    conn.close()
    return zonas

@router_zonas.post("/", status_code=201, summary="Crear zona")
def crear_zona(zona: ZonaCampusCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar"))):
    """Crea una nueva zona con auditoría."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("INSERT INTO zonas_campus (nombre_zona) VALUES (%s)", (zona.nombre_zona,))
        nuevo_id = cursor.lastrowid
        conn.commit()
        registrar_log(user_auth['id'], "CREAR", "zonas_campus", f"Zona {nuevo_id} creada", v_nuevo=zona.dict())
        cursor.close()
        conn.close()
        return {"id": nuevo_id, "nombre_zona": zona.nombre_zona}
    except mysql.connector.Error as err:
        cursor.close(); conn.close()
        if err.errno == 1062:
            raise HTTPException(status_code=422, detail="La zona ya existe")
        raise HTTPException(status_code=500, detail="Error al crear zona")

@router_zonas.get("/{id}", summary="Obtener zona por ID")
def obtener_zona(id: int, user_auth: dict = Depends(check_permission("reportes:leer"))):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM zonas_campus WHERE id = %s AND es_activo = 1", (id,))
    z = cursor.fetchone()
    cursor.close()
    conn.close()
    if not z: error_404("Zona", id)
    return z

@router_zonas.put("/{id}", summary="Actualizar zona")
def actualizar_zona(id: int, zona: ZonaCampusCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar"))):
    """Actualiza una zona con auditoría."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM zonas_campus WHERE id = %s AND es_activo = 1", (id,))
    v_anterior = cursor.fetchone()
    if not v_anterior:
        cursor.close(); conn.close(); error_404("Zona", id)
        
    cursor.execute("UPDATE zonas_campus SET nombre_zona = %s WHERE id = %s", (zona.nombre_zona, id))
    conn.commit()
    
    registrar_log(user_auth['id'], "ACTUALIZAR", "zonas_campus", f"Zona {id} actualizada", 
                  v_anterior=v_anterior, v_nuevo=zona.dict())
    
    cursor.close()
    conn.close()
    return {"id": id, "nombre_zona": zona.nombre_zona}

@router_zonas.delete("/{id}", summary="Eliminar zona (Soft-Delete)")
def eliminar_zona(id: int, user_auth: dict = Depends(check_permission("catalogos:gestionar"))):
    """Desactiva una zona (soft-delete)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM zonas_campus WHERE id = %s AND es_activo = 1", (id,))
    if not cursor.fetchone():
        cursor.close(); conn.close(); error_404("Zona", id)
        
    cursor.execute("UPDATE zonas_campus SET es_activo = 0 WHERE id = %s", (id,))
    conn.commit()
    
    registrar_log(user_auth['id'], "ELIMINAR", "zonas_campus", f"Zona {id} desactivada (soft-delete)")
    
    cursor.close()
    conn.close()
    return {"mensaje": f"Zona {id} desactivada exitosamente"}
