import pymysql
from fastapi import APIRouter, HTTPException
from models import get_connection
from validators import MaterialCreate
from routes.utils import error_404

router_materiales = APIRouter(prefix="/materiales", tags=[" Materiales"])

@router_materiales.get("/", summary="Listar materiales")
def listar_materiales():
    conn = get_connection()
    mats = conn.execute("SELECT * FROM materiales ORDER BY id").fetchall()
    conn.close()
    return [dict(m) for m in mats]

@router_materiales.post("/", status_code=201, summary="Crear material")
def crear_material(material: MaterialCreate):
    conn = get_connection()
    try:
        cursor = conn.execute("INSERT INTO materiales (nombre_material) VALUES (%s)", (material.nombre_material,))
        conn.commit(); nuevo_id = cursor.lastrowid; conn.close()
        return {"id": nuevo_id, "nombre_material": material.nombre_material}
    except pymysql.err.IntegrityError:
        conn.close(); raise HTTPException(status_code=422, detail="El material ya existe")

@router_materiales.get("/{id}", summary="Obtener material por ID")
def obtener_material(id: int):
    conn = get_connection()
    m = conn.execute("SELECT * FROM materiales WHERE id = %s", (id,)).fetchone()
    conn.close()
    if not m: error_404("Material", id)
    return dict(m)

@router_materiales.put("/{id}", summary="Actualizar material")
def actualizar_material(id: int, material: MaterialCreate):
    conn = get_connection()
    if not conn.execute("SELECT id FROM materiales WHERE id = %s", (id,)).fetchone():
        conn.close(); error_404("Material", id)
    conn.execute("UPDATE materiales SET nombre_material = %s WHERE id = %s", (material.nombre_material, id))
    conn.commit(); conn.close()
    return {"id": id, "nombre_material": material.nombre_material}

@router_materiales.delete("/{id}", summary="Eliminar material")
def eliminar_material(id: int):
    conn = get_connection()
    if not conn.execute("SELECT id FROM materiales WHERE id = %s", (id,)).fetchone():
        conn.close(); error_404("Material", id)
    conn.execute("DELETE FROM materiales WHERE id = %s", (id,))
    conn.commit(); conn.close()
    return {"mensaje": f"Material {id} eliminado exitosamente"}
