from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from repositorios import RepositorioGeolocalizaciones, RepositorioReportes, RepositorioLogs


class ServicioGeolocalizaciones:
    """
    Capa de negocio para geolocalizaciones.
    Orquesta las operaciones usando los repositorios correspondientes.
    """

    def __init__(self, db: Session):
        self.db                        = db
        self.repositorio_geos          = RepositorioGeolocalizaciones(db)
        self.repositorio_reportes      = RepositorioReportes(db)
        self.repositorio_logs          = RepositorioLogs(db)

    def listar_todas(self):
        return self.repositorio_geos.obtener_todas_activas()

    def obtener_por_id(self, geo_id: int):
        g = self.repositorio_geos.obtener_por_id(geo_id)
        if not g:
            raise HTTPException(status_code=404, detail=f"Geolocalización con id {geo_id} no encontrada")
        return g

    def crear(self, datos: dict, usuario_id: int) -> dict:
        reporte = self.repositorio_reportes.obtener_activo_por_id(datos["reporte_id"])
        if not reporte:
            raise HTTPException(status_code=404, detail="El reporte no existe o está inactivo")

        try:
            nueva = self.repositorio_geos.crear(
                latitud=datos["latitud"],
                longitud=datos["longitud"],
                reporte_id=datos["reporte_id"],
                altitud=datos.get("altitud"),
                precision=datos.get("precision"),
            )
            self.repositorio_logs.registrar(
                usuario_id, "CREAR", "geolocalizaciones",
                f"Geolocalización {nueva.id} para reporte {datos['reporte_id']}",
                valor_nuevo=datos
            )
            return {"id": nueva.id, **datos}
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=422, detail="Ya existe una geolocalización para este reporte")
        except Exception:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Error al crear la geolocalización")

    def actualizar(self, geo_id: int, datos: dict, usuario_id: int) -> dict:
        g = self.repositorio_geos.obtener_por_id(geo_id)
        if not g:
            raise HTTPException(status_code=404, detail=f"Geolocalización con id {geo_id} no encontrada")

        anterior = {
            "latitud":    float(g.latitud)    if g.latitud    else None,
            "longitud":   float(g.longitud)   if g.longitud   else None,
            "altitud":    float(g.altitud)    if g.altitud    else None,
            "precision":  float(g.precision)  if g.precision  else None,
            "reporte_id": g.reporte_id,
        }
        campos = {k: v for k, v in datos.items() if v is not None}
        if campos:
            self.repositorio_geos.actualizar(g, campos)
            self.repositorio_logs.registrar(usuario_id, "ACTUALIZAR", "geolocalizaciones",
                                            f"Geolocalización {geo_id} modificada",
                                            valor_anterior=anterior, valor_nuevo=campos)
        return {"mensaje": f"Geolocalización {geo_id} actualizada", "campos": list(campos.keys())}

    def eliminar(self, geo_id: int, usuario_id: int) -> dict:
        g = self.repositorio_geos.obtener_por_id(geo_id)
        if not g:
            raise HTTPException(status_code=404, detail=f"Geolocalización con id {geo_id} no encontrada")
        reporte_id = g.reporte_id
        self.repositorio_geos.eliminar(g)
        self.repositorio_logs.registrar(usuario_id, "ELIMINAR", "geolocalizaciones",
                                        f"Geolocalización {geo_id} eliminada para reporte {reporte_id}")
        return {"mensaje": f"Geolocalización {geo_id} eliminada físicamente"}
