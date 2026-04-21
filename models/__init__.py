import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()
from utils.security import get_password_hash

# Configuración de la base de datos (Aiven Cloud)
DB_CONFIG = {
    'host':      os.getenv('DB_HOST'),
    'port':      os.getenv('DB_PORT', 16491),
    'user':      os.getenv('DB_USER'),
    'password':  os.getenv('DB_PASSWORD'),
    'database':  os.getenv('DB_NAME'),
    # Aiven requiere SSL por defecto.
}

def get_connection():
    """
    Crea y retorna una conexión a la base de datos MySQL en Aiven Cloud.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        raise

def init_db():
    """
    Inicializa la base de datos en MySQL con el nuevo esquema RBAC y Soft-Delete.
    Sincroniza las tablas necesarias para la migración desde SQLite.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # --- TABLAS DE SEGURIDAD (RBAC Avanzado) ---
    
    # Roles: admin, autor
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            nombre_rol VARCHAR(50) NOT NULL UNIQUE
        ) ENGINE=InnoDB;
    """)

    # Permisos: recurso:accion
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS permisos (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            nombre_permiso  VARCHAR(100) NOT NULL UNIQUE
        ) ENGINE=InnoDB;
    """)

    # Relación Roles-Permisos (Pivote)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rol_permisos (
            rol_id      INT NOT NULL,
            permiso_id  INT NOT NULL,
            PRIMARY KEY (rol_id, permiso_id),
            FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE,
            FOREIGN KEY (permiso_id) REFERENCES permisos(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
    """)

    # Usuarios (con Soft-Delete: es_activo)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            nombre     VARCHAR(100) NOT NULL,
            email      VARCHAR(150) NOT NULL UNIQUE,
            password   VARCHAR(255) NOT NULL,
            codigo_estudiantil VARCHAR(20),
            es_activo  TINYINT(1)   NOT NULL DEFAULT 1,
            rol_id     INT          NOT NULL,
            creado_en  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (rol_id) REFERENCES roles(id)
        ) ENGINE=InnoDB;
    """)

    # Sesiones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sesiones (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id  INT NOT NULL,
            token       VARCHAR(255) NOT NULL UNIQUE,
            creado_en   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
            expira_en   DATETIME     NOT NULL,
            activa      TINYINT(1)   NOT NULL DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
    """)

    # Auditoría (Historial de cambios conforme a estándares administrativos)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs_auditoria (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id  INT,
            accion      VARCHAR(100) NOT NULL,
            recurso     VARCHAR(100) NOT NULL,
            detalles    TEXT,
            valor_anterior TEXT,
            valor_nuevo    TEXT,
            fecha       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
        ) ENGINE=InnoDB;
    """)

    # --- TABLAS DEL PROYECTO (Recidron App) ---

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tipos_residuo (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            nombre_tipo VARCHAR(100) NOT NULL UNIQUE,
            es_activo   TINYINT(1)   NOT NULL DEFAULT 1
        ) ENGINE=InnoDB;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiales (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            nombre_material VARCHAR(100) NOT NULL UNIQUE,
            es_activo       TINYINT(1)   NOT NULL DEFAULT 1
        ) ENGINE=InnoDB;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS zonas_campus (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            nombre_zona VARCHAR(100) NOT NULL UNIQUE,
            es_activo   TINYINT(1)   NOT NULL DEFAULT 1
        ) ENGINE=InnoDB;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tamanos (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            nombre_tamano VARCHAR(100) NOT NULL UNIQUE,
            es_activo     TINYINT(1)   NOT NULL DEFAULT 1
        ) ENGINE=InnoDB;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reportes (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            descripcion     TEXT,
            fecha_reporte   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            es_activo       TINYINT(1) NOT NULL DEFAULT 1,
            usuario_id      INT NOT NULL,
            tipo_residuo_id INT NOT NULL,
            material_id     INT NOT NULL,
            zona_id         INT NOT NULL,
            tamano_id       INT NOT NULL,
            FOREIGN KEY (usuario_id)      REFERENCES usuarios(id),
            FOREIGN KEY (tipo_residuo_id) REFERENCES tipos_residuo(id),
            FOREIGN KEY (material_id)     REFERENCES materiales(id),
            FOREIGN KEY (zona_id)         REFERENCES zonas_campus(id),
            FOREIGN KEY (tamano_id)       REFERENCES tamanos(id)
        ) ENGINE=InnoDB;
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS geolocalizaciones (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            latitud    DECIMAL(10, 8) NOT NULL,
            longitud   DECIMAL(11, 8) NOT NULL,
            altitud    DECIMAL(10, 2),
            `precision`  DECIMAL(10, 2),
            reporte_id INT NOT NULL UNIQUE,
            FOREIGN KEY (reporte_id) REFERENCES reportes(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
    """)

    # --- MIGRACIONES (Asegurar columnas nuevas) ---
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

    # --- DATOS INICIALES (Seed) ---
    _seed_roles(cursor)
    _seed_permisos(cursor)
    _seed_list(cursor, 'tipos_residuo', 'nombre_tipo',     ['Aprovechable', 'Orgánico', 'No Aprovechable', 'Peligroso'])
    _seed_list(cursor, 'materiales',   'nombre_material', ['Plástico', 'Vidrio', 'Cartón/Papel', 'Metal', 'Residuos Orgánicos', 'Restos de Comida'])
    _seed_list(cursor, 'zonas_campus', 'nombre_zona',     ['Biblioteca', 'Edificio A', 'Edificio B', 'Cafetería', 'Zona Deportiva', 'Parqueadero'])
    _seed_list(cursor, 'tamanos',      'nombre_tamano',   ['Leve', 'Mediano (2-5kg)', 'Crítico'])
    _seed_admin_maestro(cursor)
    _sync_permisos_roles(cursor)

    conn.commit()
    cursor.close()
    conn.close()
    print('[ OK ] MySQL - Base de datos sincronizada correctamente.')

def _seed_roles(cursor):
    cursor.execute("SELECT COUNT(*) FROM roles")
    if cursor.fetchone()[0] == 0:
        roles = [('admin',), ('autor',)]
        cursor.executemany("INSERT INTO roles (nombre_rol) VALUES (%s)", roles)

def _seed_permisos(cursor):
    cursor.execute("SELECT COUNT(*) FROM permisos")
    if cursor.fetchone()[0] == 0:
        permisos = [
            ('usuarios:leer',), ('usuarios:crear',), ('usuarios:editar',), ('usuarios:eliminar',),
            ('reportes:leer',), ('reportes:crear',), ('reportes:editar',), ('reportes:eliminar',),
            ('audit:leer',),
            ('catalogos:gestionar',)
        ]
        cursor.executemany("INSERT INTO permisos (nombre_permiso) VALUES (%s)", permisos)
        
        # El rol 'admin' recibe todos los permisos
        cursor.execute("SELECT id FROM roles WHERE nombre_rol = 'admin'")
        admin_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM permisos")
        p_ids = [row[0] for row in cursor.fetchall()]
        relaciones_admin = [(admin_id, p_id) for p_id in p_ids]
        cursor.executemany("INSERT INTO rol_permisos (rol_id, permiso_id) VALUES (%s, %s)", relaciones_admin)

        # El rol 'autor' (estudiante) recibe permisos limitados
        cursor.execute("SELECT id FROM roles WHERE nombre_rol = 'autor'")
        res_autor = cursor.fetchone()
        if res_autor:
            autor_id = res_autor[0]
            # Permisos permitidos para estudiantes
            permisos_estudiante = ['reportes:leer', 'reportes:crear', 'usuarios:leer']
            cursor.execute("SELECT id FROM permisos WHERE nombre_permiso IN (%s, %s, %s)" % ("%s", "%s", "%s"), permisos_estudiante)
            est_p_ids = [row[0] for row in cursor.fetchall()]
            relaciones_autor = [(autor_id, p_id) for p_id in est_p_ids]
            cursor.executemany("INSERT INTO rol_permisos (rol_id, permiso_id) VALUES (%s, %s)", relaciones_autor)

def _sync_permisos_roles(cursor):
    """Garantiza que el Admin tenga todo y el Autor tenga lo básico."""
    # 1. Todo para Admin (Rol 1)
    cursor.execute("INSERT IGNORE INTO rol_permisos (rol_id, permiso_id) SELECT 1, id FROM permisos")

    # 2. Lo básico para Autor (Rol 2)
    # Buscamos los IDs de reportes:leer, reportes:crear, usuarios:leer
    permisos_autor = ['reportes:leer', 'reportes:crear', 'usuarios:leer']
    query_id = "SELECT id FROM permisos WHERE nombre_permiso IN (%s, %s, %s)"
    cursor.execute(query_id, tuple(permisos_autor))
    ids = [row[0] for row in cursor.fetchall()]
    
    for p_id in ids:
        cursor.execute("INSERT IGNORE INTO rol_permisos (rol_id, permiso_id) VALUES (2, %s)", (p_id,))
    
    print("[ OK ] Permisos de roles sincronizados automáticamente.")

def _seed_admin_maestro(cursor):
    """Crea el usuario administrador maestro si no existe, usando datos del .env."""
    import os
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_name  = os.getenv('ADMIN_NAME', 'Admin Root')
    admin_pass  = os.getenv('ADMIN_PASSWORD')
    
    if not admin_email or not admin_pass:
        return

    cursor.execute("SELECT id FROM usuarios WHERE email = %s", (admin_email,))
    if not cursor.fetchone():
        # Asignar rol_id = 1 (admin)
        hashed_pass = get_password_hash(admin_pass)
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password, rol_id) VALUES (%s, %s, %s, %s)",
            (admin_name, admin_email, hashed_pass, 1)
        )
        print(f"[ SEED ] Administrador Maestro creado: {admin_email}")

def _seed_list(cursor, tabla, campo, valores):
    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
    if cursor.fetchone()[0] == 0:
        data = [(v,) for v in valores]
        cursor.executemany(f"INSERT INTO {tabla} ({campo}) VALUES (%s)", data)