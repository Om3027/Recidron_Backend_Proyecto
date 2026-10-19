import os
from sqlalchemy.orm import Session
from utils.security import get_password_hash
from models.security import Role, Permission, User
from models.project import TipoResiduo, Material, ZonaCampus, Tamano, TipoSubzona, SubzonaCampus

def _seed_roles(db: Session):
    if db.query(Role).count() == 0:
        db.add_all([Role(nombre_rol='admin'), Role(nombre_rol='autor')])
        db.commit()

def _seed_permisos(db: Session):
    if db.query(Permission).count() == 0:
        permisos_nombres = [
            'usuarios:leer', 'usuarios:crear', 'usuarios:editar', 'usuarios:eliminar',
            'reportes:leer', 'reportes:crear', 'reportes:editar', 'reportes:eliminar',
            'audit:leer', 'catalogos:gestionar'
        ]
        db.add_all([Permission(nombre_permiso=p) for p in permisos_nombres])
        db.commit()

def _sync_permisos_roles(db: Session):
    """Garantiza que el Admin tenga todo y el Autor tenga lo básico."""
    admin_rol = db.query(Role).filter_by(nombre_rol='admin').first()
    autor_rol = db.query(Role).filter_by(nombre_rol='autor').first()
    todos_permisos = db.query(Permission).all()
    
    if admin_rol:
        for p in todos_permisos:
            if p not in admin_rol.permisos:
                admin_rol.permisos.append(p)
                
    if autor_rol:
        nombres_autor = ['reportes:leer', 'reportes:crear', 'usuarios:leer']
        for p in todos_permisos:
            if p.nombre_permiso in nombres_autor and p not in autor_rol.permisos:
                autor_rol.permisos.append(p)
                
    db.commit()
    print("[ OK ] Permisos de roles sincronizados automáticamente.")

def _seed_admin_maestro(db: Session):
    """Crea el usuario administrador maestro si no existe."""
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_name  = os.getenv('ADMIN_NAME', 'Admin Root')
    admin_pass  = os.getenv('ADMIN_PASSWORD')
    
    if not admin_email or not admin_pass:
        return

    if not db.query(User).filter_by(email=admin_email).first():
        admin_rol = db.query(Role).filter_by(nombre_rol='admin').first()
        hashed_pass = get_password_hash(admin_pass)
        nuevo_admin = User(
            nombre=admin_name,
            email=admin_email,
            password=hashed_pass,
            rol_id=admin_rol.id if admin_rol else 1
        )
        db.add(nuevo_admin)
        db.commit()
        print(f"[ SEED ] Administrador Maestro creado: {admin_email}")

def run_seeders(db: Session):
    """Ejecuta los seeders para poblar datos iniciales."""
    _seed_roles(db)
    _seed_permisos(db)
    _sync_permisos_roles(db)
    _seed_admin_maestro(db)
    
    # Modelos del proyecto
    # Limpiar 'Especial' si se coló en la base de datos
    db.query(TipoResiduo).filter_by(nombre_tipo='Especial').delete()
    
    # Tipos de Residuo
    tipos_esperados = ['Aprovechable', 'Orgánico', 'No Aprovechable', 'Peligroso', 'Otro']
    for t in tipos_esperados:
        if not db.query(TipoResiduo).filter_by(nombre_tipo=t).first():
            db.add(TipoResiduo(nombre_tipo=t))

    # Materiales
    materiales_esperados = [
        'Plástico', 'Vidrio', 'Cartón/Papel', 'Latas/Metal', 
        'Residuos Tecnológicos', 'Desechos Médicos', 'Residuos Orgánicos', 
        'Restos de Comida', 'Icopor', 'Textiles', 'Escombros', 'Otro'
    ]
    for m in materiales_esperados:
        if not db.query(Material).filter_by(nombre_material=m).first():
            db.add(Material(nombre_material=m))

    # Zonas
    if db.query(ZonaCampus).count() == 0:
        db.add_all([ZonaCampus(nombre_zona=n) for n in ['Biblioteca', 'Edificio A', 'Edificio B', 'Cafetería', 'Zona Deportiva', 'Parqueadero']])
    
    # Tamaños
    if db.query(Tamano).count() == 0:
        db.add_all([Tamano(nombre_tamano=n) for n in ['Leve', 'Mediano (2-5kg)', 'Crítico']])
    
    db.commit()

    # Subzonas y Tipos de Subzona
    _seed_subzonas(db)


