from fastapi import APIRouter, HTTPException
from models import get_connection
from validators import ReporteCreate, ReporteUpdate
from routes.utils import error_404

router_reportes = APIRouter(prefix="/reportes", tags=[" Reportes"])

@router_reportes.get("/", summary="Listar todos los reportes")
def listar_reportes():
    """Consulta todos los reportes de residuos registrados."""
    conn = get_connection()
    reportes = conn.execute("SELECT * FROM reportes ORDER BY fecha_reporte DESC").fetchall()
    conn.close()
    return [dict(r) for r in reportes]

@router_reportes.post("/", status_code=201, summary="Crear un reporte")
def crear_reporte(reporte: ReporteCreate):
    """Registra un nuevo reporte de residuo."""
    conn = get_connection()
    checks = [
        ("usuarios",      reporte.usuario_id,      "Usuario"),
        ("tipos_residuo", reporte.tipo_residuo_id,  "TipoResiduo"),
        ("materiales",    reporte.material_id,       "Material"),
        ("zonas_campus",  reporte.zona_id,           "Zona"),
        ("tamanos",       reporte.tamano_id,         "Tamano"),
    ]
    for tabla, fk_id, nombre in checks:
        if not conn.execute(f"SELECT id FROM {tabla} WHERE id = ?", (fk_id,)).fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail=f"{nombre} con id {fk_id} no existe")

    cursor = conn.execute(
        "INSERT INTO reportes (descripcion, usuario_id, tipo_residuo_id, material_id, zona_id, tamano_id) VALUES (?,?,?,?,?,?)",
        (reporte.descripcion, reporte.usuario_id, reporte.tipo_residuo_id,
        reporte.material_id, reporte.zona_id, reporte.tamano_id)
    )
    conn.commit(); nuevo_id = cursor.lastrowid; conn.close()
    return {"id": nuevo_id, **reporte.dict()}

@router_reportes.get("/{id}", summary="Obtener reporte por ID")
def obtener_reporte(id: int):
    """Retorna un reporte específico con todos sus detalles."""
    conn = get_connection()
    r = conn.execute("SELECT * FROM reportes WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not r: error_404("Reporte", id)
    return dict(r)

@router_reportes.put("/{id}", summary="Actualizar reporte")
def actualizar_reporte(id: int, datos: ReporteUpdate):
    """Modifica los datos de un reporte existente."""
    conn = get_connection()
    if not conn.execute("SELECT id FROM reportes WHERE id = ?", (id,)).fetchone():
        conn.close(); error_404("Reporte", id)
    campos = {k: v for k, v in datos.dict().items() if v is not None}
    if campos:
        set_clause = ", ".join([f"{k} = ?" for k in campos])
        conn.execute(f"UPDATE reportes SET {set_clause} WHERE id = ?", list(campos.values()) + [id])
        conn.commit()
    conn.close()
    return {"mensaje": f"Reporte {id} actualizado", "campos": list(campos.keys())}

@router_reportes.delete("/{id}", summary="Eliminar reporte")
def eliminar_reporte(id: int):
    """Elimina un reporte de residuo."""
    conn = get_connection()
    if not conn.execute("SELECT id FROM reportes WHERE id = ?", (id,)).fetchone():
        conn.close(); error_404("Reporte", id)
    conn.execute("DELETE FROM reportes WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return {"mensaje": f"Reporte {id} eliminado exitosamente"}
