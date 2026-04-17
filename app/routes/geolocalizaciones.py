import pymysql
from fastapi import APIRouter, HTTPException
from app.models import get_connection
from app.validators import GeoCreate, GeoUpdate
from app.routes.utils import error_404

router_geos = APIRouter(prefix="/geolocalizaciones", tags=[" Geolocalizaciones"])

@router_geos.get("/", summary="Listar geolocalizaciones")
def listar_geos():
    """Consulta todas las coordenadas GPS registradas."""
    conn = get_connection()
    geos = conn.execute("SELECT * FROM geolocalizaciones ORDER BY id").fetchall()
    conn.close()
    return [dict(g) for g in geos]

@router_geos.post("/", status_code=201, summary="Registrar geolocalización")
def crear_geo(geo: GeoCreate):
    """Registra las coordenadas GPS de un reporte."""
    conn = get_connection()
    if not conn.execute("SELECT id FROM reportes WHERE id = %s", (geo.reporte_id,)).fetchone():
        conn.close(); raise HTTPException(status_code=404, detail="El reporte no existe")
    try:
        cursor = conn.execute(
            "INSERT INTO geolocalizaciones (latitud, longitud, altitud, precision_gps, reporte_id) VALUES (%s,%s,%s,%s,%s)",
            (geo.latitud, geo.longitud, geo.altitud, geo.precision_gps, geo.reporte_id)
        )
        conn.commit(); nuevo_id = cursor.lastrowid; conn.close()
        return {"id": nuevo_id, **geo.dict()}
    except pymysql.err.IntegrityError:
        conn.close(); raise HTTPException(status_code=422, detail="Este reporte ya tiene geolocalización")

@router_geos.get("/{id}", summary="Obtener geolocalización por ID")
def obtener_geo(id: int):
    conn = get_connection()
    g = conn.execute("SELECT * FROM geolocalizaciones WHERE id = %s", (id,)).fetchone()
    conn.close()
    if not g: error_404("Geolocalizacion", id)
    return dict(g)

@router_geos.put("/{id}", summary="Actualizar geolocalización")
def actualizar_geo(id: int, datos: GeoUpdate):
    conn = get_connection()
    if not conn.execute("SELECT id FROM geolocalizaciones WHERE id = %s", (id,)).fetchone():
        conn.close(); error_404("Geolocalizacion", id)
    campos = {k: v for k, v in datos.dict().items() if v is not None}
    if campos:
        set_clause = ", ".join([f"{k} = %s" for k in campos])
        conn.execute(f"UPDATE geolocalizaciones SET {set_clause} WHERE id = %s", list(campos.values()) + [id])
        conn.commit()
    conn.close()
    return {"mensaje": f"Geolocalizacion {id} actualizada"}

@router_geos.delete("/{id}", summary="Eliminar geolocalización")
def eliminar_geo(id: int):
    conn = get_connection()
    if not conn.execute("SELECT id FROM geolocalizaciones WHERE id = %s", (id,)).fetchone():
        conn.close(); error_404("Geolocalizacion", id)
    conn.execute("DELETE FROM geolocalizaciones WHERE id = %s", (id,))
    conn.commit(); conn.close()
    return {"mensaje": f"Geolocalizacion {id} eliminada exitosamente"}
