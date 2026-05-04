# Capa de Acceso a Datos — Repositorios
# Cada repositorio encapsula las consultas SQLAlchemy de una entidad.
# Los servicios consumen estos repositorios; las rutas NUNCA tocan la DB directamente.

from .repositorio_roles              import RepositorioRoles
from .repositorio_usuarios           import RepositorioUsuarios
from .repositorio_sesiones           import RepositorioSesiones
from .repositorio_logs               import RepositorioLogs
from .repositorio_tipos_residuo      import RepositorioTiposResiduo
from .repositorio_materiales         import RepositorioMateriales
from .repositorio_zonas_campus       import RepositorioZonasCampus
from .repositorio_tamanos            import RepositorioTamanos
from .repositorio_reportes           import RepositorioReportes
from .repositorio_geolocalizaciones  import RepositorioGeolocalizaciones
from .repositorio_estadisticas       import RepositorioEstadisticas
from .repositorio_fotos              import RepositorioFotos

__all__ = [
    "RepositorioRoles",
    "RepositorioUsuarios",
    "RepositorioSesiones",
    "RepositorioLogs",
    "RepositorioTiposResiduo",
    "RepositorioMateriales",
    "RepositorioZonasCampus",
    "RepositorioTamanos",
    "RepositorioReportes",
    "RepositorioGeolocalizaciones",
    "RepositorioEstadisticas",
    "RepositorioFotos",
]
