from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


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

