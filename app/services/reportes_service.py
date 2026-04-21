from app.database import SessionLocal
from .base_services import BaseService
from app.models.sqlalchemy_models import Reporte, Geolocalizacion

class ReporteService(BaseService):
    def __init__(self):
        self.db = SessionLocal()
    
    def get_all(self):
        return self.db.query(Reporte).order_by(Reporte.fecha_reporte.desc()).all()
    
    def get_by_id(self, id):
        return self.db.query(Reporte).filter(Reporte.id == id).first()
    
    def create(self, data):
        nuevo = Reporte(**data)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo
    
    def update(self, id, data):
        self.db.query(Reporte).filter(Reporte.id == id).update(data)
        self.db.commit()
    
    def delete(self, id):
        self.db.query(Reporte).filter(Reporte.id == id).delete()
        self.db.commit()

class GeolocalizacionService(BaseService):
    def __init__(self):
        self.db = SessionLocal()
    
    def get_all(self):
        return self.db.query(Geolocalizacion).all()
    
    def get_by_id(self, id):
        return self.db.query(Geolocalizacion).filter(Geolocalizacion.id == id).first()
    
    def create(self, data):
        nuevo = Geolocalizacion(**data)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo
    
    def update(self, id, data):
        self.db.query(Geolocalizacion).filter(Geolocalizacion.id == id).update(data)
        self.db.commit()
    
    def delete(self, id):
        self.db.query(Geolocalizacion).filter(Geolocalizacion.id == id).delete()
        self.db.commit()
