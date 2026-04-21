from models import get_connection

def debug_and_patch():
    print("--- DIAGNÓSTICO DE PERMISOS ---")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Ver roles existentes
    cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()
    print(f"Roles encontrados: {roles}")
    
    autor_id = next((r['id'] for r in roles if r['nombre_rol'] == 'autor'), None)
    if not autor_id:
        print("ERROR: No se encontró el rol 'autor'.")
        return

    # 2. Ver permisos existentes
    cursor.execute("SELECT * FROM permisos")
    permisos_db = cursor.fetchall()
    print(f"Permisos en DB: {[p['nombre_permiso'] for p in permisos_db]}")

    # 3. Aplicar Parche
    permisos_a_dar = ['reportes:leer', 'reportes:crear', 'usuarios:leer']
    p_ids = [p['id'] for p in permisos_db if p['nombre_permiso'] in permisos_a_dar]
    
    print(f"Asignando IDs de permiso {p_ids} al rol {autor_id}...")
    
    for p_id in p_ids:
        try:
            cursor.execute("INSERT INTO rol_permisos (rol_id, permiso_id) VALUES (%s, %s)", (autor_id, p_id))
            print(f"[ OK ] Permiso {p_id} asignado.")
        except:
            print(f"[ SKIP ] El permiso {p_id} ya lo tenía o hubo un error.")
            
    conn.commit()
    
    # 4. Verificación Final
    cursor.execute("""
        SELECT p.nombre_permiso 
        FROM rol_permisos rp
        JOIN permisos p ON rp.permiso_id = p.id
        WHERE rp.rol_id = %s
    """, (autor_id,))
    finales = [row['nombre_permiso'] for row in cursor.fetchall()]
    print(f"PERMISOS FINALES DEL ROL AUTOR: {finales}")
    
    cursor.close()
    conn.close()
    print("--- FIN DEL PROCESO ---")

if __name__ == "__main__":
    debug_and_patch()
