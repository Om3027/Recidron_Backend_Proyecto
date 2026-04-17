from .db import get_connection

# --- TIPOS DE RESIDUO ---
def get_all_types():
    conn = get_connection()
    tipos = conn.execute("SELECT * FROM tipos_residuo ORDER BY id").fetchall()
    conn.close()
    return [dict(t) for t in tipos]

def get_type_by_id(type_id: int):
    conn = get_connection()
    t = conn.execute("SELECT * FROM tipos_residuo WHERE id = %s", (type_id,)).fetchone()
    conn.close()
    return dict(t) if t else None

def create_type(nombre_tipo: str):
    conn = get_connection()
    cursor = conn.execute("INSERT INTO tipos_residuo (nombre_tipo) VALUES (%s)", (nombre_tipo,))
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return nuevo_id

def update_type(type_id: int, nombre_tipo: str):
    conn = get_connection()
    conn.execute("UPDATE tipos_residuo SET nombre_tipo = %s WHERE id = %s", (nombre_tipo, type_id))
    conn.commit()
    conn.close()

def delete_type(type_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM tipos_residuo WHERE id = %s", (type_id,))
    conn.commit()
    conn.close()


# --- MATERIALES ---
def get_all_materials():
    conn = get_connection()
    mats = conn.execute("SELECT * FROM materiales ORDER BY id").fetchall()
    conn.close()
    return [dict(m) for m in mats]

def get_material_by_id(material_id: int):
    conn = get_connection()
    m = conn.execute("SELECT * FROM materiales WHERE id = %s", (material_id,)).fetchone()
    conn.close()
    return dict(m) if m else None

def create_material(nombre_material: str):
    conn = get_connection()
    cursor = conn.execute("INSERT INTO materiales (nombre_material) VALUES (%s)", (nombre_material,))
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return nuevo_id

def update_material(material_id: int, nombre_material: str):
    conn = get_connection()
    conn.execute("UPDATE materiales SET nombre_material = %s WHERE id = %s", (nombre_material, material_id))
    conn.commit()
    conn.close()

def delete_material(material_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM materiales WHERE id = %s", (material_id,))
    conn.commit()
    conn.close()


# --- ZONAS CAMPUS ---
def get_all_zones():
    conn = get_connection()
    zonas = conn.execute("SELECT * FROM zonas_campus ORDER BY id").fetchall()
    conn.close()
    return [dict(z) for z in zonas]

def get_zone_by_id(zone_id: int):
    conn = get_connection()
    z = conn.execute("SELECT * FROM zonas_campus WHERE id = %s", (zone_id,)).fetchone()
    conn.close()
    return dict(z) if z else None

def create_zone(nombre_zona: str):
    conn = get_connection()
    cursor = conn.execute("INSERT INTO zonas_campus (nombre_zona) VALUES (%s)", (nombre_zona,))
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return nuevo_id

def update_zone(zone_id: int, nombre_zona: str):
    conn = get_connection()
    conn.execute("UPDATE zonas_campus SET nombre_zona = %s WHERE id = %s", (nombre_zona, zone_id))
    conn.commit()
    conn.close()

def delete_zone(zone_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM zonas_campus WHERE id = %s", (zone_id,))
    conn.commit()
    conn.close()


# --- TAMAÑOS ---
def get_all_sizes():
    conn = get_connection()
    tamanos = conn.execute("SELECT * FROM tamanos ORDER BY id").fetchall()
    conn.close()
    return [dict(t) for t in tamanos]

def get_size_by_id(size_id: int):
    conn = get_connection()
    t = conn.execute("SELECT * FROM tamanos WHERE id = %s", (size_id,)).fetchone()
    conn.close()
    return dict(t) if t else None

def create_size(nombre_tamano: str):
    conn = get_connection()
    cursor = conn.execute("INSERT INTO tamanos (nombre_tamano) VALUES (%s)", (nombre_tamano,))
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return nuevo_id

def update_size(size_id: int, nombre_tamano: str):
    conn = get_connection()
    conn.execute("UPDATE tamanos SET nombre_tamano = %s WHERE id = %s", (nombre_tamano, size_id))
    conn.commit()
    conn.close()

def delete_size(size_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM tamanos WHERE id = %s", (size_id,))
    conn.commit()
    conn.close()
