from .db import get_connection

# --- REPORTES ---
def get_all_reports():
    conn = get_connection()
    reportes = conn.execute("SELECT * FROM reportes ORDER BY fecha_reporte DESC").fetchall()
    conn.close()
    return [dict(r) for r in reportes]

def get_report_by_id(report_id: int):
    conn = get_connection()
    r = conn.execute("SELECT * FROM reportes WHERE id = %s", (report_id,)).fetchone()
    conn.close()
    return dict(r) if r else None

def create_report(descripcion, usuario_id, tipo_residuo_id, material_id, zona_id, tamano_id):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO reportes (descripcion, usuario_id, tipo_residuo_id, material_id, zona_id, tamano_id) VALUES (%s,%s,%s,%s,%s,%s)",
        (descripcion, usuario_id, tipo_residuo_id, material_id, zona_id, tamano_id)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return nuevo_id

def update_report(report_id: int, campos: dict):
    conn = get_connection()
    set_clause = ", ".join([f"{k} = %s" for k in campos])
    conn.execute(f"UPDATE reportes SET {set_clause} WHERE id = %s", list(campos.values()) + [report_id])
    conn.commit()
    conn.close()

def delete_report(report_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM reportes WHERE id = %s", (report_id,))
    conn.commit()
    conn.close()


# --- GEOLOCALIZACIONES ---
def get_all_geos():
    conn = get_connection()
    geos = conn.execute("SELECT * FROM geolocalizaciones ORDER BY id").fetchall()
    conn.close()
    return [dict(g) for g in geos]

def get_geo_by_id(geo_id: int):
    conn = get_connection()
    g = conn.execute("SELECT * FROM geolocalizaciones WHERE id = %s", (geo_id,)).fetchone()
    conn.close()
    return dict(g) if g else None

def create_geo(latitud, longitud, altitud, precision_gps, reporte_id):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO geolocalizaciones (latitud, longitud, altitud, precision_gps, reporte_id) VALUES (%s,%s,%s,%s,%s)",
        (latitud, longitud, altitud, precision_gps, reporte_id)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return nuevo_id

def update_geo(geo_id: int, campos: dict):
    conn = get_connection()
    set_clause = ", ".join([f"{k} = %s" for k in campos])
    conn.execute(f"UPDATE geolocalizaciones SET {set_clause} WHERE id = %s", list(campos.values()) + [geo_id])
    conn.commit()
    conn.close()

def delete_geo(geo_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM geolocalizaciones WHERE id = %s", (geo_id,))
    conn.commit()
    conn.close()
