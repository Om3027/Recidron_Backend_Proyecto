from sqlalchemy.orm import Session
from app.database import SessionLocal
from .sqlalchemy_models import Role, User, Session as SessionModel, LogAuditoria

def _get_db():
    return SessionLocal()

# --- ROLES ---
def get_all_roles():
    db = _get_db()
    try:
        roles = db.query(Role).order_by(Role.id).all()
        return [r.__dict__ for r in roles]
    finally:
        db.close()

def get_role_by_id(role_id: int):
    db = _get_db()
    try:
        role = db.query(Role).filter(Role.id == role_id).first()
        return role.__dict__ if role else None
    finally:
        db.close()

def create_role(nombre_rol: str):
    db = _get_db()
    try:
        nuevo_rol = Role(nombre_rol=nombre_rol)
        db.add(nuevo_rol)
        db.commit()
        db.refresh(nuevo_rol)
        return nuevo_rol.id
    finally:
        db.close()

def update_role(role_id: int, nombre_rol: str):
    db = _get_db()
    try:
        db.query(Role).filter(Role.id == role_id).update({"nombre_rol": nombre_rol})
        db.commit()
    finally:
        db.close()

def delete_role(role_id: int):
    db = _get_db()
    try:
        db.query(Role).filter(Role.id == role_id).delete()
        db.commit()
    finally:
        db.close()


# --- USUARIOS ---
def get_all_users():
    db = _get_db()
    try:
        usuarios = db.query(User).order_by(User.id).all()
        # Excluimos el password manualmente para seguridad
        res = []
        for u in usuarios:
            d = u.__dict__.copy()
            d.pop('password', None)
            d.pop('_sa_instance_state', None)
            res.append(d)
        return res
    finally:
        db.close()

def get_user_by_id(user_id: int):
    db = _get_db()
    try:
        u = db.query(User).filter(User.id == user_id).first()
        if u:
            d = u.__dict__.copy()
            d.pop('password', None)
            d.pop('_sa_instance_state', None)
            return d
        return None
    finally:
        db.close()

def create_user(nombre, email, password, rol_id):
    db = _get_db()
    try:
        nuevo_usuario = User(nombre=nombre, email=email, password=password, rol_id=rol_id)
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario.id
    finally:
        db.close()

def update_user(user_id: int, campos: dict):
    db = _get_db()
    try:
        db.query(User).filter(User.id == user_id).update(campos)
        db.commit()
    finally:
        db.close()

def deactivate_user(user_id: int):
    db = _get_db()
    try:
        db.query(User).filter(User.id == user_id).update({"activo": 0})
        db.commit()
    finally:
        db.close()


# --- SESIONES ---
def get_all_sessions():
    db = _get_db()
    try:
        sesiones = db.query(SessionModel).order_by(SessionModel.id).all()
        return [s.__dict__ for s in sesiones]
    finally:
        db.close()

def get_session_by_id(session_id: int):
    db = _get_db()
    try:
        s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        return s.__dict__ if s else None
    finally:
        db.close()

def create_session(usuario_id, token, expira_en):
    db = _get_db()
    try:
        nueva_sesion = SessionModel(usuario_id=usuario_id, token=token, expira_en=expira_en)
        db.add(nueva_sesion)
        db.commit()
        db.refresh(nueva_sesion)
        return nueva_sesion.id
    finally:
        db.close()

def update_session(session_id, usuario_id, token, expira_en):
    db = _get_db()
    try:
        db.query(SessionModel).filter(SessionModel.id == session_id).update({
            "usuario_id": usuario_id,
            "token": token,
            "expira_en": expira_en
        })
        db.commit()
    finally:
        db.close()

def delete_session(session_id: int):
    db = _get_db()
    try:
        db.query(SessionModel).filter(SessionModel.id == session_id).delete()
        db.commit()
    finally:
        db.close()


# --- LOGS ---
def get_all_logs():
    db = _get_db()
    try:
        logs = db.query(LogAuditoria).order_by(LogAuditoria.fecha.desc()).all()
        return [l.__dict__ for l in logs]
    finally:
        db.close()

def get_log_by_id(log_id: int):
    db = _get_db()
    try:
        log = db.query(LogAuditoria).filter(LogAuditoria.id == log_id).first()
        return log.__dict__ if log else None
    finally:
        db.close()

def create_log(usuario_id, accion, tabla, descripcion):
    db = _get_db()
    try:
        nuevo_log = LogAuditoria(usuario_id=usuario_id, accion=accion, tabla=tabla, descripcion=descripcion)
        db.add(nuevo_log)
        db.commit()
        db.refresh(nuevo_log)
        return nuevo_log.id
    finally:
        db.close()

def update_log(log_id, usuario_id, accion, tabla, descripcion):
    db = _get_db()
    try:
        db.query(LogAuditoria).filter(LogAuditoria.id == log_id).update({
            "usuario_id": usuario_id,
            "accion": accion,
            "tabla": tabla,
            "descripcion": descripcion
        })
        db.commit()
    finally:
        db.close()

def delete_log(log_id: int):
    db = _get_db()
    try:
        db.query(LogAuditoria).filter(LogAuditoria.id == log_id).delete()
        db.commit()
    finally:
        db.close()

