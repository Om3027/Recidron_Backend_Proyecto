from fastapi import APIRouter, HTTPException, Depends
from models import get_connection
from validators import TamanoCreate
from routes.utils import error_404, registrar_log
from routes.auth import check_permission
import mysql.connector

router_tamanos = APIRouter(prefix="/tamanos", tags=[" Tamaños"])

@router_tamanos.get("/", summary="Listar tamaños")
def listar_tamanos(user_auth: dict = Depends(check_permission("reportes:leer"))):
    """Lista tamaños activos."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tamanos WHERE es_activo = 1 ORDER BY id")
    tams = cursor.fetchall()
    cursor.close()
    conn.close()
    return tams

@router_tamanos.post("/", status_code=201, summary="Crear tamaño")
def crear_tamano(tamano: TamanoCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar"))):
    """Crea un nuevo tamaño con auditoría."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("INSERT INTO tamanos (nombre_tamano) VALUES (%s)", (tamano.nombre_tamano,))
        nuevo_id = cursor.lastrowid
        conn.commit()
        registrar_log(user_auth['id'], "CREAR", "tamanos", f"Tamaño {nuevo_id} creado", v_nuevo=tamano.dict())
        cursor.close()
        conn.close()
        return {"id": nuevo_id, "nombre_tamano": tamano.nombre_tamano}
    except mysql.connector.Error as err:
        cursor.close(); conn.close()
        if err.errno == 1062:
            raise HTTPException(status_code=422, detail="El tamaño ya existe")
        raise HTTPException(status_code=500, detail="Error al crear tamaño")

@router_tamanos.get("/{id}", summary="Obtener tamaño por ID")
def obtener_tamano(id: int, user_auth: dict = Depends(check_permission("reportes:leer"))):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tamanos WHERE id = %s AND es_activo = 1", (id,))
    t = cursor.fetchone()
    cursor.close()
    conn.close()
    if not t: error_404("Tamaño", id)
    return t

@router_tamanos.put("/{id}", summary="Actualizar tamaño")
def actualizar_tamano(id: int, tamano: TamanoCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar"))):
    """Actualiza un tamaño con auditoría."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM tamanos WHERE id = %s AND es_activo = 1", (id,))
    v_anterior = cursor.fetchone()
    if not v_anterior:
        cursor.close(); conn.close(); error_404("Tamaño", id)
        
    cursor.execute("UPDATE tamanos SET nombre_tamano = %s WHERE id = %s", (tamano.nombre_tamano, id))
    conn.commit()
    
    registrar_log(user_auth['id'], "ACTUALIZAR", "tamanos", f"Tamaño {id} actualizado", 
                  v_anterior=v_anterior, v_nuevo=tamano.dict())
    
    cursor.close()
    conn.close()
    return {"id": id, "nombre_tamano": tamano.nombre_tamano}

@router_tamanos.delete("/{id}", summary="Eliminar tamaño (Soft-Delete)")
def eliminar_tamano(id: int, user_auth: dict = Depends(check_permission("catalogos:gestionar"))):
    """Desactiva un tamaño (soft-delete)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM tamanos WHERE id = %s AND es_activo = 1", (id,))
    if not cursor.fetchone():
        cursor.close(); conn.close(); error_404("Tamaño", id)
        
    cursor.execute("UPDATE tamanos SET es_activo = 0 WHERE id = %s", (id,))
    conn.commit()
    
    registrar_log(user_auth['id'], "ELIMINAR", "tamanos", f"Tamaño {id} desactivado (soft-delete)")
    
    cursor.close()
    conn.close()
    return {"mensaje": f"Tamaño {id} desactivado exitosamente"}
