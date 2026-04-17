from .db import get_connection

# --- ROLES ---
def get_all_roles():
    conn = get_connection()
    roles = conn.execute("SELECT * FROM roles ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in roles]

def get_role_by_id(role_id: int):
    conn = get_connection()
    role = conn.execute("SELECT * FROM roles WHERE id = %s", (role_id,)).fetchone()
    conn.close()
    return dict(role) if role else None

def create_role(nombre_rol: str):
    conn = get_connection()
    cursor = conn.execute("INSERT INTO roles (nombre_rol) VALUES (%s)", (nombre_rol,))
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return nuevo_id

def update_role(role_id: int, nombre_rol: str):
    conn = get_connection()
    conn.execute("UPDATE roles SET nombre_rol = %s WHERE id = %s", (nombre_rol, role_id))
    conn.commit()
    conn.close()

def delete_role(role_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM roles WHERE id = %s", (role_id,))
    conn.commit()
    conn.close()


# --- USUARIOS ---
def get_all_users():
    conn = get_connection()
    usuarios = conn.execute(
        "SELECT id, nombre, email, activo, rol_id, creado_en FROM usuarios ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(u) for u in usuarios]

def get_user_by_id(user_id: int):
    conn = get_connection()
    u = conn.execute(
        "SELECT id, nombre, email, activo, rol_id, creado_en FROM usuarios WHERE id = %s", (user_id,)
    ).fetchone()
    conn.close()
    return dict(u) if u else None

def create_user(nombre, email, password, rol_id):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO usuarios (nombre, email, password, rol_id) VALUES (%s, %s, %s, %s)",
        (nombre, email, password, rol_id)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return nuevo_id

def update_user(user_id: int, campos: dict):
    conn = get_connection()
    set_clause = ", ".join([f"{k} = %s" for k in campos])
    conn.execute(f"UPDATE usuarios SET {set_clause} WHERE id = %s", list(campos.values()) + [user_id])
    conn.commit()
    conn.close()

def deactivate_user(user_id: int):
    conn = get_connection()
    conn.execute("UPDATE usuarios SET activo = 0 WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()


# --- SESIONES ---
def get_all_sessions():
    conn = get_connection()
    sesiones = conn.execute("SELECT * FROM sesiones ORDER BY id").fetchall()
    conn.close()
    return [dict(s) for s in sesiones]

def get_session_by_id(session_id: int):
    conn = get_connection()
    s = conn.execute("SELECT * FROM sesiones WHERE id = %s", (session_id,)).fetchone()
    conn.close()
    return dict(s) if s else None

def create_session(usuario_id, token, expira_en):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO sesiones (usuario_id, token, expira_en) VALUES (%s, %s, %s)",
        (usuario_id, token, expira_en)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return nuevo_id

def update_session(session_id, usuario_id, token, expira_en):
    conn = get_connection()
    conn.execute(
        "UPDATE sesiones SET usuario_id=%s, token=%s, expira_en=%s WHERE id=%s",
        (usuario_id, token, expira_en, session_id)
    )
    conn.commit()
    conn.close()

def delete_session(session_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM sesiones WHERE id = %s", (session_id,))
    conn.commit()
    conn.close()


# --- LOGS ---
def get_all_logs():
    conn = get_connection()
    logs = conn.execute("SELECT * FROM logs_auditoria ORDER BY fecha DESC").fetchall()
    conn.close()
    return [dict(l) for l in logs]

def get_log_by_id(log_id: int):
    conn = get_connection()
    log = conn.execute("SELECT * FROM logs_auditoria WHERE id = %s", (log_id,)).fetchone()
    conn.close()
    return dict(log) if log else None

def create_log(usuario_id, accion, tabla, descripcion):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO logs_auditoria (usuario_id, accion, tabla, descripcion) VALUES (%s, %s, %s, %s)",
        (usuario_id, accion, tabla, descripcion)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return nuevo_id

def update_log(log_id, usuario_id, accion, tabla, descripcion):
    conn = get_connection()
    conn.execute(
        "UPDATE logs_auditoria SET usuario_id=%s, accion=%s, tabla=%s, descripcion=%s WHERE id=%s",
        (usuario_id, accion, tabla, descripcion, log_id)
    )
    conn.commit()
    conn.close()

def delete_log(log_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM logs_auditoria WHERE id = %s", (log_id,))
    conn.commit()
    conn.close()
