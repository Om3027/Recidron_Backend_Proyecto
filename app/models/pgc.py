from app.database import SessionLocal
from .sqlalchemy_models import TipoResiduo, Material, ZonaCampus, Tamano

def _get_db():
    return SessionLocal()

# --- TIPOS DE RESIDUO ---
def get_all_types():
    db = _get_db()
    try:
        tipos = db.query(TipoResiduo).order_by(TipoResiduo.id).all()
        return [{k: v for k, v in t.__dict__.items() if k != '_sa_instance_state'} for t in tipos]
    finally:
        db.close()

def get_type_by_id(type_id: int):
    db = _get_db()
    try:
        t = db.query(TipoResiduo).filter(TipoResiduo.id == type_id).first()
        if t:
            return {k: v for k, v in t.__dict__.items() if k != '_sa_instance_state'}
        return None
    finally:
        db.close()

def create_type(nombre_tipo: str):
    db = _get_db()
    try:
        nuevo = TipoResiduo(nombre_tipo=nombre_tipo)
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo.id
    finally:
        db.close()

def update_type(type_id: int, nombre_tipo: str):
    db = _get_db()
    try:
        db.query(TipoResiduo).filter(TipoResiduo.id == type_id).update({"nombre_tipo": nombre_tipo})
        db.commit()
    finally:
        db.close()

def delete_type(type_id: int):
    db = _get_db()
    try:
        db.query(TipoResiduo).filter(TipoResiduo.id == type_id).delete()
        db.commit()
    finally:
        db.close()


# --- MATERIALES ---
def get_all_materials():
    db = _get_db()
    try:
        mats = db.query(Material).order_by(Material.id).all()
        return [m.__dict__ for m in mats]
    finally:
        db.close()

def get_material_by_id(material_id: int):
    db = _get_db()
    try:
        m = db.query(Material).filter(Material.id == material_id).first()
        return m.__dict__ if m else None
    finally:
        db.close()

def create_material(nombre_material: str):
    db = _get_db()
    try:
        nuevo = Material(nombre_material=nombre_material)
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo.id
    finally:
        db.close()

def update_material(material_id: int, nombre_material: str):
    db = _get_db()
    try:
        db.query(Material).filter(Material.id == material_id).update({"nombre_material": nombre_material})
        db.commit()
    finally:
        db.close()

def delete_material(material_id: int):
    db = _get_db()
    try:
        db.query(Material).filter(Material.id == material_id).delete()
        db.commit()
    finally:
        db.close()


# --- ZONAS CAMPUS ---
def get_all_zones():
    db = _get_db()
    try:
        zonas = db.query(ZonaCampus).order_by(ZonaCampus.id).all()
        return [z.__dict__ for z in zonas]
    finally:
        db.close()

def get_zone_by_id(zone_id: int):
    db = _get_db()
    try:
        z = db.query(ZonaCampus).filter(ZonaCampus.id == zone_id).first()
        return z.__dict__ if z else None
    finally:
        db.close()

def create_zone(nombre_zona: str):
    db = _get_db()
    try:
        nuevo = ZonaCampus(nombre_zona=nombre_zona)
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo.id
    finally:
        db.close()

def update_zone(zone_id: int, nombre_zona: str):
    db = _get_db()
    try:
        db.query(ZonaCampus).filter(ZonaCampus.id == zone_id).update({"nombre_zona": nombre_zona})
        db.commit()
    finally:
        db.close()

def delete_zone(zone_id: int):
    db = _get_db()
    try:
        db.query(ZonaCampus).filter(ZonaCampus.id == zone_id).delete()
        db.commit()
    finally:
        db.close()


# --- TAMAÑOS ---
def get_all_sizes():
    db = _get_db()
    try:
        tamanos = db.query(Tamano).order_by(Tamano.id).all()
        return [t.__dict__ for t in tamanos]
    finally:
        db.close()

def get_size_by_id(size_id: int):
    db = _get_db()
    try:
        t = db.query(Tamano).filter(Tamano.id == size_id).first()
        return t.__dict__ if t else None
    finally:
        db.close()

def create_size(nombre_tamano: str):
    db = _get_db()
    try:
        nuevo = Tamano(nombre_tamano=nombre_tamano)
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo.id
    finally:
        db.close()

def update_size(size_id: int, nombre_tamano: str):
    db = _get_db()
    try:
        db.query(Tamano).filter(Tamano.id == size_id).update({"nombre_tamano": nombre_tamano})
        db.commit()
    finally:
        db.close()

def delete_size(size_id: int):
    db = _get_db()
    try:
        db.query(Tamano).filter(Tamano.id == size_id).delete()
        db.commit()
    finally:
        db.close()

