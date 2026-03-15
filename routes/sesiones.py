import pymysql
from fastapi import APIRouter, HTTPException
from models import get_connection
from validators import SesionCreate
from routes.utils import error_404

router_sesiones = APIRouter(prefix="/sesiones", tags=[" Sesiones"])

@router_sesiones.get("/", summary="Listar todas las sesiones")
def listar_sesiones():
    """Consulta todas las sesiones registradas en el sistema."""
    conn = get_connection()
    sesiones = conn.execute("SELECT * FROM sesiones ORDER BY id").fetchall()
    conn.close()
    return [dict(s) for s in sesiones]

@router_sesiones.post("/", status_code=201, summary="Registrar una sesión")
def crear_sesion(sesion: SesionCreate):
    """Registra una nueva sesión activa para un usuario."""
    conn = get_connection()
    if not conn.execute("SELECT id FROM usuarios WHERE id = %s", (sesion.usuario_id,)).fetchone():
        conn.close(); raise HTTPException(status_code=404, detail="El usuario no existe")
    try:
        cursor = conn.execute(
            "INSERT INTO sesiones (usuario_id, token, expira_en) VALUES (%s, %s, %s)",
            (sesion.usuario_id, sesion.token, sesion.expira_en)
        )
        conn.commit(); nuevo_id = cursor.lastrowid; conn.close()
        return {"id": nuevo_id, **sesion.dict()}
    except pymysql.err.IntegrityError:
        conn.close()
        raise HTTPException(status_code=422, detail="El token ya existe")

@router_sesiones.get("/{id}", summary="Obtener una sesión por ID")
def obtener_sesion(id: int):
    """Retorna una sesión específica."""
    conn = get_connection()
    s = conn.execute("SELECT * FROM sesiones WHERE id = %s", (id,)).fetchone()
    conn.close()
    if not s: error_404("Sesion", id)
    return dict(s)

@router_sesiones.put("/{id}", summary="Actualizar una sesión")
def actualizar_sesion(id: int, sesion: SesionCreate):
    """Actualiza los datos de una sesión existente."""
    conn = get_connection()
    if not conn.execute("SELECT id FROM sesiones WHERE id = %s", (id,)).fetchone():
        conn.close(); error_404("Sesion", id)
    conn.execute(
        "UPDATE sesiones SET usuario_id=%s, token=%s, expira_en=%s WHERE id=%s",
        (sesion.usuario_id, sesion.token, sesion.expira_en, id)
    )
    conn.commit(); conn.close()
    return {"id": id, **sesion.dict()}

@router_sesiones.delete("/{id}", summary="Cerrar una sesión")
def eliminar_sesion(id: int):
    """Cierra/elimina una sesión del sistema."""
    conn = get_connection()
    if not conn.execute("SELECT id FROM sesiones WHERE id = %s", (id,)).fetchone():
        conn.close(); error_404("Sesion", id)
    conn.execute("DELETE FROM sesiones WHERE id = %s", (id,))
    conn.commit(); conn.close()
    return {"mensaje": f"Sesion {id} eliminada exitosamente"}
