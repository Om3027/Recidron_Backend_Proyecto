from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from models import get_db
from servicios import ServicioAutenticacion
from repositorios import RepositorioUsuarios

# ── Esquema de seguridad Bearer para Swagger UI y OpenAPI ───────────────────────
# auto_error=False permite que las rutas públicas u opcionales no lancen error automáticamente
bearer_scheme = HTTPBearer(auto_error=False)


# ── Dependencias de autenticación reutilizables en todas las rutas ─────────────

def obtener_usuario_actual(
    auth: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict:
    """Extrae y valida el token del header Authorization (vía Swagger o Frontend)."""
    if not auth:
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    return ServicioAutenticacion(db).obtener_usuario_actual(auth.credentials)


def obtener_usuario_opcional(
    auth: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict | None:
    """Intenta obtener el usuario; retorna None si no hay token válido."""
    if not auth:
        return None
    try:
        return ServicioAutenticacion(db).obtener_usuario_actual(auth.credentials)
    except HTTPException:
        return None


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


def verificar_super_admin(
    usuario: dict = Depends(obtener_usuario_actual),
) -> dict:
    """
    Verifica que el usuario actual tenga rol de administrador y sea el
    Super Administrador oficial (admin@recidron.com).
    """
    import os
    admin_email = os.getenv("ADMIN_EMAIL", "admin@recidron.com").strip().lower()
    user_email = (usuario.get("email") or "").strip().lower()
    rol_nombre = (usuario.get("nombre_rol") or "").strip().lower()
    rol_id = usuario.get("rol_id")

    es_admin = rol_nombre == "admin" or rol_id == 1
    if not (es_admin and user_email == admin_email):
        raise HTTPException(
            status_code=403,
            detail="Acceso restringido: Se requieren permisos de Administrador Maestro para esta acción",
        )
    return usuario


# ── Alias de compatibilidad (mantienen los nombres originales) ─────────────────
# Permiten que las rutas que no se han migrado aún sigan funcionando sin cambios.

def get_current_user(
    auth: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict:
    return obtener_usuario_actual(auth, db)


def get_optional_user(
    auth: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict | None:
    return obtener_usuario_opcional(auth, db)


def check_permission(permission_required: str):
    return verificar_permiso(permission_required)
