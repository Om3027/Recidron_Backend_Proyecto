from sqlalchemy.orm import Session
from sqlalchemy import update
from models.security import PasswordRecoveryCode
from datetime import datetime

class RepositorioRecuperacion:
    """
    Repositorio para gestionar los códigos OTP de recuperación de contraseña.
    """

    def __init__(self, db: Session):
        self.db = db

    def invalidar_codigos_anteriores(self, usuario_id: int):
        """Marca como usados todos los códigos pendientes de un usuario."""
        stmt = (
            update(PasswordRecoveryCode)
            .where(PasswordRecoveryCode.usuario_id == usuario_id)
            .where(PasswordRecoveryCode.usado == False)
            .values(usado=True)
        )
        self.db.execute(stmt)
        self.db.commit()

    def crear_codigo(self, usuario_id: int, codigo: str, expira_en: datetime) -> PasswordRecoveryCode:
        """Crea un nuevo código OTP para el usuario en la BD."""
        nuevo_codigo = PasswordRecoveryCode(
            usuario_id=usuario_id,
            codigo=codigo,
            expira_en=expira_en,
            usado=False
        )
        self.db.add(nuevo_codigo)
        self.db.commit()
        self.db.refresh(nuevo_codigo)
        return nuevo_codigo

    def obtener_codigo_valido(self, usuario_id: int, codigo: str) -> PasswordRecoveryCode | None:
        """Obtiene un código de recuperación si coincide, no está usado y no ha expirado."""
        ahora = datetime.utcnow()
        return self.db.query(PasswordRecoveryCode).filter(
            PasswordRecoveryCode.usuario_id == usuario_id,
            PasswordRecoveryCode.codigo == codigo,
            PasswordRecoveryCode.usado == False,
            PasswordRecoveryCode.expira_en > ahora
        ).first()

    def marcar_como_usado(self, codigo_obj: PasswordRecoveryCode):
        """Marca un objeto PasswordRecoveryCode como usado."""
        codigo_obj.usado = True
        self.db.commit()
        self.db.refresh(codigo_obj)
