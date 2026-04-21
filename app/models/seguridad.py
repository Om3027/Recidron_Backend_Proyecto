from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    nombre_rol = Column(String(50), nullable=False, unique=True)
    
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(150), nullable=False)
    activo = Column(Integer, nullable=False, default=1)
    rol_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    creado_en = Column(DateTime, default=func.now())
    
    role = relationship("Role", back_populates="users")
    sessions = relationship("Session", back_populates="user")
    logs = relationship("LogAuditoria", back_populates="user")
    reports = relationship("Reporte", back_populates="user")

class Session(Base):
    __tablename__ = 'sesiones'
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    token = Column(String(150), nullable=False, unique=True)
    creado_en = Column(DateTime, default=func.now())
    expira_en = Column(String(150), nullable=False)
    activa = Column(Integer, nullable=False, default=1)
    
    user = relationship("User", back_populates="sessions")

class LogAuditoria(Base):
    __tablename__ = 'logs_auditoria'
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    accion = Column(String(200), nullable=False)
    tabla = Column(String(200), nullable=False)
    descripcion = Column(String(1000))
    fecha = Column(DateTime, default=func.now())
    
    user = relationship("User", back_populates="logs")

