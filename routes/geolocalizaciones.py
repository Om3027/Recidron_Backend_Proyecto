from fastapi import APIRouter, HTTPException, Depends
from models import get_connection
from validators import GeoCreate, GeoUpdate
from routes.utils import error_404, registrar_log
from routes.auth import check_permission
import mysql.connector

router_geos = APIRouter(prefix="/geos", tags=[" Geolocalizaciones"])

@router_geos.get("/", summary="Listar geolocalizaciones")
def listar_geos(user_auth: dict = Depends(check_permission("reportes:leer"))):
    """Lista coordenadas GPS de reportes activos."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    # Solo traemos geos de reportes que estén activos
    query = """
        SELECT g.* FROM geolocalizaciones g
        JOIN reportes r ON g.reporte_id = r.id
        WHERE r.es_activo = 1
    """
    cursor.execute(query)
    geos = cursor.fetchall()
    cursor.close()
    conn.close()
    return geos

@router_geos.post("/", status_code=201, summary="Registrar geolocalización")
def crear_geo(geo: GeoCreate, user_auth: dict = Depends(check_permission("reportes:crear"))):
    """Asocia coordenadas GPS a un reporte con auditoría."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Validar que el reporte exista y esté activo
    cursor.execute("SELECT id FROM reportes WHERE id = %s AND es_activo = 1", (geo.reporte_id,))
    if not cursor.fetchone():
        cursor.close(); conn.close()
        raise HTTPException(status_code=404, detail="El reporte no existe o está inactivo")
        
    try:
        query = """
            INSERT INTO geolocalizaciones (latitud, longitud, altitud, `precision`, reporte_id) 
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (geo.latitud, geo.longitud, geo.altitud, geo.precision, geo.reporte_id)
        cursor.execute(query, params)
        nuevo_id = cursor.lastrowid
        conn.commit()
        
        registrar_log(user_auth['id'], "CREAR", "geolocalizaciones", f"Geo {nuevo_id} para reporte {geo.reporte_id}", v_nuevo=geo.dict())
        
        cursor.close()
        conn.close()
        return {"id": nuevo_id, **geo.dict()}
    except mysql.connector.Error as err:
        cursor.close(); conn.close()
        if err.errno == 1062:
            raise HTTPException(status_code=422, detail="Ya existe una geolocalización para este reporte")
        raise HTTPException(status_code=500, detail="Error al crear geolocalización")

@router_geos.get("/{id}", summary="Obtener geolocalización por ID")
def obtener_geo(id: int, user_auth: dict = Depends(check_permission("reportes:leer"))):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM geolocalizaciones WHERE id = %s", (id,))
    g = cursor.fetchone()
    cursor.close()
    conn.close()
    if not g: error_404("Geolocalización", id)
    return g

@router_geos.put("/{id}", summary="Actualizar geolocalización")
def actualizar_geo(id: int, datos: GeoUpdate, user_auth: dict = Depends(check_permission("reportes:editar"))):
    """Actualiza coordenadas con auditoría."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM geolocalizaciones WHERE id = %s", (id,))
    v_anterior = cursor.fetchone()
    if not v_anterior:
        cursor.close(); conn.close(); error_404("Geolocalización", id)
        
    campos = {k: v for k, v in datos.dict().items() if v is not None}
    if campos:
        set_clause = ", ".join([f"`{k}` = %s" for k in campos])
        cursor.execute(f"UPDATE geolocalizaciones SET {set_clause} WHERE id = %s", list(campos.values()) + [id])
        conn.commit()
        
        registrar_log(user_auth['id'], "ACTUALIZAR", "geolocalizaciones", f"Geo {id} modificada", 
                      v_anterior=v_anterior, v_nuevo=campos)
                      
    cursor.close()
    conn.close()
    return {"mensaje": f"Geolocalización {id} actualizada", "campos": list(campos.keys())}

@router_geos.delete("/{id}", summary="Eliminar geolocalización")
def eliminar_geo(id: int, user_auth: dict = Depends(check_permission("reportes:eliminar"))):
    """Elimina físicamente la geolocalización (usualmente ligada al reporte)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, reporte_id FROM geolocalizaciones WHERE id = %s", (id,))
    geo = cursor.fetchone()
    if not geo:
        cursor.close(); conn.close(); error_404("Geolocalización", id)
        
    cursor.execute("DELETE FROM geolocalizaciones WHERE id = %s", (id,))
    conn.commit()
    
    registrar_log(user_auth['id'], "ELIMINAR", "geolocalizaciones", f"Geo {id} eliminada para reporte {geo[1]}")
    
    cursor.close()
    conn.close()
    return {"mensaje": f"Geolocalización {id} eliminada físicamente"}
