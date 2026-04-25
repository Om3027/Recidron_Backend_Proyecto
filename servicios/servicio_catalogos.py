from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from repositorios import (
    RepositorioTiposResiduo, RepositorioMateriales,
    RepositorioZonasCampus, RepositorioTamanos, RepositorioLogs,
)


class ServicioCatalogos:
    """
    Capa de negocio para los catálogos del proyecto:
    TipoResiduo, Material, ZonaCampus y Tamano.
    Orquesta las operaciones usando los repositorios correspondientes.
    """

    def __init__(self, db: Session):
        self.db                   = db
        self.repositorio_tipos    = RepositorioTiposResiduo(db)
        self.repositorio_mats     = RepositorioMateriales(db)
        self.repositorio_zonas    = RepositorioZonasCampus(db)
        self.repositorio_tamanos  = RepositorioTamanos(db)
        self.repositorio_logs     = RepositorioLogs(db)

    # ── Tipos de Residuo ──────────────────────────────────────────────────────

    def listar_tipos(self):
        return self.repositorio_tipos.obtener_todos_activos()

    def obtener_tipo(self, tipo_id: int):
        t = self.repositorio_tipos.obtener_activo_por_id(tipo_id)
        if not t:
            raise HTTPException(status_code=404, detail=f"TipoResiduo con id {tipo_id} no encontrado")
        return t

    def crear_tipo(self, nombre_tipo: str, usuario_id: int) -> dict:
        try:
            nuevo = self.repositorio_tipos.crear(nombre_tipo)
            self.repositorio_logs.registrar(usuario_id, "CREAR", "tipos_residuo", f"TipoResiduo {nuevo.id} creado")
            return {"id": nuevo.id, "nombre_tipo": nuevo.nombre_tipo}
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=422, detail="El tipo de residuo ya existe")
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Error al crear el tipo de residuo")

    def actualizar_tipo(self, tipo_id: int, nombre_tipo: str, usuario_id: int) -> dict:
        t = self.repositorio_tipos.obtener_activo_por_id(tipo_id)
        if not t:
            raise HTTPException(status_code=404, detail=f"TipoResiduo con id {tipo_id} no encontrado")
        anterior = {"nombre_tipo": t.nombre_tipo}
        self.repositorio_tipos.actualizar_nombre(t, nombre_tipo)
        self.repositorio_logs.registrar(usuario_id, "ACTUALIZAR", "tipos_residuo",
                                        f"TipoResiduo {tipo_id} actualizado",
                                        valor_anterior=anterior, valor_nuevo={"nombre_tipo": nombre_tipo})
        return {"id": tipo_id, "nombre_tipo": nombre_tipo}

    def desactivar_tipo(self, tipo_id: int, usuario_id: int) -> dict:
        t = self.repositorio_tipos.obtener_activo_por_id(tipo_id)
        if not t:
            raise HTTPException(status_code=404, detail=f"TipoResiduo con id {tipo_id} no encontrado")
        self.repositorio_tipos.desactivar(t)
        self.repositorio_logs.registrar(usuario_id, "ELIMINAR", "tipos_residuo",
                                        f"TipoResiduo {tipo_id} desactivado (soft-delete)")
        return {"mensaje": f"TipoResiduo {tipo_id} desactivado exitosamente"}

    # ── Materiales ────────────────────────────────────────────────────────────

    def listar_materiales(self):
        return self.repositorio_mats.obtener_todos_activos()

    def obtener_material(self, material_id: int):
        m = self.repositorio_mats.obtener_activo_por_id(material_id)
        if not m:
            raise HTTPException(status_code=404, detail=f"Material con id {material_id} no encontrado")
        return m

    def crear_material(self, nombre_material: str, usuario_id: int) -> dict:
        try:
            nuevo = self.repositorio_mats.crear(nombre_material)
            self.repositorio_logs.registrar(usuario_id, "CREAR", "materiales", f"Material {nuevo.id} creado")
            return {"id": nuevo.id, "nombre_material": nuevo.nombre_material}
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=422, detail="El material ya existe")
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Error al crear el material")

    def actualizar_material(self, material_id: int, nombre_material: str, usuario_id: int) -> dict:
        m = self.repositorio_mats.obtener_activo_por_id(material_id)
        if not m:
            raise HTTPException(status_code=404, detail=f"Material con id {material_id} no encontrado")
        anterior = {"nombre_material": m.nombre_material}
        self.repositorio_mats.actualizar_nombre(m, nombre_material)
        self.repositorio_logs.registrar(usuario_id, "ACTUALIZAR", "materiales",
                                        f"Material {material_id} actualizado",
                                        valor_anterior=anterior, valor_nuevo={"nombre_material": nombre_material})
        return {"id": material_id, "nombre_material": nombre_material}

    def desactivar_material(self, material_id: int, usuario_id: int) -> dict:
        m = self.repositorio_mats.obtener_activo_por_id(material_id)
        if not m:
            raise HTTPException(status_code=404, detail=f"Material con id {material_id} no encontrado")
        self.repositorio_mats.desactivar(m)
        self.repositorio_logs.registrar(usuario_id, "ELIMINAR", "materiales",
                                        f"Material {material_id} desactivado (soft-delete)")
        return {"mensaje": f"Material {material_id} desactivado exitosamente"}

    # ── Zonas Campus ──────────────────────────────────────────────────────────

    def listar_zonas(self):
        return self.repositorio_zonas.obtener_todas_activas()

    def obtener_zona(self, zona_id: int):
        z = self.repositorio_zonas.obtener_activa_por_id(zona_id)
        if not z:
            raise HTTPException(status_code=404, detail=f"Zona con id {zona_id} no encontrada")
        return z

    def crear_zona(self, nombre_zona: str, usuario_id: int) -> dict:
        try:
            nueva = self.repositorio_zonas.crear(nombre_zona)
            self.repositorio_logs.registrar(usuario_id, "CREAR", "zonas_campus", f"Zona {nueva.id} creada")
            return {"id": nueva.id, "nombre_zona": nueva.nombre_zona}
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=422, detail="La zona ya existe")
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Error al crear la zona")

    def actualizar_zona(self, zona_id: int, nombre_zona: str, usuario_id: int) -> dict:
        z = self.repositorio_zonas.obtener_activa_por_id(zona_id)
        if not z:
            raise HTTPException(status_code=404, detail=f"Zona con id {zona_id} no encontrada")
        anterior = {"nombre_zona": z.nombre_zona}
        self.repositorio_zonas.actualizar_nombre(z, nombre_zona)
        self.repositorio_logs.registrar(usuario_id, "ACTUALIZAR", "zonas_campus",
                                        f"Zona {zona_id} actualizada",
                                        valor_anterior=anterior, valor_nuevo={"nombre_zona": nombre_zona})
        return {"id": zona_id, "nombre_zona": nombre_zona}

    def desactivar_zona(self, zona_id: int, usuario_id: int) -> dict:
        z = self.repositorio_zonas.obtener_activa_por_id(zona_id)
        if not z:
            raise HTTPException(status_code=404, detail=f"Zona con id {zona_id} no encontrada")
        self.repositorio_zonas.desactivar(z)
        self.repositorio_logs.registrar(usuario_id, "ELIMINAR", "zonas_campus",
                                        f"Zona {zona_id} desactivada (soft-delete)")
        return {"mensaje": f"Zona {zona_id} desactivada exitosamente"}

    # ── Tamaños ───────────────────────────────────────────────────────────────

    def listar_tamanos(self):
        return self.repositorio_tamanos.obtener_todos_activos()

    def obtener_tamano(self, tamano_id: int):
        t = self.repositorio_tamanos.obtener_activo_por_id(tamano_id)
        if not t:
            raise HTTPException(status_code=404, detail=f"Tamaño con id {tamano_id} no encontrado")
        return t

    def crear_tamano(self, nombre_tamano: str, usuario_id: int) -> dict:
        try:
            nuevo = self.repositorio_tamanos.crear(nombre_tamano)
            self.repositorio_logs.registrar(usuario_id, "CREAR", "tamanos", f"Tamaño {nuevo.id} creado")
            return {"id": nuevo.id, "nombre_tamano": nuevo.nombre_tamano}
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=422, detail="El tamaño ya existe")
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Error al crear el tamaño")

    def actualizar_tamano(self, tamano_id: int, nombre_tamano: str, usuario_id: int) -> dict:
        t = self.repositorio_tamanos.obtener_activo_por_id(tamano_id)
        if not t:
            raise HTTPException(status_code=404, detail=f"Tamaño con id {tamano_id} no encontrado")
        anterior = {"nombre_tamano": t.nombre_tamano}
        self.repositorio_tamanos.actualizar_nombre(t, nombre_tamano)
        self.repositorio_logs.registrar(usuario_id, "ACTUALIZAR", "tamanos",
                                        f"Tamaño {tamano_id} actualizado",
                                        valor_anterior=anterior, valor_nuevo={"nombre_tamano": nombre_tamano})
        return {"id": tamano_id, "nombre_tamano": nombre_tamano}

    def desactivar_tamano(self, tamano_id: int, usuario_id: int) -> dict:
        t = self.repositorio_tamanos.obtener_activo_por_id(tamano_id)
        if not t:
            raise HTTPException(status_code=404, detail=f"Tamaño con id {tamano_id} no encontrado")
        self.repositorio_tamanos.desactivar(t)
        self.repositorio_logs.registrar(usuario_id, "ELIMINAR", "tamanos",
                                        f"Tamaño {tamano_id} desactivado (soft-delete)")
        return {"mensaje": f"Tamaño {tamano_id} desactivado exitosamente"}
