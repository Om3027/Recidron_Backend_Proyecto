from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class TipoResiduo(Base):
    __tablename__ = "tipos_residuo"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_tipo = Column(String(100), unique=True, nullable=False)
    es_activo = Column(Boolean, nullable=False, default=True)

    reportes = relationship("Reporte", back_populates="tipo_residuo")


class Material(Base):
    __tablename__ = "materiales"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_material = Column(String(100), unique=True, nullable=False)
    es_activo = Column(Boolean, nullable=False, default=True)

    reportes = relationship("Reporte", back_populates="material")


class ZonaCampus(Base):
    __tablename__ = "zonas_campus"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_zona = Column(String(100), unique=True, nullable=False)
    es_activo = Column(Boolean, nullable=False, default=True)

    reportes = relationship("Reporte", back_populates="zona")


class Tamano(Base):
    __tablename__ = "tamanos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_tamano = Column(String(100), unique=True, nullable=False)
    es_activo = Column(Boolean, nullable=False, default=True)

    reportes = relationship("Reporte", back_populates="tamano")


class Reporte(Base):
    __tablename__ = "reportes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    descripcion = Column(Text, nullable=True)
    fecha_reporte = Column(DateTime, server_default=func.now())
    es_activo = Column(Boolean, nullable=False, default=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo_residuo_id = Column(Integer, ForeignKey("tipos_residuo.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materiales.id"), nullable=False)
    zona_id = Column(Integer, ForeignKey("zonas_campus.id"), nullable=False)
    tamano_id = Column(Integer, ForeignKey("tamanos.id"), nullable=False)

    # Relaciones
    usuario = relationship("User", back_populates="reportes")
    tipo_residuo = relationship("TipoResiduo", back_populates="reportes")
    material = relationship("Material", back_populates="reportes")
    zona = relationship("ZonaCampus", back_populates="reportes")
    tamano = relationship("Tamano", back_populates="reportes")
    geolocalizacion = relationship("Geolocalizacion", back_populates="reporte", uselist=False, cascade="all, delete-orphan")
    foto = relationship("FotoReporte", back_populates="reporte", uselist=False, cascade="all, delete-orphan")


class Geolocalizacion(Base):
    __tablename__ = "geolocalizaciones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    latitud = Column(DECIMAL(10, 8), nullable=False)
    longitud = Column(DECIMAL(11, 8), nullable=False)
    altitud = Column(DECIMAL(10, 2), nullable=True)
    precision = Column(DECIMAL(10, 2), nullable=True)
    reporte_id = Column(Integer, ForeignKey("reportes.id", ondelete="CASCADE"), unique=True, nullable=False)

    reporte = relationship("Reporte", back_populates="geolocalizacion")


class FotoReporte(Base):
    __tablename__ = "fotos_reporte"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(Text, nullable=False)
    fecha_subida = Column(DateTime, server_default=func.now())
    reporte_id = Column(Integer, ForeignKey("reportes.id", ondelete="CASCADE"), unique=True, nullable=False)

    reporte = relationship("Reporte", back_populates="foto")
