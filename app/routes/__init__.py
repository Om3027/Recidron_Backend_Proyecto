from .roles import router_roles
from .usuarios import router_usuarios
from .sesiones import router_sesiones
from .logs import router_logs
from .tipos_residuo import router_tipos
from .materiales import router_materiales
from .zonas_campus import router_zonas
from .tamanos import router_tamanos
from .reportes import router_reportes
from .geolocalizaciones import router_geos

__all__ = [
    "router_roles",
    "router_usuarios",
    "router_sesiones",
    "router_logs",
    "router_tipos",
    "router_materiales",
    "router_zonas",
    "router_tamanos",
    "router_reportes",
    "router_geos",
]