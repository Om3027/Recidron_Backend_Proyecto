import os
from sqlalchemy.orm import Session
from utils.security import get_password_hash
from models.security import Role, Permission, User
from models.project import TipoResiduo, Material, ZonaCampus, Tamano

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
    if db.query(TipoResiduo).count() == 0:
        db.add_all([TipoResiduo(nombre_tipo=n) for n in ['Aprovechable', 'Orgánico', 'No Aprovechable', 'Peligroso']])
    if db.query(Material).count() == 0:
        db.add_all([Material(nombre_material=n) for n in ['Plástico', 'Vidrio', 'Cartón/Papel', 'Metal', 'Residuos Orgánicos', 'Restos de Comida']])
    if db.query(ZonaCampus).count() == 0:
        db.add_all([ZonaCampus(nombre_zona=n) for n in ['Biblioteca', 'Edificio A', 'Edificio B', 'Cafetería', 'Zona Deportiva', 'Parqueadero']])
    if db.query(Tamano).count() == 0:
        db.add_all([Tamano(nombre_tamano=n) for n in ['Leve', 'Mediano (2-5kg)', 'Crítico']])
    
    db.commit()
