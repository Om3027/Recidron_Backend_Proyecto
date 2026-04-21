from app.database import SessionLocal
from .base_service import BaseService
from app.models.pgc import TipoResiduo, Material, ZonaCampus, Tamano

class TipoResiduoService(BaseService):
    def __init__(self):
        self.db = SessionLocal()
    
    def get_all(self):
        return self.db.query(TipoResiduo).all()
    
    def get_by_id(self, id):
        return self.db.query(TipoResiduo).filter(TipoResiduo.id == id).first()
    
    def create(self, data):
        nuevo = TipoResiduo(**data)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo
    
    def update(self, id, data):
        self.db.query(TipoResiduo).filter(TipoResiduo.id == id).update(data)
        self.db.commit()
    
    def delete(self, id):
        self.db.query(TipoResiduo).filter(TipoResiduo.id == id).delete()
        self.db.commit()

class MaterialService(BaseService):
    def __init__(self):
        self.db = SessionLocal()
    
    def get_all(self):
        return self.db.query(Material).all()
    
    def get_by_id(self, id):
        return self.db.query(Material).filter(Material.id == id).first()
    
    def create(self, data):
        nuevo = Material(**data)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo
    
    def update(self, id, data):
        self.db.query(Material).filter(Material.id == id).update(data)
        self.db.commit()
    
    def delete(self, id):
        self.db.query(Material).filter(Material.id == id).delete()
        self.db.commit()

class ZonaCampusService(BaseService):
    def __init__(self):
        self.db = SessionLocal()
    
    def get_all(self):
        return self.db.query(ZonaCampus).all()
    
    def get_by_id(self, id):
        return self.db.query(ZonaCampus).filter(ZonaCampus.id == id).first()
    
    def create(self, data):
        nuevo = ZonaCampus(**data)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo
    
    def update(self, id, data):
        self.db.query(ZonaCampus).filter(ZonaCampus.id == id).update(data)
        self.db.commit()
    
    def delete(self, id):
        self.db.query(ZonaCampus).filter(ZonaCampus.id == id).delete()
        self.db.commit()

class TamanoService(BaseService):
    def __init__(self):
        self.db = SessionLocal()
    
    def get_all(self):
        return self.db.query(Tamano).all()
    
    def get_by_id(self, id):
        return self.db.query(Tamano).filter(Tamano.id == id).first()
    
    def create(self, data):
        nuevo = Tamano(**data)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo
    
    def update(self, id, data):
        self.db.query(Tamano).filter(Tamano.id == id).update(data)
        self.db.commit()
    
    def delete(self, id):
        self.db.query(Tamano).filter(Tamano.id == id).delete()
        self.db.commit()

