
# Define las tablas de la base de datos y las crea automáticamente.
# Usamos sqlite3 puro — igual a como lo hacías en tu clase GestorBaseDatos.
#
# Tablas del PGC (Proyecto de Generación de Conocimiento):
#   - roles, usuarios, tipos_residuo, materiales, zonas_campus, tamanos
#   - reportes, geolocalizaciones
#
# Tablas de Seguridad Informática:
#   - sesiones, logs_auditoria


#import sqlite3
import os
import pymysql
import dotenv
dotenv.load_dotenv(dotenv_path='.env.test')
# Ruta del archivo de base de datos — se crea automáticamente
#DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'recidron.db')
DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_PORT = os.getenv('DATABASE_PORT')


class CursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor
        
    def execute(self, query, args=None):
        self._cursor.execute(query, args)
        return self
        
    def fetchone(self):
        return self._cursor.fetchone()
        
    def fetchall(self):
        return self._cursor.fetchall()
        
    @property
    def lastrowid(self):
        return self._cursor.lastrowid

class MySQLConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn

    def close(self):
        self._conn.close()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def execute(self, query, args=None):
        cursor = self._conn.cursor()
        cursor.execute(query, args)
        return CursorWrapper(cursor)

    def cursor(self):
        return CursorWrapper(self._conn.cursor())


def get_connection():
    """
    Crea y retorna una conexión a la base de datos de MySQL.
    """
    conn = pymysql.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        port=int(DATABASE_PORT),
        db=DATABASE_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    return MySQLConnectionWrapper(conn)


def init_db():
    """
    Crea todas las tablas si no existen.
    Este es el equivalente al script DDL que pide el profe.
    Se ejecuta automáticamente al arrancar la API.
    """
    print("[ INFO ] Inicializando base de datos...")
    conn = get_connection()
    print("[ INFO ] Conectado a la base de datos.")
    cursor = conn.cursor()
    print("[ INFO ] Cursor creado.")
    # TABLAS DE SEGURIDAD INFORMÁTICA
    # Roles de usuario: Administrador, Invitado
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre_rol VARCHAR(50) NOT NULL UNIQUE
        );
    """)

    # Usuarios del sistema con autenticación por roles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre     VARCHAR(50)    NOT NULL,
            email      VARCHAR(100)    NOT NULL UNIQUE,
            password   VARCHAR(150)    NOT NULL,
            activo     INTEGER NOT NULL DEFAULT 1,
            rol_id     INTEGER NOT NULL,
            creado_en  DATETIME    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (rol_id) REFERENCES roles(id)
        );
    """)

    # Sesiones activas — control de acceso por token
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sesiones (
            id          INT PRIMARY KEY AUTO_INCREMENT,
            usuario_id  INT NOT NULL,
            token       VARCHAR(150)    NOT NULL UNIQUE,
            creado_en   DATETIME    DEFAULT CURRENT_TIMESTAMP,
            expira_en   DATETIME    NOT NULL,
            activa      INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
    """)

    # Auditoría — registro de acciones importantes del sistema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs_auditoria (
            id          INT PRIMARY KEY AUTO_INCREMENT,
            usuario_id  INT,
            accion      VARCHAR(200) NOT NULL,
            tabla       VARCHAR(200) NOT NULL,
            descripcion VARCHAR(1000),
            fecha       DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
    """)

    # TABLAS DEL PGC — Recidron App
    # Tipos de residuo: Aprovechable, No Aprovechable, Orgánico, Peligroso
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tipos_residuo (
            id          INTEGER PRIMARY KEY AUTO_INCREMENT,
            nombre_tipo VARCHAR(50) NOT NULL UNIQUE
        );
    """)

    # Material del residuo: Plástico, Icopor, Metal, Papel/Cartón, Vidrio
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiales (
            id              INTEGER PRIMARY KEY AUTO_INCREMENT,
            nombre_material VARCHAR(50) NOT NULL UNIQUE
        );
    """)

    # Zonas del campus universitario
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS zonas_campus (
            id          INTEGER PRIMARY KEY AUTO_INCREMENT,
            nombre_zona VARCHAR(50) NOT NULL UNIQUE
        );
    """)

    # Tamaño estimado del residuo: Pequeño, Mediano, Grande
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tamanos (
            id            INTEGER PRIMARY KEY AUTO_INCREMENT,
            nombre_tamano VARCHAR(50) NOT NULL UNIQUE
        );
    """)

    # Reportes de residuos — tabla principal del sistema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reportes (
            id              INTEGER PRIMARY KEY AUTO_INCREMENT,
            descripcion     VARCHAR(1000),
            fecha_reporte   DATETIME DEFAULT CURRENT_TIMESTAMP,
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
    """)

    # Coordenadas GPS de cada reporte
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS geolocalizaciones (
            id         INTEGER PRIMARY KEY AUTO_INCREMENT,
            latitud    FLOAT    NOT NULL,
            longitud   FLOAT    NOT NULL,
            altitud    FLOAT,
            precision_gps  FLOAT,
            reporte_id INTEGER NOT NULL UNIQUE,
            FOREIGN KEY (reporte_id) REFERENCES reportes(id)
        );
    """)

    print("[ INFO ] Tablas creadas exitosamente.")

    # SEED — Datos iniciales (solo inserta si la tabla está vacía)
    _seed(cursor, 'roles',        'nombre_rol',      ['Administrador', 'Invitado'])
    _seed(cursor, 'tipos_residuo','nombre_tipo',     ['Aprovechable', 'No Aprovechable', 'Orgánico', 'Peligroso'])
    _seed(cursor, 'materiales',   'nombre_material', ['Plástico', 'Icopor', 'Metal', 'Papel/Cartón', 'Vidrio'])
    _seed(cursor, 'zonas_campus', 'nombre_zona',     ['Entrada Principal', 'Bloque A', 'Bloque B', 'Canchas', 'Cafetería', 'Parqueadero'])
    _seed(cursor, 'tamanos',      'nombre_tamano',   ['Pequeño', 'Mediano', 'Grande'])

    print("[ INFO ] Datos iniciales insertados exitosamente.")

    conn.commit()
    conn.close()
    print('[ OK ] Base de datos lista.')


def _seed(cursor, tabla, campo, valores):
    """Inserta valores iniciales solo si la tabla está vacía."""
    cursor.execute(f"SELECT COUNT(*) AS count FROM {tabla}")
    if cursor.fetchone()['count'] == 0:
        for valor in valores:
            cursor.execute(f"INSERT INTO {tabla} ({campo}) VALUES (%s)", (valor,))