def _seed_tipos_subzona(db: Session):
    tipos = ['Aula', 'Oficina', 'Baño', 'Laboratorio', 'Área Común', 'Servicio']
    for t in tipos:
        if not db.query(TipoSubzona).filter_by(nombre_tipo=t).first():
            db.add(TipoSubzona(nombre_tipo=t))
    db.commit()


def _seed_subzonas(db: Session):
    _seed_tipos_subzona(db)

    tipos_dict = {t.nombre_tipo: t.id for t in db.query(TipoSubzona).all()}

    zona_academico = db.query(ZonaCampus).filter(ZonaCampus.nombre_zona.ilike('%Academico%')).first()
    zona_admin = db.query(ZonaCampus).filter(ZonaCampus.nombre_zona.ilike('%Administrativo%')).first()
    zona_enfermeria = db.query(ZonaCampus).filter(ZonaCampus.nombre_zona.ilike('%Enfermeria%')).first()
    zona_ambiental = db.query(ZonaCampus).filter(ZonaCampus.nombre_zona.ilike('%Ambiental%')).first()
    zona_admisiones = db.query(ZonaCampus).filter(ZonaCampus.nombre_zona.ilike('%Admisiones%')).first()

    subzonas_a_crear = []

    # 1. Edificio Académico
    if zona_academico:
        # Aulas Piso 1: 101 - 118
        for num in range(101, 119):
            subzonas_a_crear.append({
                'zona_id': zona_academico.id,
                'nombre_subzona': f'Aula {num}',
                'tipo_subzona_id': tipos_dict['Aula'],
                'piso': '1'
            })
        # Aulas Piso 2: 201 - 220
        for num in range(201, 221):
            subzonas_a_crear.append({
                'zona_id': zona_academico.id,
                'nombre_subzona': f'Aula {num}',
                'tipo_subzona_id': tipos_dict['Aula'],
                'piso': '2'
            })
        # Aulas Piso 3: 301 - 320
        for num in range(301, 321):
            subzonas_a_crear.append({
                'zona_id': zona_academico.id,
                'nombre_subzona': f'Aula {num}',
                'tipo_subzona_id': tipos_dict['Aula'],
                'piso': '3'
            })
        # Baños por piso (Hombre y Mujer)
        for p in ['1', '2', '3']:
            subzonas_a_crear.append({
                'zona_id': zona_academico.id,
                'nombre_subzona': f'Baño Hombres - Piso {p}',
                'tipo_subzona_id': tipos_dict['Baño'],
                'piso': p
            })
            subzonas_a_crear.append({
                'zona_id': zona_academico.id,
                'nombre_subzona': f'Baño Mujeres - Piso {p}',
                'tipo_subzona_id': tipos_dict['Baño'],
                'piso': p
            })
        # Zona Común El Ajedrez
        subzonas_a_crear.append({
            'zona_id': zona_academico.id,
            'nombre_subzona': 'Zona Común El Ajedrez',
            'tipo_subzona_id': tipos_dict['Área Común'],
            'piso': 'Exterior'
        })

    # 2. Edificio Administrativo
    if zona_admin:
        subzonas_a_crear.extend([
            {'zona_id': zona_admin.id, 'nombre_subzona': 'Oficina de Bienestar Universitario', 'tipo_subzona_id': tipos_dict['Oficina'], 'piso': '1'},
            {'zona_id': zona_admin.id, 'nombre_subzona': 'Coordinación de Ingeniería de Software', 'tipo_subzona_id': tipos_dict['Oficina'], 'piso': '2'},
            {'zona_id': zona_admin.id, 'nombre_subzona': 'Coordinación de Ingeniería Ambiental', 'tipo_subzona_id': tipos_dict['Oficina'], 'piso': '2'},
            {'zona_id': zona_admin.id, 'nombre_subzona': 'Coordinación de Administración de Empresas', 'tipo_subzona_id': tipos_dict['Oficina'], 'piso': '2'},
            {'zona_id': zona_admin.id, 'nombre_subzona': 'Coordinación de Enfermería', 'tipo_subzona_id': tipos_dict['Oficina'], 'piso': '2'},
            {'zona_id': zona_admin.id, 'nombre_subzona': 'Aula A201', 'tipo_subzona_id': tipos_dict['Aula'], 'piso': '2'},
            {'zona_id': zona_admin.id, 'nombre_subzona': 'Sala de Conferencias', 'tipo_subzona_id': tipos_dict['Área Común'], 'piso': '2'},
            {'zona_id': zona_admin.id, 'nombre_subzona': 'Oficinas de Administración de Sede', 'tipo_subzona_id': tipos_dict['Oficina'], 'piso': '3'},
        ])

    # 3. Bloque de Enfermería
    if zona_enfermeria:
        subzonas_a_crear.extend([
            {'zona_id': zona_enfermeria.id, 'nombre_subzona': 'Unidad Amiga', 'tipo_subzona_id': tipos_dict['Oficina'], 'piso': '1'},
            {'zona_id': zona_enfermeria.id, 'nombre_subzona': 'Laboratorio de Enfermería - Piso 1', 'tipo_subzona_id': tipos_dict['Laboratorio'], 'piso': '1'},
            {'zona_id': zona_enfermeria.id, 'nombre_subzona': 'Baños - Piso 1', 'tipo_subzona_id': tipos_dict['Baño'], 'piso': '1'},
            {'zona_id': zona_enfermeria.id, 'nombre_subzona': 'Laboratorio de Enfermería - Piso 2', 'tipo_subzona_id': tipos_dict['Laboratorio'], 'piso': '2'},
            {'zona_id': zona_enfermeria.id, 'nombre_subzona': 'Baños - Piso 2', 'tipo_subzona_id': tipos_dict['Baño'], 'piso': '2'},
            {'zona_id': zona_enfermeria.id, 'nombre_subzona': 'Hall de Área Común', 'tipo_subzona_id': tipos_dict['Área Común'], 'piso': 'General'},
            {'zona_id': zona_enfermeria.id, 'nombre_subzona': 'Ala de Enfermería', 'tipo_subzona_id': tipos_dict['Área Común'], 'piso': 'General'},
        ])

    # 4. Bloque de Ingeniería Ambiental
    if zona_ambiental:
        for p in ['1', '2', '3']:
            subzonas_a_crear.extend([
                {'zona_id': zona_ambiental.id, 'nombre_subzona': f'Laboratorio Ambiental - Piso {p}', 'tipo_subzona_id': tipos_dict['Laboratorio'], 'piso': p},
                {'zona_id': zona_ambiental.id, 'nombre_subzona': f'Aulas Ambientales - Piso {p}', 'tipo_subzona_id': tipos_dict['Aula'], 'piso': p},
                {'zona_id': zona_ambiental.id, 'nombre_subzona': f'Baños - Piso {p}', 'tipo_subzona_id': tipos_dict['Baño'], 'piso': p},
            ])

    # 5. Área Común de Admisiones
    if zona_admisiones:
        subzonas_a_crear.extend([
            {'zona_id': zona_admisiones.id, 'nombre_subzona': 'Papelería', 'tipo_subzona_id': tipos_dict['Servicio'], 'piso': 'PB'},
            {'zona_id': zona_admisiones.id, 'nombre_subzona': 'Oficina de Admisiones y Registro', 'tipo_subzona_id': tipos_dict['Oficina'], 'piso': 'PB'},
            {'zona_id': zona_admisiones.id, 'nombre_subzona': 'Zona Libre (Bancas al frente de la papelería)', 'tipo_subzona_id': tipos_dict['Área Común'], 'piso': 'PB'},
        ])

    # Cargar subzonas existentes en un set para inserción ultra rápida en 1 query
    subzonas_existentes = {
        (s.zona_id, s.nombre_subzona)
        for s in db.query(SubzonaCampus.zona_id, SubzonaCampus.nombre_subzona).all()
    }

    nuevas = [
        SubzonaCampus(**item)
        for item in subzonas_a_crear
        if (item['zona_id'], item['nombre_subzona']) not in subzonas_existentes
    ]

    if nuevas:
        db.bulk_save_objects(nuevas)
        db.commit()

    print(f"[ SEED ] Subzonas del campus sincronizadas ({len(nuevas)} creadas, {len(subzonas_a_crear)} totales).", flush=True)
