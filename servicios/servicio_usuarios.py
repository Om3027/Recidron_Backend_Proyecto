from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from repositorios import RepositorioUsuarios, RepositorioRoles, RepositorioLogs
from utils.security import get_password_hash, verify_password


class ServicioUsuarios:
    """
    Capa de negocio para usuarios.
    Orquesta las operaciones usando los repositorios correspondientes.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repositorio_usuarios = RepositorioUsuarios(db)
        self.repositorio_roles    = RepositorioRoles(db)
        self.repositorio_logs     = RepositorioLogs(db)

    def listar_todos(self) -> list:
        usuarios = self.repositorio_usuarios.obtener_todos()
        return [
            {
                "id": u.id, "nombre": u.nombre, "email": u.email,
                "codigo_estudiantil": u.codigo_estudiantil,
                "es_activo": u.es_activo, "rol_id": u.rol_id,
                "nombre_rol": u.rol.nombre_rol,
                "creado_en": u.creado_en,
            }
            for u in usuarios
        ]

    def obtener_por_id(self, usuario_id: int) -> dict:
        u = self.repositorio_usuarios.obtener_activo_por_id(usuario_id)
        if not u:
            raise HTTPException(status_code=404, detail=f"Usuario con id {usuario_id} no encontrado")
        return {
            "id": u.id, "nombre": u.nombre, "email": u.email,
            "codigo_estudiantil": u.codigo_estudiantil,
            "es_activo": u.es_activo, "rol_id": u.rol_id,
            "nombre_rol": u.rol.nombre_rol,
            "creado_en": u.creado_en,
        }

    def obtener_perfil_propio(self, usuario_id: int) -> dict:
        u = self.repositorio_usuarios.obtener_por_id(usuario_id)
        return {
            "id": u.id, "nombre": u.nombre, "email": u.email,
            "codigo_estudiantil": u.codigo_estudiantil,
            "rol_id": u.rol_id,
            "nombre_rol": u.rol.nombre_rol,
            "creado_en": u.creado_en,
        }

    def registrar(self, datos: dict, usuario_auth: dict | None = None) -> dict:
        """
        Registra un nuevo usuario aplicando las reglas de negocio:
        - Sin token (público): se fuerza rol_id = 2 (Autor/Estudiante).
        - Con token de admin con permiso: se permite elegir cualquier rol.
        """
        rol_autor = self.repositorio_roles.obtener_por_nombre("autor")
        if not rol_autor:
            raise HTTPException(status_code=500, detail="El rol base 'autor' no está configurado en el sistema")
            
        rol_final = rol_autor.id
        es_admin = False

        if usuario_auth and self.repositorio_usuarios.rol_tiene_permiso(usuario_auth["rol_id"], "usuarios:crear"):
            es_admin = True
            if datos.get("rol_id"):
                rol_final = datos["rol_id"]

        if not self.repositorio_roles.obtener_por_id(rol_final):
            raise HTTPException(status_code=404, detail="El rol especificado no existe")

        try:
            hashed = get_password_hash(datos["password"])
            nuevo = self.repositorio_usuarios.crear(
                nombre=datos["nombre"],
                email=datos["email"],
                password_hash=hashed,
                rol_id=rol_final,
                codigo_estudiantil=datos.get("codigo_estudiantil"),
            )

            log_id = usuario_auth["id"] if es_admin else nuevo.id
            detalle = f"Usuario {nuevo.id} registrado por Admin" if es_admin else "Auto-registro de nuevo usuario"
            self.repositorio_logs.registrar(
                log_id, "CREAR", "usuarios", detalle,
                valor_nuevo={k: v for k, v in datos.items() if k != "password"}
            )

            return {
                "id": nuevo.id, "nombre": nuevo.nombre,
                "email": nuevo.email,
                "codigo_estudiantil": nuevo.codigo_estudiantil,
                "rol_id": rol_final,
            }
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=422, detail="El email ya está registrado")
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Error interno al crear el usuario")

    def actualizar_perfil_propio(self, usuario_id: int, datos: dict) -> dict:
        """
        Permite al usuario editar su propio perfil.
        - Solo puede cambiar: nombre, email, codigo_estudiantil y contraseña.
        - Si envía nueva_password, confirmar_password es obligatorio y deben coincidir.
        - Mínimo 8 caracteres para la nueva contraseña.
        """
        usuario = self.repositorio_usuarios.obtener_activo_por_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        nueva_pass   = datos.get("nueva_password")
        confirma     = datos.get("confirmar_password")

        # ── Validaciones de contraseña ─────────────────────────────────────────
        if nueva_pass or confirma:
            if not nueva_pass or not confirma:
                raise HTTPException(
                    status_code=422,
                    detail="Debes enviar nueva_password y confirmar_password juntos."
                )
            if nueva_pass != confirma:
                raise HTTPException(status_code=422, detail="Las contraseñas no coinciden.")
            if len(nueva_pass) < 8:
                raise HTTPException(
                    status_code=422,
                    detail="La contraseña debe tener al menos 8 caracteres."
                )

        # ── Construir campos a actualizar ──────────────────────────────────────
        campos: dict = {}
        for campo in ("nombre", "email", "codigo_estudiantil"):
            if datos.get(campo) is not None:
                campos[campo] = datos[campo]

        if nueva_pass:
            campos["password"] = get_password_hash(nueva_pass)

        valor_anterior = {
            "nombre": usuario.nombre,
            "email":  usuario.email,
            "codigo_estudiantil": usuario.codigo_estudiantil,
        }

        if campos:
            self.repositorio_usuarios.actualizar(usuario, campos)
            campos_log = {k: v for k, v in campos.items() if k != "password"}
            self.repositorio_logs.registrar(
                usuario_id, "ACTUALIZAR", "usuarios",
                "Usuario actualizó su propio perfil",
                valor_anterior=valor_anterior, valor_nuevo=campos_log,
            )

        return {
            "mensaje": "Perfil actualizado correctamente",
            "campos":  [k for k in campos if k != "password"],
        }

    def actualizar(self, usuario_id: int, datos: dict, auth_usuario_id: int) -> dict:
        auth_user = self.repositorio_usuarios.obtener_activo_por_id(auth_usuario_id)
        if not auth_user:
            raise HTTPException(status_code=401, detail="Usuario autenticado no válido")

        usuario = self.repositorio_usuarios.obtener_por_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail=f"Usuario con id {usuario_id} no encontrado")

        campos = {k: v for k, v in datos.items() if v is not None}
        es_super_admin = auth_user.email == "admin@recidron.com"

        # Validaciones para Admin Normal
        if not es_super_admin:
            if usuario.email == "admin@recidron.com":
                raise HTTPException(status_code=403, detail="No puedes modificar la cuenta del Super Administrador principal")
            if "rol_id" in campos and campos["rol_id"] != usuario.rol_id:
                raise HTTPException(status_code=403, detail="Solo el Super Administrador puede cambiar roles de usuarios")
        else:
            if usuario.email == "admin@recidron.com" and "es_activo" in campos and not campos["es_activo"]:
                raise HTTPException(status_code=403, detail="El Super Administrador principal no puede ser desactivado")

        valor_anterior = {
            "nombre": usuario.nombre, "email": usuario.email,
            "codigo_estudiantil": usuario.codigo_estudiantil, "rol_id": usuario.rol_id,
            "es_activo": usuario.es_activo
        }


        if "password" in campos:
            campos["password"] = get_password_hash(campos["password"])

        if campos:
            self.repositorio_usuarios.actualizar(usuario, campos)
            campos_log = {k: v for k, v in campos.items() if k != "password"}
            self.repositorio_logs.registrar(
                auth_usuario_id, "ACTUALIZAR", "usuarios",
                f"Usuario {usuario_id} modificado",
                valor_anterior=valor_anterior, valor_nuevo=campos_log
            )

        return {"mensaje": f"Usuario {usuario_id} actualizado", "campos": list(campos.keys())}

    def desactivar(self, usuario_id: int, auth_usuario_id: int) -> dict:
        auth_user = self.repositorio_usuarios.obtener_activo_por_id(auth_usuario_id)
        if not auth_user or auth_user.email != "admin@recidron.com":
            raise HTTPException(status_code=403, detail="Solo el Super Administrador puede desactivar cuentas")

        usuario = self.repositorio_usuarios.obtener_activo_por_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail=f"Usuario con id {usuario_id} no encontrado")

        self.repositorio_usuarios.desactivar(usuario)
        self.repositorio_logs.registrar(
            auth_usuario_id, "ELIMINAR", "usuarios",
            f"Usuario {usuario_id} desactivado (soft-delete)"
        )
        return {"mensaje": f"Usuario {usuario_id} desactivado exitosamente"}
