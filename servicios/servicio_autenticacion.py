from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import string
from repositorios import RepositorioSesiones, RepositorioUsuarios, RepositorioRecuperacion
from utils.email import enviar_email_recuperacion
from utils.security import get_password_hash


class ServicioAutenticacion:
    """
    Capa de negocio para autenticación.
    Valida tokens y permisos usando el repositorio de sesiones.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repositorio_sesiones = RepositorioSesiones(db)
        self.repositorio_usuarios = RepositorioUsuarios(db)
        self.repositorio_recuperacion = RepositorioRecuperacion(db)

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

    def solicitar_recuperacion(self, email: str, background_tasks: BackgroundTasks) -> dict:
        """Genera un código OTP, lo guarda y encola el envío del correo."""
        usuario = self.repositorio_usuarios.obtener_por_email(email)
        
        # Por seguridad (prevención de enumeración de usuarios), siempre retornamos éxito.
        if not usuario or not usuario.es_activo:
            return {"mensaje": "Si el correo está registrado, recibirás un código de verificación."}

        # 1. Invalidar códigos anteriores
        self.repositorio_recuperacion.invalidar_codigos_anteriores(usuario.id)

        # 2. Generar código alfanumérico de 6 caracteres
        caracteres = string.ascii_uppercase + string.digits
        codigo = ''.join(secrets.choice(caracteres) for _ in range(6))
        
        # 3. Guardar código (expira en 15 minutos)
        expira_en = datetime.utcnow() + timedelta(minutes=15)
        self.repositorio_recuperacion.crear_codigo(usuario.id, codigo, expira_en)

        # 4. Enviar correo en background
        background_tasks.add_task(enviar_email_recuperacion, email, codigo)

        return {"mensaje": "Si el correo está registrado, recibirás un código de verificación."}

    def restablecer_password(self, email: str, codigo: str, nueva_password: str) -> dict:
        """Valida el código OTP y actualiza la contraseña."""
        usuario = self.repositorio_usuarios.obtener_por_email(email)
        
        if not usuario or not usuario.es_activo:
            raise HTTPException(status_code=400, detail="Código inválido o expirado.")

        codigo_obj = self.repositorio_recuperacion.obtener_codigo_valido(usuario.id, codigo)
        if not codigo_obj:
            raise HTTPException(status_code=400, detail="Código inválido o expirado.")

        # 1. Actualizar contraseña
        password_hasheada = get_password_hash(nueva_password)
        self.repositorio_usuarios.actualizar(usuario, {"password": password_hasheada})

        # 2. Marcar código como usado
        self.repositorio_recuperacion.marcar_como_usado(codigo_obj)

        return {"mensaje": "Contraseña actualizada exitosamente."}
