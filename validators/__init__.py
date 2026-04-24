
# Los VALIDADORES definen qué datos acepta cada ruta de la API.
# FastAPI los usa automáticamente para:
#   1. Validar los datos que llegan (si faltan campos → error 422 automático)
#   2. Documentar el Swagger (muestra qué campos acepta cada ruta)
#
# Usamos Pydantic — viene incluido con FastAPI, no necesitas instalarlo.
# Optional significa que el campo NO es obligatorio.


from pydantic import BaseModel
from typing import Optional


# SEGURIDAD INFORMÁTICA

class RolCreate(BaseModel):
    """Datos para crear o actualizar un Rol."""
    nombre_rol: str


class UsuarioCreate(BaseModel):
    """Datos para registrar un nuevo Usuario."""
    nombre:   str
    email:    str
    password: str
    codigo_estudiantil: Optional[str] = None
    rol_id:   Optional[int] = None

class UsuarioLogin(BaseModel):
    """Estructura de datos para validar el inicio de sesión."""
    email:    str
    password: str


class UsuarioUpdate(BaseModel):
    """Datos para actualizar un Usuario — todos opcionales."""
    nombre:   Optional[str] = None
    email:    Optional[str] = None
    password: Optional[str] = None
    codigo_estudiantil: Optional[str] = None
    rol_id:   Optional[int] = None


class PerfilUpdate(BaseModel):
    """
    Datos para que un usuario edite su propio perfil.
    - nombre, email y codigo_estudiantil son campos de identidad (opcionales).
    - nueva_password + confirmar_password: deben enviarse juntas y coincidir.
    - rol_id no está disponible: el usuario no puede cambiar su propio rol.
    """
    nombre:             Optional[str] = None
    email:              Optional[str] = None
    codigo_estudiantil: Optional[str] = None
    nueva_password:     Optional[str] = None
    confirmar_password: Optional[str] = None


class SesionCreate(BaseModel):
    """Datos para registrar una sesión activa."""
    usuario_id: int
    token:      str
    expira_en:  str


class LogCreate(BaseModel):
    """Datos para registrar una acción de auditoría."""
    usuario_id:  Optional[int] = None
    accion:      str
    tabla:       str
    descripcion: Optional[str] = None



# PGC — RECIDRON APP

class TipoResiduoCreate(BaseModel):
    """Datos para crear o actualizar un Tipo de Residuo."""
    nombre_tipo: str


class MaterialCreate(BaseModel):
    """Datos para crear o actualizar un Material."""
    nombre_material: str


class ZonaCampusCreate(BaseModel):
    """Datos para crear o actualizar una Zona del Campus."""
    nombre_zona: str


class TamanoCreate(BaseModel):
    """Datos para crear o actualizar un Tamaño."""
    nombre_tamano: str


class ReporteCreate(BaseModel):
    """Datos para registrar un nuevo Reporte de residuo."""
    descripcion:     Optional[str] = None
    usuario_id:      int
    tipo_residuo_id: int
    material_id:     int
    zona_id:         int
    tamano_id:       int


class ReporteUpdate(BaseModel):
    """Datos para actualizar un Reporte — todos opcionales."""
    descripcion:     Optional[str] = None
    tipo_residuo_id: Optional[int] = None
    material_id:     Optional[int] = None
    zona_id:         Optional[int] = None
    tamano_id:       Optional[int] = None


class GeoCreate(BaseModel):
    """Datos para registrar coordenadas GPS de un reporte."""
    latitud:    float
    longitud:   float
    altitud:    Optional[float] = None
    precision:  Optional[float] = None
    reporte_id: int


class GeoUpdate(BaseModel):
    """Datos para actualizar coordenadas GPS — todos opcionales."""
    latitud:   Optional[float] = None
    longitud:  Optional[float] = None
    altitud:   Optional[float] = None
    precision: Optional[float] = None