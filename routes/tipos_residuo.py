from fastapi import APIRouter, HTTPException, Depends
from models import get_connection
from validators import TipoResiduoCreate
from routes.utils import error_404, registrar_log
from routes.auth import check_permission
import mysql.connector

router_tipos = APIRouter(prefix="/tipos_residuo", tags=[" Tipos de Residuo"])

@router_tipos.get("/", summary="Listar tipos de residuo")
def listar_tipos(user_auth: dict = Depends(check_permission("reportes:leer"))):
    """Lista tipos de residuo activos."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tipos_residuo WHERE es_activo = 1 ORDER BY id")
    tipos = cursor.fetchall()
    cursor.close()
    conn.close()
    return tipos

@router_tipos.post("/", status_code=201, summary="Crear tipo de residuo")
def crear_tipo(tipo: TipoResiduoCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar"))):
    """Crea un nuevo tipo de residuo con auditoría."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("INSERT INTO tipos_residuo (nombre_tipo) VALUES (%s)", (tipo.nombre_tipo,))
        nuevo_id = cursor.lastrowid
        conn.commit()
        registrar_log(user_auth['id'], "CREAR", "tipos_residuo", f"Tipo de residuo {nuevo_id} creado", v_nuevo=tipo.dict())
        cursor.close()
        conn.close()
        return {"id": nuevo_id, "nombre_tipo": tipo.nombre_tipo}
    except mysql.connector.Error as err:
        cursor.close(); conn.close()
        if err.errno == 1062:
            raise HTTPException(status_code=422, detail="El tipo de residuo ya existe")
        raise HTTPException(status_code=500, detail="Error al crear tipo de residuo")

@router_tipos.get("/{id}", summary="Obtener tipo de residuo por ID")
def obtener_tipo(id: int, user_auth: dict = Depends(check_permission("reportes:leer"))):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tipos_residuo WHERE id = %s AND es_activo = 1", (id,))
    t = cursor.fetchone()
    cursor.close()
    conn.close()
    if not t: error_404("Tipo de Residuo", id)
    return t

@router_tipos.put("/{id}", summary="Actualizar tipo de residuo")
def actualizar_tipo(id: int, tipo: TipoResiduoCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar"))):
    """Actualiza un tipo de residuo con auditoría."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM tipos_residuo WHERE id = %s AND es_activo = 1", (id,))
    v_anterior = cursor.fetchone()
    if not v_anterior:
        cursor.close(); conn.close(); error_404("Tipo de Residuo", id)
        
    cursor.execute("UPDATE tipos_residuo SET nombre_tipo = %s WHERE id = %s", (tipo.nombre_tipo, id))
    conn.commit()
    
    registrar_log(user_auth['id'], "ACTUALIZAR", "tipos_residuo", f"Tipo de residuo {id} actualizado", 
                  v_anterior=v_anterior, v_nuevo=tipo.dict())
    
    cursor.close()
    conn.close()
    return {"id": id, "nombre_tipo": tipo.nombre_tipo}

@router_tipos.delete("/{id}", summary="Eliminar tipo de residuo (Soft-Delete)")
def eliminar_tipo(id: int, user_auth: dict = Depends(check_permission("catalogos:gestionar"))):
    """Desactiva un tipo de residuo (soft-delete)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM tipos_residuo WHERE id = %s AND es_activo = 1", (id,))
    if not cursor.fetchone():
        cursor.close(); conn.close(); error_404("Tipo de Residuo", id)
        
    cursor.execute("UPDATE tipos_residuo SET es_activo = 0 WHERE id = %s", (id,))
    conn.commit()
    
    registrar_log(user_auth['id'], "ELIMINAR", "tipos_residuo", f"Tipo de residuo {id} desactivado (soft-delete)")
    
    cursor.close()
    conn.close()
    return {"mensaje": f"Tipo de residuo {id} desactivado exitosamente"}
