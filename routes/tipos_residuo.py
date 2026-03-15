import pymysql
from fastapi import APIRouter, HTTPException
from models import get_connection
from validators import TipoResiduoCreate
from routes.utils import error_404

router_tipos = APIRouter(prefix="/tipos-residuo", tags=[" Tipos de Residuo"])

@router_tipos.get("/", summary="Listar tipos de residuo")
def listar_tipos():
    conn = get_connection()
    tipos = conn.execute("SELECT * FROM tipos_residuo ORDER BY id").fetchall()
    conn.close()
    return [dict(t) for t in tipos]

@router_tipos.post("/", status_code=201, summary="Crear tipo de residuo")
def crear_tipo(tipo: TipoResiduoCreate):
    conn = get_connection()
    try:
        cursor = conn.execute("INSERT INTO tipos_residuo (nombre_tipo) VALUES (%s)", (tipo.nombre_tipo,))
        conn.commit(); nuevo_id = cursor.lastrowid; conn.close()
        return {"id": nuevo_id, "nombre_tipo": tipo.nombre_tipo}
    except pymysql.err.IntegrityError:
        conn.close(); raise HTTPException(status_code=422, detail="El tipo ya existe")

@router_tipos.get("/{id}", summary="Obtener tipo de residuo por ID")
def obtener_tipo(id: int):
    conn = get_connection()
    t = conn.execute("SELECT * FROM tipos_residuo WHERE id = %s", (id,)).fetchone()
    conn.close()
    if not t: error_404("TipoResiduo", id)
    return dict(t)

@router_tipos.put("/{id}", summary="Actualizar tipo de residuo")
def actualizar_tipo(id: int, tipo: TipoResiduoCreate):
    conn = get_connection()
    if not conn.execute("SELECT id FROM tipos_residuo WHERE id = %s", (id,)).fetchone():
        conn.close(); error_404("TipoResiduo", id)
    conn.execute("UPDATE tipos_residuo SET nombre_tipo = %s WHERE id = %s", (tipo.nombre_tipo, id))
    conn.commit(); conn.close()
    return {"id": id, "nombre_tipo": tipo.nombre_tipo}

@router_tipos.delete("/{id}", summary="Eliminar tipo de residuo")
def eliminar_tipo(id: int):
    conn = get_connection()
    if not conn.execute("SELECT id FROM tipos_residuo WHERE id = %s", (id,)).fetchone():
        conn.close(); error_404("TipoResiduo", id)
    conn.execute("DELETE FROM tipos_residuo WHERE id = %s", (id,))
    conn.commit(); conn.close()
    return {"mensaje": f"TipoResiduo {id} eliminado exitosamente"}
