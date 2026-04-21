from fastapi import APIRouter, HTTPException, Depends
from models import get_connection
from validators import MaterialCreate
from routes.utils import error_404, registrar_log
from routes.auth import check_permission
import mysql.connector

router_materiales = APIRouter(prefix="/materiales", tags=[" Materiales"])

@router_materiales.get("/", summary="Listar materiales")
def listar_materiales(user_auth: dict = Depends(check_permission("reportes:leer"))):
    """Lista materiales activos."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM materiales WHERE es_activo = 1 ORDER BY id")
    mats = cursor.fetchall()
    cursor.close()
    conn.close()
    return mats

@router_materiales.post("/", status_code=201, summary="Crear material")
def crear_material(material: MaterialCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar"))):
    """Crea un nuevo tipo de material con auditoría."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("INSERT INTO materiales (nombre_material) VALUES (%s)", (material.nombre_material,))
        nuevo_id = cursor.lastrowid
        conn.commit()
        registrar_log(user_auth['id'], "CREAR", "materiales", f"Material {nuevo_id} creado", v_nuevo=material.dict())
        cursor.close()
        conn.close()
        return {"id": nuevo_id, "nombre_material": material.nombre_material}
    except mysql.connector.Error as err:
        cursor.close(); conn.close()
        if err.errno == 1062:
            raise HTTPException(status_code=422, detail="El material ya existe")
        raise HTTPException(status_code=500, detail="Error al crear material")

@router_materiales.get("/{id}", summary="Obtener material por ID")
def obtener_material(id: int, user_auth: dict = Depends(check_permission("reportes:leer"))):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM materiales WHERE id = %s AND es_activo = 1", (id,))
    m = cursor.fetchone()
    cursor.close()
    conn.close()
    if not m: error_404("Material", id)
    return m

@router_materiales.put("/{id}", summary="Actualizar material")
def actualizar_material(id: int, material: MaterialCreate, user_auth: dict = Depends(check_permission("catalogos:gestionar"))):
    """Actualiza un material con auditoría."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM materiales WHERE id = %s AND es_activo = 1", (id,))
    v_anterior = cursor.fetchone()
    if not v_anterior:
        cursor.close(); conn.close(); error_404("Material", id)
        
    cursor.execute("UPDATE materiales SET nombre_material = %s WHERE id = %s", (material.nombre_material, id))
    conn.commit()
    
    registrar_log(user_auth['id'], "ACTUALIZAR", "materiales", f"Material {id} actualizado", 
                  v_anterior=v_anterior, v_nuevo=material.dict())
    
    cursor.close()
    conn.close()
    return {"id": id, "nombre_material": material.nombre_material}

@router_materiales.delete("/{id}", summary="Eliminar material (Soft-Delete)")
def eliminar_material(id: int, user_auth: dict = Depends(check_permission("catalogos:gestionar"))):
    """Desactiva un material (soft-delete)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM materiales WHERE id = %s AND es_activo = 1", (id,))
    if not cursor.fetchone():
        cursor.close(); conn.close(); error_404("Material", id)
        
    cursor.execute("UPDATE materiales SET es_activo = 0 WHERE id = %s", (id,))
    conn.commit()
    
    registrar_log(user_auth['id'], "ELIMINAR", "materiales", f"Material {id} desactivado (soft-delete)")
    
    cursor.close()
    conn.close()
    return {"mensaje": f"Material {id} desactivado exitosamente"}
