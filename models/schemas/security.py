def create_security_tables(cursor):
    """
    Crea las tablas de seguridad (RBAC Avanzado).
    """
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
