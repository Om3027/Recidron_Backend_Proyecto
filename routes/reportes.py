from fastapi import APIRouter, HTTPException, Depends
from models import get_connection
from validators import ReporteCreate, ReporteUpdate
from routes.utils import error_404, registrar_log
from routes.auth import check_permission

router_reportes = APIRouter(prefix="/reportes", tags=[" Reportes"])

@router_reportes.get("/", summary="Listar todos los reportes")
def listar_reportes(user: dict = Depends(check_permission("reportes:leer"))):
    """Consulta todos los reportes de residuos registrados (solo activos)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reportes WHERE es_activo = 1 ORDER BY fecha_reporte DESC")
    reportes = cursor.fetchall()
    cursor.close()
    conn.close()
    return reportes

@router_reportes.post("/", status_code=201, summary="Crear un reporte")
def crear_reporte(reporte: ReporteCreate, user: dict = Depends(check_permission("reportes:crear"))):
    """Registra un nuevo reporte de residuo y lo audita."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Validaciones de llaves foráneas
    checks = [
        ("usuarios",      reporte.usuario_id,      "Usuario"),
        ("tipos_residuo", reporte.tipo_residuo_id,  "TipoResiduo"),
        ("materiales",    reporte.material_id,       "Material"),
        ("zonas_campus",  reporte.zona_id,           "Zona"),
        ("tamanos",       reporte.tamano_id,         "Tamano"),
    ]
    for tabla, fk_id, nombre in checks:
        cursor.execute(f"SELECT id FROM {tabla} WHERE id = %s AND es_activo = 1", (fk_id,))
        if not cursor.fetchone():
            cursor.close(); conn.close()
            raise HTTPException(status_code=404, detail=f"{nombre} con id {fk_id} no existe o está inactivo")

    # Inserción
    query = """
        INSERT INTO reportes (descripcion, usuario_id, tipo_residuo_id, material_id, zona_id, tamano_id) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (reporte.descripcion, reporte.usuario_id, reporte.tipo_residuo_id,
              reporte.material_id, reporte.zona_id, reporte.tamano_id)
    cursor.execute(query, params)
    nuevo_id = cursor.lastrowid
    conn.commit()
    
    # Auditoría
    registrar_log(user['id'], "CREAR", "reportes", f"Reporte {nuevo_id} creado", v_nuevo=reporte.dict())
    
    cursor.close()
    conn.close()
    return {"id": nuevo_id, **reporte.dict()}

@router_reportes.get("/{id}", summary="Obtener reporte por ID")
def obtener_reporte(id: int, user: dict = Depends(check_permission("reportes:leer"))):
    """Retorna un reporte específico que esté activo."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reportes WHERE id = %s AND es_activo = 1", (id,))
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    if not r: error_404("Reporte", id)
    return r

@router_reportes.put("/{id}", summary="Actualizar reporte")
def actualizar_reporte(id: int, datos: ReporteUpdate, user: dict = Depends(check_permission("reportes:editar"))):
    """Modifica los datos de un reporte activo y registra el cambio anterior/nuevo."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Obtener estado anterior para el log
    cursor.execute("SELECT * FROM reportes WHERE id = %s AND es_activo = 1", (id,))
    v_anterior = cursor.fetchone()
    if not v_anterior:
        cursor.close(); conn.close(); error_404("Reporte", id)
    
    campos = {k: v for k, v in datos.dict().items() if v is not None}
    if campos:
        set_clause = ", ".join([f"{k} = %s" for k in campos])
        cursor.execute(f"UPDATE reportes SET {set_clause} WHERE id = %s", list(campos.values()) + [id])
        conn.commit()
        
        # Auditoría con trazabilidad de valores
        registrar_log(user['id'], "ACTUALIZAR", "reportes", f"Reporte {id} modificado", 
                      v_anterior=v_anterior, v_nuevo=campos)
    
    cursor.close()
    conn.close()
    return {"mensaje": f"Reporte {id} actualizado", "campos": list(campos.keys())}

@router_reportes.delete("/{id}", summary="Eliminar reporte (Soft-Delete)")
def eliminar_reporte(id: int, user: dict = Depends(check_permission("reportes:eliminar"))):
    """Realiza un borrado lógico (es_activo = 0) del reporte."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM reportes WHERE id = %s AND es_activo = 1", (id,))
    if not cursor.fetchone():
        cursor.close(); conn.close(); error_404("Reporte", id)
        
    cursor.execute("UPDATE reportes SET es_activo = 0 WHERE id = %s", (id,))
    conn.commit()
    
    registrar_log(user['id'], "ELIMINAR", "reportes", f"Reporte {id} marcado como inactivo (soft-delete)")
    
    cursor.close()
    conn.close()
    return {"mensaje": f"Reporte {id} eliminado exitosamente (lógico)"}

@router_reportes.get("/stats/my", summary="Estadísticas de mis reportes")
def obtener_mis_estadisticas(user: dict = Depends(check_permission("reportes:leer"))):
    """Retorna un resumen de la actividad del usuario autenticado."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Total de reportes propios
        cursor.execute("SELECT COUNT(*) as total FROM reportes WHERE usuario_id = %s AND es_activo = 1", (user['id'],))
        total = cursor.fetchone()['total']
        
        # 2. Material que más acostumbra reportar
        cursor.execute("""
            SELECT m.nombre_material as material, COUNT(r.id) as cantidad
            FROM reportes r
            JOIN materiales m ON r.material_id = m.id
            WHERE r.usuario_id = %s AND r.es_activo = 1
            GROUP BY m.id, m.nombre_material
            ORDER BY cantidad DESC LIMIT 1
        """, (user['id'],))
        top_material = cursor.fetchone()
        
        # 3. Zonas en las que ha participado
        cursor.execute("SELECT COUNT(DISTINCT zona_id) as zonas FROM reportes WHERE usuario_id = %s AND es_activo = 1", (user['id'],))
        zonas = cursor.fetchone()['zonas']
        
        return {
            "stats": [
                {"title": "Mis Reportes", "value": str(total), "subtitle": "Total acumulado"},
                {"title": "Zonas Limpias", "value": str(zonas), "subtitle": "Diferentes lugares"},
                {"title": "Material Top", "value": top_material['material'] if top_material else "Ninguno", "subtitle": "Más frecuente"},
                {"title": "Mi Rango", "value": "Colaborador", "subtitle": "Usuario activo"}
            ]
        }
    except Exception as e:
        print(f"Error en stats/my: {e}")
        return {"stats": []}
    finally:
        cursor.close()
        conn.close()
