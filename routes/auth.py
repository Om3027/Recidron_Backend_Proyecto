from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from models import get_db
from servicios import ServicioAutenticacion
from repositorios import RepositorioUsuarios


# ── Dependencias de autenticación reutilizables en todas las rutas ─────────────

def obtener_usuario_actual(authorization: str = Header(None), db: Session = Depends(get_db)) -> dict:
    """Extrae y valida el token del header Authorization."""
    return ServicioAutenticacion(db).obtener_usuario_actual(authorization)


def obtener_usuario_opcional(authorization: str = Header(None), db: Session = Depends(get_db)) -> dict | None:
    """Intenta obtener el usuario; retorna None si no hay token válido."""
    return ServicioAutenticacion(db).obtener_usuario_opcional(authorization)


def verificar_permiso(permiso_requerido: str):
    """
    Fábrica de dependencias que verifica un permiso específico del usuario.
    Uso: Depends(verificar_permiso("reportes:crear"))
    """
    def verificador(
        usuario: dict = Depends(obtener_usuario_actual),
        db: Session = Depends(get_db),
    ) -> dict:
        repositorio = RepositorioUsuarios(db)
        if not repositorio.rol_tiene_permiso(usuario["rol_id"], permiso_requerido):
            raise HTTPException(
                status_code=403,
                detail=f"No tienes permiso para realizar esta acción ({permiso_requerido})",
            )
        return usuario

    return verificador


# ── Alias de compatibilidad (mantienen los nombres originales) ─────────────────
# Permiten que las rutas que no se han migrado aún sigan funcionando sin cambios.

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> dict:
    return obtener_usuario_actual(authorization, db)

def get_optional_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> dict | None:
    return obtener_usuario_opcional(authorization, db)

def check_permission(permission_required: str):
    return verificar_permiso(permission_required)
