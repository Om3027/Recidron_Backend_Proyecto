import pymysql
from fastapi import APIRouter, HTTPException
from app.models import get_connection
from app.validators import ZonaCampusCreate
from app.routes.utils import error_404

router_zonas = APIRouter(prefix="/zonas", tags=[" Zonas del Campus"])

@router_zonas.get("/", summary="Listar zonas del campus")
def listar_zonas():
    conn = get_connection()
    zonas = conn.execute("SELECT * FROM zonas_campus ORDER BY id").fetchall()
    conn.close()
    return [dict(z) for z in zonas]

@router_zonas.post("/", status_code=201, summary="Crear zona")
def crear_zona(zona: ZonaCampusCreate):
    conn = get_connection()
    try:
        cursor = conn.execute("INSERT INTO zonas_campus (nombre_zona) VALUES (%s)", (zona.nombre_zona,))
        conn.commit(); nuevo_id = cursor.lastrowid; conn.close()
        return {"id": nuevo_id, "nombre_zona": zona.nombre_zona}
    except pymysql.err.IntegrityError:
        conn.close(); raise HTTPException(status_code=422, detail="La zona ya existe")

@router_zonas.get("/{id}", summary="Obtener zona por ID")
def obtener_zona(id: int):
    conn = get_connection()
    z = conn.execute("SELECT * FROM zonas_campus WHERE id = %s", (id,)).fetchone()
    conn.close()
    if not z: error_404("ZonaCampus", id)
    return dict(z)

@router_zonas.put("/{id}", summary="Actualizar zona")
def actualizar_zona(id: int, zona: ZonaCampusCreate):
    conn = get_connection()
    if not conn.execute("SELECT id FROM zonas_campus WHERE id = %s", (id,)).fetchone():
        conn.close(); error_404("ZonaCampus", id)
    conn.execute("UPDATE zonas_campus SET nombre_zona = %s WHERE id = %s", (zona.nombre_zona, id))
    conn.commit(); conn.close()
    return {"id": id, "nombre_zona": zona.nombre_zona}

@router_zonas.delete("/{id}", summary="Eliminar zona")
def eliminar_zona(id: int):
    conn = get_connection()
    if not conn.execute("SELECT id FROM zonas_campus WHERE id = %s", (id,)).fetchone():
        conn.close(); error_404("ZonaCampus", id)
    conn.execute("DELETE FROM zonas_campus WHERE id = %s", (id,))
    conn.commit(); conn.close()
    return {"mensaje": f"Zona {id} eliminada exitosamente"}
