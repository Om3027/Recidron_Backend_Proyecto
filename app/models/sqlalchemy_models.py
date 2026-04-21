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

class TipoResiduo(Base):
    __tablename__ = 'tipos_residuo'
    id = Column(Integer, primary_key=True, index=True)
    nombre_tipo = Column(String(50), nullable=False, unique=True)
    
    reports = relationship("Reporte", back_populates="tipo_residuo")

class Material(Base):
    __tablename__ = 'materiales'
    id = Column(Integer, primary_key=True, index=True)
    nombre_material = Column(String(50), nullable=False, unique=True)
    
    reports = relationship("Reporte", back_populates="material")

class ZonaCampus(Base):
    __tablename__ = 'zonas_campus'
    id = Column(Integer, primary_key=True, index=True)
    nombre_zona = Column(String(50), nullable=False, unique=True)
    
    reports = relationship("Reporte", back_populates="zona")

class Tamano(Base):
    __tablename__ = 'tamanos'
    id = Column(Integer, primary_key=True, index=True)
    nombre_tamano = Column(String(50), nullable=False, unique=True)
    
    reports = relationship("Reporte", back_populates="tamano")

class Reporte(Base):
    __tablename__ = 'reportes'
    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(1000))
    fecha_reporte = Column(DateTime, default=func.now())
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    tipo_residuo_id = Column(Integer, ForeignKey('tipos_residuo.id'), nullable=False)
    material_id = Column(Integer, ForeignKey('materiales.id'), nullable=False)
    zona_id = Column(Integer, ForeignKey('zonas_campus.id'), nullable=False)
    tamano_id = Column(Integer, ForeignKey('tamanos.id'), nullable=False)
    
    user = relationship("User", back_populates="reports")
    tipo_residuo = relationship("TipoResiduo", back_populates="reports")
    material = relationship("Material", back_populates="reports")
    zona = relationship("ZonaCampus", back_populates="reports")
    tamano = relationship("Tamano", back_populates="reports")
    geolocalizacion = relationship("Geolocalizacion", back_populates="reporte", uselist=False)

class Geolocalizacion(Base):
    __tablename__ = 'geolocalizaciones'
    id = Column(Integer, primary_key=True, index=True)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    altitud = Column(Float)
    precision_gps = Column(Float)
    reporte_id = Column(Integer, ForeignKey('reportes.id'), nullable=False, unique=True)
    
    reporte = relationship("Reporte", back_populates="geolocalizacion")
