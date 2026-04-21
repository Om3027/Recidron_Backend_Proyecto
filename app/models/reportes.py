from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

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
