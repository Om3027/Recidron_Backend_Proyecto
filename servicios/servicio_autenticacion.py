from fastapi import HTTPException
from sqlalchemy.orm import Session
from repositorios import RepositorioSesiones


class ServicioAutenticacion:
    """
    Capa de negocio para autenticación.
    Valida tokens y permisos usando el repositorio de sesiones.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repositorio_sesiones = RepositorioSesiones(db)

    def obtener_usuario_actual(self, authorization: str | None) -> dict:
        """Valida el token del header Authorization y retorna los datos del usuario."""
        if not authorization:
            raise HTTPException(status_code=401, detail="Token no proporcionado")

        token = authorization.replace("Bearer ", "").strip()
        sesion = self.repositorio_sesiones.obtener_por_token(token)

        if not sesion or not sesion.usuario:
            raise HTTPException(status_code=401, detail="Sesión inválida o expirada")

        usuario = sesion.usuario
        return {
            "id":         usuario.id,
            "nombre":     usuario.nombre,
            "email":      usuario.email,
            "rol_id":     usuario.rol_id,
            "nombre_rol": usuario.rol.nombre_rol,
        }

    def obtener_usuario_opcional(self, authorization: str | None) -> dict | None:
        """Intenta obtener el usuario; retorna None si no hay token válido."""
        if not authorization:
            return None
        try:
            return self.obtener_usuario_actual(authorization)
        except HTTPException:
            return None
