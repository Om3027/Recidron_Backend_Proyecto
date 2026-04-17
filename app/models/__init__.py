# El paquete models maneja la conexión y lógica de datos.
# Modularizado para facilitar la transición a SQLAlchemy en el futuro.

from .db import get_connection
from .setup import init_db
from .seguridad import *
from .pgc import *
from .reportes import *

# Exportamos las funciones principales para mantener compatibilidad
__all__ = ["get_connection", "init_db"]