import pymysql
from fastapi import APIRouter, HTTPException
from app.models import get_connection
from app.validators import TamanoCreate
from app.routes.utils import error_404

router_tamanos = APIRouter(prefix="/tamanos", tags=[" Tamaños"])

@router_tamanos.get("/", summary="Listar tamaños")
def listar_tamanos():
    conn = get_connection()
    tamanos = conn.execute("SELECT * FROM tamanos ORDER BY id").fetchall()
    conn.close()
    return [dict(t) for t in tamanos]

@router_tamanos.post("/", status_code=201, summary="Crear tamaño")
def crear_tamano(tamano: TamanoCreate):
    conn = get_connection()
    try:
        cursor = conn.execute("INSERT INTO tamanos (nombre_tamano) VALUES (%s)", (tamano.nombre_tamano,))
        conn.commit(); nuevo_id = cursor.lastrowid; conn.close()
        return {"id": nuevo_id, "nombre_tamano": tamano.nombre_tamano}
    except pymysql.err.IntegrityError:
        conn.close(); raise HTTPException(status_code=422, detail="El tamaño ya existe")

@router_tamanos.get("/{id}", summary="Obtener tamaño por ID")
def obtener_tamano(id: int):
    conn = get_connection()
    t = conn.execute("SELECT * FROM tamanos WHERE id = %s", (id,)).fetchone()
    conn.close()
    if not t: error_404("Tamano", id)
    return dict(t)

@router_tamanos.put("/{id}", summary="Actualizar tamaño")
def actualizar_tamano(id: int, tamano: TamanoCreate):
    conn = get_connection()
    if not conn.execute("SELECT id FROM tamanos WHERE id = %s", (id,)).fetchone():
        conn.close(); error_404("Tamano", id)
    conn.execute("UPDATE tamanos SET nombre_tamano = %s WHERE id = %s", (tamano.nombre_tamano, id))
    conn.commit(); conn.close()
    return {"id": id, "nombre_tamano": tamano.nombre_tamano}

@router_tamanos.delete("/{id}", summary="Eliminar tamaño")
def eliminar_tamano(id: int):
    conn = get_connection()
    if not conn.execute("SELECT id FROM tamanos WHERE id = %s", (id,)).fetchone():
        conn.close(); error_404("Tamano", id)
    conn.execute("DELETE FROM tamanos WHERE id = %s", (id,))
    conn.commit(); conn.close()
    return {"mensaje": f"Tamano {id} eliminado exitosamente"}
