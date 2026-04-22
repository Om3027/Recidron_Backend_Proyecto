import mysql.connector
from mysql.connector import errorcode

def run_migrations(cursor):
    """
    Ejecuta scripts de migración (ALTER TABLE) para asegurar columnas nuevas.
    """
    # 1. Código Estudiantil
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN codigo_estudiantil VARCHAR(20) AFTER password")
        print("[ MOD ] Columna 'codigo_estudiantil' añadida.")
    except mysql.connector.Error as err:
        if err.errno != errorcode.ER_DUP_FIELDNAME: print(f"Error col codigo: {err}")

    # 2. Estado Activo (Soft Delete)
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN es_activo TINYINT(1) NOT NULL DEFAULT 1 AFTER codigo_estudiantil")
        print("[ MOD ] Columna 'es_activo' añadida.")
    except mysql.connector.Error as err:
        if err.errno != errorcode.ER_DUP_FIELDNAME: print(f"Error col es_activo: {err}")

    # 3. Rol ID (RBAC)
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN rol_id INT AFTER es_activo")
        cursor.execute("UPDATE usuarios SET rol_id = 2 WHERE rol_id IS NULL")
        cursor.execute("ALTER TABLE usuarios MODIFY rol_id INT NOT NULL")
        cursor.execute("ALTER TABLE usuarios ADD FOREIGN KEY (rol_id) REFERENCES roles(id)")
        print("[ MOD ] Columna 'rol_id' y FK configuradas.")
    except mysql.connector.Error as err:
        if err.errno != errorcode.ER_DUP_FIELDNAME: 
            if err.errno != 121: print(f"Error col rol_id: {err}")

    # 4. Logs de Auditoría (Sincronizar nombres y campos)
    try:
        # Intentar renombrar 'tabla' a 'recurso' si existe la vieja
        cursor.execute("ALTER TABLE logs_auditoria CHANGE tabla recurso VARCHAR(100) NOT NULL")
        print("[ MOD ] Columna 'tabla' renombrada a 'recurso' en logs.")
    except mysql.connector.Error:
        try:
            cursor.execute("ALTER TABLE logs_auditoria ADD COLUMN recurso VARCHAR(100) NOT NULL AFTER accion")
            print("[ MOD ] Columna 'recurso' añadida.")
        except mysql.connector.Error as e:
            if e.errno != errorcode.ER_DUP_FIELDNAME: print(f"Error col recurso: {e}")

    # Asegurar que exista 'detalles'
    try:
        cursor.execute("ALTER TABLE logs_auditoria ADD COLUMN detalles TEXT AFTER recurso")
        print("[ MOD ] Columna 'detalles' añadida.")
    except mysql.connector.Error as e:
        if e.errno != errorcode.ER_DUP_FIELDNAME: print(f"Error col detalles: {e}")

    # Asegurar que existan los valores de auditoría
    try:
        cursor.execute("ALTER TABLE logs_auditoria ADD COLUMN valor_anterior TEXT AFTER detalles")
        cursor.execute("ALTER TABLE logs_auditoria ADD COLUMN valor_nuevo TEXT AFTER valor_anterior")
        print("[ MOD ] Columnas de valores de auditoría añadidas.")
    except mysql.connector.Error as e:
        if e.errno != errorcode.ER_DUP_FIELDNAME: print(f"Error cols valores logs: {e}")

    # 5. Asegurar 'es_activo' en todas las tablas del proyecto
    tablas_maestras = ["reportes", "materiales", "tipos_residuo", "zonas_campus", "tamanos"]
    for tabla in tablas_maestras:
        try:
            cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN es_activo TINYINT(1) NOT NULL DEFAULT 1")
            print(f"[ MOD ] Columna 'es_activo' asegurada en '{tabla}'.")
        except mysql.connector.Error as e:
            if e.errno != errorcode.ER_DUP_FIELDNAME: print(f"Error col es_activo en {tabla}: {e}")
