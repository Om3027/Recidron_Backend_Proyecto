from .db import get_connection

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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre_rol VARCHAR(50) NOT NULL UNIQUE
        );
    """)

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sesiones (
            id          INT PRIMARY KEY AUTO_INCREMENT,
            usuario_id  INT NOT NULL,
            token       VARCHAR(150)    NOT NULL UNIQUE,
            creado_en   VARCHAR(150)    DEFAULT CURRENT_TIMESTAMP,
            expira_en   VARCHAR(150)    NOT NULL,
            activa      INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
    """)

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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tipos_residuo (
            id          INTEGER PRIMARY KEY AUTO_INCREMENT,
            nombre_tipo VARCHAR(50) NOT NULL UNIQUE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiales (
            id              INTEGER PRIMARY KEY AUTO_INCREMENT,
            nombre_material VARCHAR(50) NOT NULL UNIQUE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS zonas_campus (
            id          INTEGER PRIMARY KEY AUTO_INCREMENT,
            nombre_zona VARCHAR(50) NOT NULL UNIQUE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tamanos (
            id            INTEGER PRIMARY KEY AUTO_INCREMENT,
            nombre_tamano VARCHAR(50) NOT NULL UNIQUE
        );
    """)

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

    # SEED — Datos iniciales
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
