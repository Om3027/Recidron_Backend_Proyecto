from fastapi import HTTPException
from sqlalchemy.orm import Session
from repositorios import (
    RepositorioReportes, RepositorioUsuarios, RepositorioTiposResiduo,
    RepositorioMateriales, RepositorioZonasCampus, RepositorioTamanos, RepositorioLogs,
    RepositorioFotos, RepositorioGeolocalizaciones,
)
from utils.cloudinary_upload import subir_imagen_cloudinary


class ServicioReportes:
    """
    Capa de negocio para reportes de residuos.
    Orquesta las operaciones usando los repositorios correspondientes.
    """

    def __init__(self, db: Session):
        self.db                    = db
        self.repositorio_reportes  = RepositorioReportes(db)
        self.repositorio_usuarios  = RepositorioUsuarios(db)
        self.repositorio_tipos     = RepositorioTiposResiduo(db)
        self.repositorio_mats      = RepositorioMateriales(db)
        self.repositorio_zonas     = RepositorioZonasCampus(db)
        self.repositorio_tamanos   = RepositorioTamanos(db)
        self.repositorio_logs      = RepositorioLogs(db)
        self.repositorio_fotos     = RepositorioFotos(db)
        self.repositorio_geos      = RepositorioGeolocalizaciones(db)

    def listar_todos(self, skip: int = 0, limit: int = 10,
                     tipo_nombre: str = None, fecha_inicio: str = None, 
                     fecha_fin: str = None) -> list:
        reportes = self.repositorio_reportes.obtener_todos_activos(
            skip=skip, limit=limit, tipo_nombre=tipo_nombre, 
            fecha_inicio=fecha_inicio, fecha_fin=fecha_fin
        )
        return [
            {
                "id":              r.id,
                "descripcion":     r.descripcion,
                "fecha_reporte":   r.fecha_reporte,
                "es_activo":       r.es_activo,
                "usuario_id":      r.usuario_id,
                "tipo_residuo_id": r.tipo_residuo_id,
                "material_id":     r.material_id,
                "zona_id":         r.zona_id,
                "tamano_id":       r.tamano_id,
                "usuario_nombre":  r.usuario.nombre                 if r.usuario       else None,
                "tipo_nombre":     r.tipo_residuo.nombre_tipo       if r.tipo_residuo else None,
                "material_nombre": r.material.nombre_material       if r.material     else None,
                "zona_nombre":     r.zona.nombre_zona               if r.zona          else None,
                "tamano_nombre":   r.tamano.nombre_tamano           if r.tamano        else None,
                "foto_url":        r.foto.url                       if r.foto          else None,
                "geolocalizacion": {
                    "id": r.geolocalizacion.id,
                    "latitud": float(r.geolocalizacion.latitud) if r.geolocalizacion.latitud is not None else None,
                    "longitud": float(r.geolocalizacion.longitud) if r.geolocalizacion.longitud is not None else None,
                    "altitud": float(r.geolocalizacion.altitud) if r.geolocalizacion.altitud is not None else None,
                    "precision": float(r.geolocalizacion.precision) if r.geolocalizacion.precision is not None else None,
                } if r.geolocalizacion else None,
                "latitud": float(r.geolocalizacion.latitud) if (r.geolocalizacion and r.geolocalizacion.latitud is not None) else None,
                "longitud": float(r.geolocalizacion.longitud) if (r.geolocalizacion and r.geolocalizacion.longitud is not None) else None,
            }
            for r in reportes
        ]

    def obtener_por_id(self, reporte_id: int):
        r = self.repositorio_reportes.obtener_activo_por_id(reporte_id)
        if not r:
            raise HTTPException(status_code=404, detail=f"Reporte con id {reporte_id} no encontrado")
        
        geo_dict = None
        if r.geolocalizacion:
            geo_dict = {
                "id": r.geolocalizacion.id,
                "latitud": float(r.geolocalizacion.latitud) if r.geolocalizacion.latitud is not None else None,
                "longitud": float(r.geolocalizacion.longitud) if r.geolocalizacion.longitud is not None else None,
                "altitud": float(r.geolocalizacion.altitud) if r.geolocalizacion.altitud is not None else None,
                "precision": float(r.geolocalizacion.precision) if r.geolocalizacion.precision is not None else None,
                "reporte_id": r.id,
            }

        foto_dict = None
        if r.foto:
            foto_dict = {
                "id": r.foto.id,
                "url": r.foto.url,
                "fecha_subida": str(r.foto.fecha_subida) if r.foto.fecha_subida else None,
                "reporte_id": r.id,
            }

        return {
            "id": r.id,
            "descripcion": r.descripcion,
            "fecha_reporte": str(r.fecha_reporte) if r.fecha_reporte else None,
            "es_activo": r.es_activo,
            "usuario_id": r.usuario_id,
            "tipo_residuo_id": r.tipo_residuo_id,
            "material_id": r.material_id,
            "zona_id": r.zona_id,
            "tamano_id": r.tamano_id,
            "usuario_nombre": r.usuario.nombre if r.usuario else None,
            "tipo_nombre": r.tipo_residuo.nombre_tipo if r.tipo_residuo else None,
            "material_nombre": r.material.nombre_material if r.material else None,
            "zona_nombre": r.zona.nombre_zona if r.zona else None,
            "tamano_nombre": r.tamano.nombre_tamano if r.tamano else None,
            "foto_url": r.foto.url if r.foto else None,
            "foto": foto_dict,
            "geolocalizacion": geo_dict,
            "latitud": geo_dict["latitud"] if geo_dict else None,
            "longitud": geo_dict["longitud"] if geo_dict else None,
            "altitud": geo_dict["altitud"] if geo_dict else None,
            "precision": geo_dict["precision"] if geo_dict else None,
        }

    def crear(self, datos: dict, usuario_id: int) -> dict:
        """Valida las llaves foráneas y registra el reporte con geolocalización opcional."""
        if not self.repositorio_usuarios.obtener_activo_por_id(datos["usuario_id"]):
            raise HTTPException(status_code=404, detail=f"Usuario con id {datos['usuario_id']} no existe o está inactivo")
        if not self.repositorio_tipos.obtener_activo_por_id(datos["tipo_residuo_id"]):
            raise HTTPException(status_code=404, detail=f"TipoResiduo con id {datos['tipo_residuo_id']} no existe o está inactivo")
        if not self.repositorio_mats.obtener_activo_por_id(datos["material_id"]):
            raise HTTPException(status_code=404, detail=f"Material con id {datos['material_id']} no existe o está inactivo")
        if not self.repositorio_zonas.obtener_activa_por_id(datos["zona_id"]):
            raise HTTPException(status_code=404, detail=f"Zona con id {datos['zona_id']} no existe o está inactiva")
        if not self.repositorio_tamanos.obtener_activo_por_id(datos["tamano_id"]):
            raise HTTPException(status_code=404, detail=f"Tamaño con id {datos['tamano_id']} no existe o está inactivo")

        nuevo = self.repositorio_reportes.crear(
            descripcion=datos.get("descripcion"),
            usuario_id=datos["usuario_id"],
            tipo_residuo_id=datos["tipo_residuo_id"],
            material_id=datos["material_id"],
            zona_id=datos["zona_id"],
            tamano_id=datos["tamano_id"],
        )

        latitud = datos.get("latitud")
        longitud = datos.get("longitud")
        altitud = datos.get("altitud")
        precision = datos.get("precision")
        geo_dict = None

        if latitud is not None and longitud is not None:
            geo = self.repositorio_geos.crear(
                latitud=float(latitud),
                longitud=float(longitud),
                reporte_id=nuevo.id,
                altitud=float(altitud) if altitud is not None else None,
                precision=float(precision) if precision is not None else None,
            )
            geo_dict = {
                "id": geo.id,
                "latitud": float(geo.latitud),
                "longitud": float(geo.longitud),
                "altitud": float(geo.altitud) if geo.altitud is not None else None,
                "precision": float(geo.precision) if geo.precision is not None else None,
                "reporte_id": nuevo.id,
            }

        self.repositorio_logs.registrar(usuario_id, "CREAR", "reportes",
                                        f"Reporte {nuevo.id} creado", valor_nuevo=datos)
        respuesta = {"id": nuevo.id, **datos}
        if geo_dict:
            respuesta["geolocalizacion"] = geo_dict
        return respuesta

    def actualizar(self, reporte_id: int, datos: dict, usuario_id: int) -> dict:
        r = self.repositorio_reportes.obtener_activo_por_id(reporte_id)
        if not r:
            raise HTTPException(status_code=404, detail=f"Reporte con id {reporte_id} no encontrado")

        anterior = {
            "descripcion": r.descripcion, "usuario_id": r.usuario_id,
            "tipo_residuo_id": r.tipo_residuo_id, "material_id": r.material_id,
            "zona_id": r.zona_id, "tamano_id": r.tamano_id,
        }
        
        geo_campos = {}
        for campo in ("latitud", "longitud", "altitud", "precision"):
            if campo in datos and datos[campo] is not None:
                geo_campos[campo] = datos[campo]

        campos_reporte = {k: v for k, v in datos.items() if v is not None and k not in ("latitud", "longitud", "altitud", "precision")}
        if campos_reporte:
            self.repositorio_reportes.actualizar(r, campos_reporte)
            self.repositorio_logs.registrar(usuario_id, "ACTUALIZAR", "reportes",
                                            f"Reporte {reporte_id} modificado",
                                            valor_anterior=anterior, valor_nuevo=campos_reporte)

        if geo_campos:
            if r.geolocalizacion:
                self.repositorio_geos.actualizar(r.geolocalizacion, geo_campos)
            elif "latitud" in geo_campos and "longitud" in geo_campos:
                self.repositorio_geos.crear(
                    latitud=float(geo_campos["latitud"]),
                    longitud=float(geo_campos["longitud"]),
                    reporte_id=reporte_id,
                    altitud=float(geo_campos["altitud"]) if "altitud" in geo_campos else None,
                    precision=float(geo_campos["precision"]) if "precision" in geo_campos else None,
                )

        campos_modificados = list(campos_reporte.keys()) + list(geo_campos.keys())
        return {"mensaje": f"Reporte {reporte_id} actualizado", "campos": campos_modificados}

    def desactivar(self, reporte_id: int, usuario_id: int) -> dict:
        r = self.repositorio_reportes.obtener_activo_por_id(reporte_id)
        if not r:
            raise HTTPException(status_code=404, detail=f"Reporte con id {reporte_id} no encontrado")
        self.repositorio_reportes.desactivar(r)
        self.repositorio_logs.registrar(usuario_id, "ELIMINAR", "reportes",
                                        f"Reporte {reporte_id} marcado como inactivo (soft-delete)")
        return {"mensaje": f"Reporte {reporte_id} eliminado exitosamente (lógico)"}

    def agregar_o_actualizar_foto(self, reporte_id: int, archivo_bytes: bytes, usuario_id: int) -> dict:
        r = self.repositorio_reportes.obtener_activo_por_id(reporte_id)
        if not r:
            raise HTTPException(status_code=404, detail=f"Reporte con id {reporte_id} no encontrado")
        
        # Validar si el usuario tiene permiso sobre este reporte (opcional, dependiendo de tus reglas)
        # if r.usuario_id != usuario_id:
        #    raise HTTPException(status_code=403, detail="No tienes permiso para modificar este reporte")

        # Subir a Cloudinary
        url_segura = subir_imagen_cloudinary(archivo_bytes)
        
        # Guardar en base de datos
        foto = self.repositorio_fotos.guardar_o_actualizar(reporte_id, url_segura)
        
        # Registrar log
        self.repositorio_logs.registrar(usuario_id, "ACTUALIZAR", "fotos_reporte",
                                        f"Foto subida para el reporte {reporte_id}", valor_nuevo={"url": url_segura})
                                        
        return {"mensaje": "Foto subida exitosamente", "url": url_segura}

    def mis_estadisticas(self, usuario_id: int) -> dict:
        total    = self.repositorio_reportes.contar_por_usuario(usuario_id)
        top_mat  = self.repositorio_reportes.material_mas_frecuente_por_usuario(usuario_id)
        zonas    = self.repositorio_reportes.contar_zonas_distintas_por_usuario(usuario_id)
        return {
            "stats": [
                {"title": "Mis Reportes",  "value": str(total),       "subtitle": "Total acumulado"},
                {"title": "Zonas Limpias", "value": str(zonas or 0),  "subtitle": "Diferentes lugares"},
                {"title": "Material Top",  "value": top_mat.material if top_mat else "Ninguno",
                 "subtitle": "Más frecuente"},
                {"title": "Mi Rango",      "value": "Colaborador",    "subtitle": "Usuario activo"},
            ]
        }
