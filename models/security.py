from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# Tabla intermedia para la relación muchos-a-muchos entre roles y permisos
role_permissions = Table(
    'rol_permisos',
    Base.metadata,
    Column('rol_id', Integer, ForeignKey('roles.id', ondelete="CASCADE"), primary_key=True),
    Column('permiso_id', Integer, ForeignKey('permisos.id', ondelete="CASCADE"), primary_key=True)
)

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_rol = Column(String(50), unique=True, nullable=False)

    # Relaciones
    usuarios = relationship("User", back_populates="rol")
    permisos = relationship("Permission", secondary=role_permissions, back_populates="roles")


class Permission(Base):
    __tablename__ = "permisos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_permiso = Column(String(100), unique=True, nullable=False)

    # Relaciones
    roles = relationship("Role", secondary=role_permissions, back_populates="permisos")


class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    codigo_estudiantil = Column(String(20), nullable=True)
    es_activo = Column(Boolean, nullable=False, default=True)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    creado_en = Column(DateTime, server_default=func.now())

    # Relaciones
    rol = relationship("Role", back_populates="usuarios")
    sesiones = relationship("Session", back_populates="usuario", cascade="all, delete-orphan")
    logs_auditoria = relationship("AuditLog", back_populates="usuario")


class Session(Base):
    __tablename__ = "sesiones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    creado_en = Column(DateTime, server_default=func.now())
    expira_en = Column(DateTime, nullable=False)
    activa = Column(Boolean, nullable=False, default=True)

    # Relaciones
    usuario = relationship("User", back_populates="sesiones")


class AuditLog(Base):
    __tablename__ = "logs_auditoria"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    accion = Column(String(100), nullable=False)
    recurso = Column(String(100), nullable=False)
    detalles = Column(Text, nullable=True)
    valor_anterior = Column(Text, nullable=True)
    valor_nuevo = Column(Text, nullable=True)
    fecha = Column(DateTime, server_default=func.now())

    # Relaciones
    usuario = relationship("User", back_populates="logs_auditoria")
