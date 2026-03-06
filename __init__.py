
# Define las tablas de la base de datos y las crea automáticamente.
# Usamos sqlite3 puro — igual a como lo hacías en tu clase GestorBaseDatos.
#
# Tablas del PGC (Proyecto de Generación de Conocimiento):
#   - roles, usuarios, tipos_residuo, materiales, zonas_campus, tamanos
#   - reportes, geolocalizaciones
#
# Tablas de Seguridad Informática:
#   - sesiones, logs_auditoria


import sqlite3
import os

# Ruta del archivo de base de datos — se crea automáticamente
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'recidron.db')


def get_connection():
    """
    Crea y retorna una conexión a la base de datos SQLite.
    row_factory permite acceder a los datos como diccionario:
    fila["nombre"] en vez de fila[0]
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Crea todas las tablas si no existen.
    Este es el equivalente al script DDL que pide el profe.
    Se ejecuta automáticamente al arrancar la API.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""

        
        -- TABLAS DE SEGURIDAD INFORMÁTICA
        -- Roles de usuario: Administrador, Invitado

        CREATE TABLE IF NOT EXISTS roles (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_rol TEXT NOT NULL UNIQUE
        );

        -- Usuarios del sistema con autenticación por roles
        CREATE TABLE IF NOT EXISTS usuarios (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre     TEXT    NOT NULL,
            email      TEXT    NOT NULL UNIQUE,
            password   TEXT    NOT NULL,
            activo     INTEGER NOT NULL DEFAULT 1,
            rol_id     INTEGER NOT NULL,
            creado_en  TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (rol_id) REFERENCES roles(id)
        );

        -- Sesiones activas — control de acceso por token
    
        CREATE TABLE IF NOT EXISTS sesiones (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id  INTEGER NOT NULL,
            token       TEXT    NOT NULL UNIQUE,
            creado_en   TEXT    DEFAULT CURRENT_TIMESTAMP,
            expira_en   TEXT    NOT NULL,
            activa      INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );

        -- Auditoría — registro de acciones importantes del sistema

        CREATE TABLE IF NOT EXISTS logs_auditoria (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id  INTEGER,
            accion      TEXT NOT NULL,
            tabla       TEXT NOT NULL,
            descripcion TEXT,
            fecha       TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );

        -- TABLAS DEL PGC — Recidron App
        -- Tipos de residuo: Aprovechable, No Aprovechable, Orgánico, Peligroso

        CREATE TABLE IF NOT EXISTS tipos_residuo (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_tipo TEXT NOT NULL UNIQUE
        );

        -- Material del residuo: Plástico, Icopor, Metal, Papel/Cartón, Vidrio

        CREATE TABLE IF NOT EXISTS materiales (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_material TEXT NOT NULL UNIQUE
        );

        -- Zonas del campus universitario

        CREATE TABLE IF NOT EXISTS zonas_campus (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_zona TEXT NOT NULL UNIQUE
        );

        -- Tamaño estimado del residuo: Pequeño, Mediano, Grande

        CREATE TABLE IF NOT EXISTS tamanos (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_tamano TEXT NOT NULL UNIQUE
        );

        -- Reportes de residuos — tabla principal del sistema
    
        CREATE TABLE IF NOT EXISTS reportes (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion     TEXT,
            fecha_reporte   TEXT    DEFAULT CURRENT_TIMESTAMP,
            usuario_id      INTEGER NOT NULL,
            tipo_residuo_id INTEGER NOT NULL,
            material_id     INTEGER NOT NULL,
            zona_id         INTEGER NOT NULL,
            tamano_id       INTEGER NOT NULL,
            FOREIGN KEY (usuario_id)      REFERENCES usuarios(id),
            FOREIGN KEY (tipo_residuo_id) REFERENCES tipos_residuo(id),
            FOREIGN KEY (material_id)     REFERENCES materiales(id),
            FOREIGN KEY (zona_id)         REFERENCES zonas_campus(id),
            FOREIGN KEY (tamano_id)       REFERENCES tamanos(id)
        );

        -- Coordenadas GPS de cada reporte
        CREATE TABLE IF NOT EXISTS geolocalizaciones (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            latitud    REAL    NOT NULL,
            longitud   REAL    NOT NULL,
            altitud    REAL,
            precision  REAL,
            reporte_id INTEGER NOT NULL UNIQUE,
            FOREIGN KEY (reporte_id) REFERENCES reportes(id)
        );

    """)

    # SEED — Datos iniciales (solo inserta si la tabla está vacía)
    _seed(cursor, 'roles',        'nombre_rol',      ['Administrador', 'Invitado'])
    _seed(cursor, 'tipos_residuo','nombre_tipo',     ['Aprovechable', 'No Aprovechable', 'Orgánico', 'Peligroso'])
    _seed(cursor, 'materiales',   'nombre_material', ['Plástico', 'Icopor', 'Metal', 'Papel/Cartón', 'Vidrio'])
    _seed(cursor, 'zonas_campus', 'nombre_zona',     ['Entrada Principal', 'Bloque A', 'Bloque B', 'Canchas', 'Cafetería', 'Parqueadero'])
    _seed(cursor, 'tamanos',      'nombre_tamano',   ['Pequeño', 'Mediano', 'Grande'])

    conn.commit()
    conn.close()
    print('[ OK ] Base de datos lista.')


def _seed(cursor, tabla, campo, valores):
    """Inserta valores iniciales solo si la tabla está vacía."""
    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
    if cursor.fetchone()[0] == 0:
        for valor in valores:
            cursor.execute(f"INSERT INTO {tabla} ({campo}) VALUES (?)", (valor,))