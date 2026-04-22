from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import get_db, Geolocalizacion, Reporte
from validators import GeoCreate, GeoUpdate
from routes.utils import error_404, registrar_log
from routes.auth import check_permission

router_geos = APIRouter(prefix="/geos", tags=[" Geolocalizaciones"])

@router_geos.get("/", summary="Listar geolocalizaciones")
def listar_geos(user_auth: dict = Depends(check_permission("reportes:leer")), db: Session = Depends(get_db)):
    """Lista coordenadas GPS de reportes activos."""
    geos = db.query(Geolocalizacion).join(Reporte).filter(Reporte.es_activo == True).all()
    return geos

@router_geos.post("/", status_code=201, summary="Registrar geolocalización")
def crear_geo(geo: GeoCreate, user_auth: dict = Depends(check_permission("reportes:crear")), db: Session = Depends(get_db)):
    """Asocia coordenadas GPS a un reporte con auditoría."""
    reporte = db.query(Reporte).filter(Reporte.id == geo.reporte_id, Reporte.es_activo == True).first()
    if not reporte:
        raise HTTPException(status_code=404, detail="El reporte no existe o está inactivo")
        
    try:
        nueva_geo = Geolocalizacion(
            latitud=geo.latitud,
            longitud=geo.longitud,
            altitud=geo.altitud,
            precision=geo.precision,
            reporte_id=geo.reporte_id
        )
        db.add(nueva_geo)
        db.commit()
        db.refresh(nueva_geo)
        
        registrar_log(user_auth['id'], "CREAR", "geolocalizaciones", f"Geo {nueva_geo.id} para reporte {geo.reporte_id}", v_nuevo=geo.dict(), db=db)
        
        return {"id": nueva_geo.id, **geo.dict()}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=422, detail="Ya existe una geolocalización para este reporte")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear geolocalización")

@router_geos.get("/{id}", summary="Obtener geolocalización por ID")
def obtener_geo(id: int, user_auth: dict = Depends(check_permission("reportes:leer")), db: Session = Depends(get_db)):
    g = db.query(Geolocalizacion).filter(Geolocalizacion.id == id).first()
    if not g: error_404("Geolocalización", id)
    return g

@router_geos.put("/{id}", summary="Actualizar geolocalización")
def actualizar_geo(id: int, datos: GeoUpdate, user_auth: dict = Depends(check_permission("reportes:editar")), db: Session = Depends(get_db)):
    """Actualiza coordenadas con auditoría."""
    g = db.query(Geolocalizacion).filter(Geolocalizacion.id == id).first()
    if not g:
        error_404("Geolocalización", id)
        
    v_anterior = {
        "latitud": float(g.latitud) if g.latitud else None,
        "longitud": float(g.longitud) if g.longitud else None,
        "altitud": float(g.altitud) if g.altitud else None,
        "precision": float(g.precision) if g.precision else None,
        "reporte_id": g.reporte_id
    }
        
    campos = {k: v for k, v in datos.dict().items() if v is not None}
    if campos:
        for k, v in campos.items():
            setattr(g, k, v)
        db.commit()
        
        registrar_log(user_auth['id'], "ACTUALIZAR", "geolocalizaciones", f"Geo {id} modificada", 
                      v_anterior=v_anterior, v_nuevo=campos, db=db)
                      
    return {"mensaje": f"Geolocalización {id} actualizada", "campos": list(campos.keys())}

@router_geos.delete("/{id}", summary="Eliminar geolocalización")
def eliminar_geo(id: int, user_auth: dict = Depends(check_permission("reportes:eliminar")), db: Session = Depends(get_db)):
    """Elimina físicamente la geolocalización (usualmente ligada al reporte)."""
    g = db.query(Geolocalizacion).filter(Geolocalizacion.id == id).first()
    if not g:
        error_404("Geolocalización", id)
        
    reporte_id = g.reporte_id
    db.delete(g)
    db.commit()
    
    registrar_log(user_auth['id'], "ELIMINAR", "geolocalizaciones", f"Geo {id} eliminada para reporte {reporte_id}", db=db)
    
    return {"mensaje": f"Geolocalización {id} eliminada físicamente"}
