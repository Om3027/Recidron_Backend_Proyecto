from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from repositorios import RepositorioSubzonas, RepositorioZonasCampus, RepositorioLogs


class ServicioSubzonas:
    """
    Capa de negocio para la gestión de subzonas y tipos de subzona.
    Orquesta las operaciones usando los repositorios correspondientes.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repositorio_subzonas = RepositorioSubzonas(db)
        self.repositorio_zonas = RepositorioZonasCampus(db)
        self.repositorio_logs = RepositorioLogs(db)

    def listar_subzonas(
        self,
        zona_id: Optional[int] = None,
        tipo_id: Optional[int] = None,
        piso: Optional[str] = None
    ) -> list[dict]:
        """Retorna las subzonas activas filtradas por zona, tipo o piso."""
        subzonas = self.repositorio_subzonas.obtener_todas_activas(
            zona_id=zona_id,
            tipo_id=tipo_id,
            piso=piso
        )
        return [
            {
                "id": s.id,
                "nombre_subzona": s.nombre_subzona,
                "piso": s.piso,
                "zona_id": s.zona_id,
                "tipo_subzona_id": s.tipo_subzona_id,
                "tipo_subzona_nombre": s.tipo_subzona.nombre_tipo if s.tipo_subzona else None,
                "es_activo": s.es_activo,
            }
            for s in subzonas
        ]

    def obtener_subzona(self, subzona_id: int) -> dict:
        """Obtiene una subzona por ID o lanza 404."""
        s = self.repositorio_subzonas.obtener_activa_por_id(subzona_id)
        if not s:
            raise HTTPException(status_code=404, detail=f"Subzona con id {subzona_id} no encontrada")
        return {
            "id": s.id,
            "nombre_subzona": s.nombre_subzona,
            "piso": s.piso,
            "zona_id": s.zona_id,
            "tipo_subzona_id": s.tipo_subzona_id,
            "tipo_subzona_nombre": s.tipo_subzona.nombre_tipo if s.tipo_subzona else None,
            "es_activo": s.es_activo,
        }

    def listar_tipos(self) -> list[dict]:
        """Retorna el catálogo oficial de tipos de subzona."""
        tipos = self.repositorio_subzonas.obtener_tipos_activos()
        return [
            {
                "id": t.id,
                "nombre_tipo": t.nombre_tipo,
                "es_activo": t.es_activo,
            }
            for t in tipos
        ]

    def crear_subzona(self, datos: dict, usuario_id: int) -> dict:
        """Crea una nueva subzona validando que la zona exista."""
        if not self.repositorio_zonas.obtener_activa_por_id(datos["zona_id"]):
            raise HTTPException(status_code=404, detail=f"Zona con id {datos['zona_id']} no existe")
        
        nueva = self.repositorio_subzonas.crear(
            nombre_subzona=datos["nombre_subzona"],
            zona_id=datos["zona_id"],
            tipo_subzona_id=datos["tipo_subzona_id"],
            piso=datos.get("piso", "1"),
        )
        self.repositorio_logs.registrar(
            usuario_id, "CREAR", "subzonas_campus",
            f"Subzona {nueva.id} ({nueva.nombre_subzona}) creada",
            valor_nuevo=datos
        )
        return {
            "id": nueva.id,
            "nombre_subzona": nueva.nombre_subzona,
            "piso": nueva.piso,
            "zona_id": nueva.zona_id,
            "tipo_subzona_id": nueva.tipo_subzona_id,
            "tipo_subzona_nombre": nueva.tipo_subzona.nombre_tipo if nueva.tipo_subzona else None,
            "es_activo": nueva.es_activo,
        }
