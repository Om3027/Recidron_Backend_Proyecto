from app.database import SessionLocal
from .sqlalchemy_models import Reporte, Geolocalizacion

def _get_db():
    return SessionLocal()

# --- REPORTES ---
def get_all_reports():
    db = _get_db()
    try:
        reportes = db.query(Reporte).order_by(Reporte.fecha_reporte.desc()).all()
        return [r.__dict__ for r in reportes]
    finally:
        db.close()

def get_report_by_id(report_id: int):
    db = _get_db()
    try:
        r = db.query(Reporte).filter(Reporte.id == report_id).first()
        return r.__dict__ if r else None
    finally:
        db.close()

def create_report(descripcion, usuario_id, tipo_residuo_id, material_id, zona_id, tamano_id):
    db = _get_db()
    try:
        nuevo = Reporte(
            descripcion=descripcion,
            usuario_id=usuario_id,
            tipo_residuo_id=tipo_residuo_id,
            material_id=material_id,
            zona_id=zona_id,
            tamano_id=tamano_id
        )
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo.id
    finally:
        db.close()

def update_report(report_id: int, campos: dict):
    db = _get_db()
    try:
        db.query(Reporte).filter(Reporte.id == report_id).update(campos)
        db.commit()
    finally:
        db.close()

def delete_report(report_id: int):
    db = _get_db()
    try:
        db.query(Reporte).filter(Reporte.id == report_id).delete()
        db.commit()
    finally:
        db.close()


# --- GEOLOCALIZACIONES ---
def get_all_geos():
    db = _get_db()
    try:
        geos = db.query(Geolocalizacion).order_by(Geolocalizacion.id).all()
        return [g.__dict__ for g in geos]
    finally:
        db.close()

def get_geo_by_id(geo_id: int):
    db = _get_db()
    try:
        g = db.query(Geolocalizacion).filter(Geolocalizacion.id == geo_id).first()
        return g.__dict__ if g else None
    finally:
        db.close()

def create_geo(latitud, longitud, altitud, precision_gps, reporte_id):
    db = _get_db()
    try:
        nueva_geo = Geolocalizacion(
            latitud=latitud,
            longitud=longitud,
            altitud=altitud,
            precision_gps=precision_gps,
            reporte_id=reporte_id
        )
        db.add(nueva_geo)
        db.commit()
        db.refresh(nueva_geo)
        return nueva_geo.id
    finally:
        db.close()

def update_geo(geo_id: int, campos: dict):
    db = _get_db()
    try:
        db.query(Geolocalizacion).filter(Geolocalizacion.id == geo_id).update(campos)
        db.commit()
    finally:
        db.close()

def delete_geo(geo_id: int):
    db = _get_db()
    try:
        db.query(Geolocalizacion).filter(Geolocalizacion.id == geo_id).delete()
        db.commit()
    finally:
        db.close()

