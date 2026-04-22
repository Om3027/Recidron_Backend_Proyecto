def create_project_tables(cursor):
    """
    Crea las tablas del proyecto (Recidron App).
    """
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
