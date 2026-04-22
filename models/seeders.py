import os
from utils.security import get_password_hash

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

def run_seeders(cursor):
    """Ejecuta los seeders para poblar datos iniciales."""
    _seed_roles(cursor)
    _seed_permisos(cursor)
    _seed_list(cursor, 'tipos_residuo', 'nombre_tipo',     ['Aprovechable', 'Orgánico', 'No Aprovechable', 'Peligroso'])
    _seed_list(cursor, 'materiales',   'nombre_material', ['Plástico', 'Vidrio', 'Cartón/Papel', 'Metal', 'Residuos Orgánicos', 'Restos de Comida'])
    _seed_list(cursor, 'zonas_campus', 'nombre_zona',     ['Biblioteca', 'Edificio A', 'Edificio B', 'Cafetería', 'Zona Deportiva', 'Parqueadero'])
    _seed_list(cursor, 'tamanos',      'nombre_tamano',   ['Leve', 'Mediano (2-5kg)', 'Crítico'])
    _seed_admin_maestro(cursor)
    _sync_permisos_roles(cursor)
