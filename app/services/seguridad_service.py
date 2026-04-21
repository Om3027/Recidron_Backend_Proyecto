from app.database import SessionLocal
from .base_service import BaseService
from app.models.seguridad import Role, User, Session as SessionModel, LogAuditoria

class RoleService(BaseService):
    def __init__(self):
        self.db = SessionLocal()
    
    def get_all(self):
        return self.db.query(Role).all()
    
    def get_by_id(self, id):
        return self.db.query(Role).filter(Role.id == id).first()
    
    def create(self, data):
        nuevo = Role(**data)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo
    
    def update(self, id, data):
        self.db.query(Role).filter(Role.id == id).update(data)
        self.db.commit()
    
    def delete(self, id):
        self.db.query(Role).filter(Role.id == id).delete()
        self.db.commit()

class UserService(BaseService):
    def __init__(self):
        self.db = SessionLocal()
    
    def get_all(self):
        return self.db.query(User).all()
    
    def get_by_id(self, id):
        return self.db.query(User).filter(User.id == id).first()
    
    def create(self, data):
        nuevo = User(**data)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo
    
    def update(self, id, data):
        self.db.query(User).filter(User.id == id).update(data)
        self.db.commit()
    
    def deactivate(self, id):
        self.db.query(User).filter(User.id == id).update({"activo": 0})
        self.db.commit()

    def delete(self, id):
        # Usualmente no se borran usuarios, se desactivan, pero implementamos para completar el BaseService
        self.db.query(User).filter(User.id == id).delete()
        self.db.commit()

class SessionService(BaseService):
    def __init__(self):
        self.db = SessionLocal()
    
    def get_all(self):
        return self.db.query(SessionModel).all()
    
    def get_by_id(self, id):
        return self.db.query(SessionModel).filter(SessionModel.id == id).first()
    
    def create(self, data):
        nuevo = SessionModel(**data)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo
    
    def update(self, id, data):
        self.db.query(SessionModel).filter(SessionModel.id == id).update(data)
        self.db.commit()
    
    def delete(self, id):
        self.db.query(SessionModel).filter(SessionModel.id == id).delete()
        self.db.commit()

class LogAuditoriaService(BaseService):
    def __init__(self):
        self.db = SessionLocal()
    
    def get_all(self):
        return self.db.query(LogAuditoria).order_by(LogAuditoria.fecha.desc()).all()
    
    def get_by_id(self, id):
        return self.db.query(LogAuditoria).filter(LogAuditoria.id == id).first()
    
    def create(self, data):
        nuevo = LogAuditoria(**data)
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo
    
    def update(self, id, data):
        self.db.query(LogAuditoria).filter(LogAuditoria.id == id).update(data)
        self.db.commit()
    
    def delete(self, id):
        self.db.query(LogAuditoria).filter(LogAuditoria.id == id).delete()
        self.db.commit()
