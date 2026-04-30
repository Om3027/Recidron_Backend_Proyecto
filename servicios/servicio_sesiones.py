import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from repositorios import RepositorioSesiones, RepositorioUsuarios, RepositorioLogs
from utils.security import verify_password


class ServicioSesiones:
    """
    Capa de negocio para sesiones.
    Orquesta las operaciones usando los repositorios correspondientes.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repositorio_sesiones = RepositorioSesiones(db)
        self.repositorio_usuarios = RepositorioUsuarios(db)
        self.repositorio_logs     = RepositorioLogs(db)

    def iniciar_sesion(self, email: str, password: str) -> dict:
        """Verifica credenciales y genera un token de sesión único."""
        usuario = self.repositorio_usuarios.obtener_por_email(email)
        if not usuario or not verify_password(password, usuario.password):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        if not usuario.es_activo:
<<<<<<< HEAD
            raise HTTPException(status_code=403, detail="Tu cuenta está desactivada. Por favor contacta al administrador.")
=======
            raise HTTPException(status_code=403, detail="Tu cuenta está desactivada. Por favor contacta al administrador")
>>>>>>> 6ff75cbc8f2c1888b561b803056f2632dff5cf3a

        token       = str(uuid.uuid4())
        vencimiento = datetime.now() + timedelta(hours=24)

        try:
            self.repositorio_sesiones.crear(usuario.id, token, vencimiento)
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Error al crear la sesión en la nube")

        self.repositorio_logs.registrar(usuario.id, "LOGIN", "sesiones", "Acceso exitoso al sistema")

        return {
            "id":     usuario.id,
            "token":  token,
            "email":  usuario.email,
            "nombre": usuario.nombre,
            "rol":    usuario.rol.nombre_rol,
            "rol_id": usuario.rol_id,
        }

    def listar_todas(self) -> list:
        return self.repositorio_sesiones.obtener_todas()

    def obtener_por_id(self, sesion_id: int):
        s = self.repositorio_sesiones.obtener_por_id(sesion_id)
        if not s:
            raise HTTPException(status_code=404, detail=f"Sesión con id {sesion_id} no encontrada")
        return s

    def crear_manual(self, usuario_id: int, token: str, expira_en) -> dict:
        """Registro manual de sesión desde el endpoint /sesiones POST."""
        usuario = self.repositorio_usuarios.obtener_activo_por_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="El usuario no existe o está inactivo")
        try:
            nueva = self.repositorio_sesiones.crear(usuario_id, token, expira_en)
            self.repositorio_logs.registrar(
                usuario_id, "LOGIN", "sesiones",
                f"Usuario inicio sesión (id_sesion: {nueva.id})"
            )
            return {"id": nueva.id, "usuario_id": usuario_id, "token": token, "expira_en": str(expira_en)}
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=422, detail="El token ya existe")
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Error al crear la sesión")

    def cerrar_sesion(self, sesion_id: int) -> dict:
        sesion = self.repositorio_sesiones.obtener_activa_por_id(sesion_id)
        if not sesion:
            raise HTTPException(status_code=404, detail=f"Sesión con id {sesion_id} no encontrada")
        self.repositorio_sesiones.cerrar_sesion(sesion)
        self.repositorio_logs.registrar(sesion.usuario_id, "LOGOUT", "sesiones", f"Sesión {sesion_id} cerrada")
        return {"mensaje": f"Sesión {sesion_id} cerrada exitosamente"}
