from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import get_db, Reporte, User, TipoResiduo, Material, ZonaCampus, Tamano
from validators import ReporteCreate, ReporteUpdate
from routes.utils import error_404, registrar_log
from routes.auth import check_permission

router_reportes = APIRouter(prefix="/reportes", tags=[" Reportes"])

@router_reportes.get("/", summary="Listar todos los reportes")
def listar_reportes(user: dict = Depends(check_permission("reportes:leer")), db: Session = Depends(get_db)):
    """Consulta todos los reportes con nombres de catálogos (solo activos)."""
    reportes = db.query(Reporte).filter(Reporte.es_activo == True).order_by(Reporte.fecha_reporte.desc()).all()
    
    resultado = []
    for r in reportes:
        resultado.append({
            "id": r.id,
            "descripcion": r.descripcion,
            "fecha_reporte": r.fecha_reporte,
            "es_activo": r.es_activo,
            "usuario_id": r.usuario_id,
            "tipo_residuo_id": r.tipo_residuo_id,
            "material_id": r.material_id,
            "zona_id": r.zona_id,
            "tamano_id": r.tamano_id,
            "tipo_nombre": r.tipo_residuo.nombre_tipo if r.tipo_residuo else None,
            "material_nombre": r.material.nombre_material if r.material else None,
            "zona_nombre": r.zona.nombre_zona if r.zona else None,
            "tamano_nombre": r.tamano.nombre_tamano if r.tamano else None
        })
    return resultado

@router_reportes.post("/", status_code=201, summary="Crear un reporte")
def crear_reporte(reporte: ReporteCreate, user: dict = Depends(check_permission("reportes:crear")), db: Session = Depends(get_db)):
    """Registra un nuevo reporte de residuo y lo audita."""
    
    # Validaciones de llaves foráneas
    if not db.query(User).filter(User.id == reporte.usuario_id, User.es_activo == True).first():
        raise HTTPException(status_code=404, detail=f"Usuario con id {reporte.usuario_id} no existe o está inactivo")
    if not db.query(TipoResiduo).filter(TipoResiduo.id == reporte.tipo_residuo_id, TipoResiduo.es_activo == True).first():
        raise HTTPException(status_code=404, detail=f"TipoResiduo con id {reporte.tipo_residuo_id} no existe o está inactivo")
    if not db.query(Material).filter(Material.id == reporte.material_id, Material.es_activo == True).first():
        raise HTTPException(status_code=404, detail=f"Material con id {reporte.material_id} no existe o está inactivo")
    if not db.query(ZonaCampus).filter(ZonaCampus.id == reporte.zona_id, ZonaCampus.es_activo == True).first():
        raise HTTPException(status_code=404, detail=f"Zona con id {reporte.zona_id} no existe o está inactiva")
    if not db.query(Tamano).filter(Tamano.id == reporte.tamano_id, Tamano.es_activo == True).first():
        raise HTTPException(status_code=404, detail=f"Tamano con id {reporte.tamano_id} no existe o está inactivo")

    # Inserción
    nuevo_reporte = Reporte(
        descripcion=reporte.descripcion,
        usuario_id=reporte.usuario_id,
        tipo_residuo_id=reporte.tipo_residuo_id,
        material_id=reporte.material_id,
        zona_id=reporte.zona_id,
        tamano_id=reporte.tamano_id
    )
    db.add(nuevo_reporte)
    db.commit()
    db.refresh(nuevo_reporte)
    
    # Auditoría
    registrar_log(user['id'], "CREAR", "reportes", f"Reporte {nuevo_reporte.id} creado", v_nuevo=reporte.dict(), db=db)
    
    return {"id": nuevo_reporte.id, **reporte.dict()}

@router_reportes.get("/{id}", summary="Obtener reporte por ID")
def obtener_reporte(id: int, user: dict = Depends(check_permission("reportes:leer")), db: Session = Depends(get_db)):
    """Retorna un reporte específico que esté activo."""
    r = db.query(Reporte).filter(Reporte.id == id, Reporte.es_activo == True).first()
    if not r: error_404("Reporte", id)
    return r

@router_reportes.put("/{id}", summary="Actualizar reporte")
def actualizar_reporte(id: int, datos: ReporteUpdate, user: dict = Depends(check_permission("reportes:editar")), db: Session = Depends(get_db)):
    """Modifica los datos de un reporte activo y registra el cambio anterior/nuevo."""
    r = db.query(Reporte).filter(Reporte.id == id, Reporte.es_activo == True).first()
    if not r:
        error_404("Reporte", id)
    
    v_anterior = {
        "descripcion": r.descripcion,
        "usuario_id": r.usuario_id,
        "tipo_residuo_id": r.tipo_residuo_id,
        "material_id": r.material_id,
        "zona_id": r.zona_id,
        "tamano_id": r.tamano_id
    }
    
    campos = {k: v for k, v in datos.dict().items() if v is not None}
    if campos:
        for k, v in campos.items():
            setattr(r, k, v)
        db.commit()
        
        # Auditoría con trazabilidad de valores
        registrar_log(user['id'], "ACTUALIZAR", "reportes", f"Reporte {id} modificado", 
                      v_anterior=v_anterior, v_nuevo=campos, db=db)
    
    return {"mensaje": f"Reporte {id} actualizado", "campos": list(campos.keys())}

@router_reportes.delete("/{id}", summary="Eliminar reporte (Soft-Delete)")
def eliminar_reporte(id: int, user: dict = Depends(check_permission("reportes:eliminar")), db: Session = Depends(get_db)):
    """Realiza un borrado lógico (es_activo = 0) del reporte."""
    r = db.query(Reporte).filter(Reporte.id == id, Reporte.es_activo == True).first()
    if not r:
        error_404("Reporte", id)
        
    r.es_activo = False
    db.commit()
    
    registrar_log(user['id'], "ELIMINAR", "reportes", f"Reporte {id} marcado como inactivo (soft-delete)", db=db)
    
    return {"mensaje": f"Reporte {id} eliminado exitosamente (lógico)"}

@router_reportes.get("/stats/my", summary="Estadísticas de mis reportes")
def obtener_mis_estadisticas(user: dict = Depends(check_permission("reportes:leer")), db: Session = Depends(get_db)):
    """Retorna un resumen de la actividad del usuario autenticado."""
    try:
        # 1. Total de reportes propios
        total = db.query(Reporte).filter(Reporte.usuario_id == user['id'], Reporte.es_activo == True).count()
        
        # 2. Material que más acostumbra reportar
        top_material = db.query(Material.nombre_material.label('material'), func.count(Reporte.id).label('cantidad')) \
            .join(Reporte, Material.id == Reporte.material_id) \
            .filter(Reporte.usuario_id == user['id'], Reporte.es_activo == True) \
            .group_by(Material.id, Material.nombre_material) \
            .order_by(func.count(Reporte.id).desc()) \
            .first()
        
        # 3. Zonas en las que ha participado
        zonas = db.query(func.count(func.distinct(Reporte.zona_id))) \
            .filter(Reporte.usuario_id == user['id'], Reporte.es_activo == True).scalar()
        
        return {
            "stats": [
                {"title": "Mis Reportes", "value": str(total), "subtitle": "Total acumulado"},
                {"title": "Zonas Limpias", "value": str(zonas or 0), "subtitle": "Diferentes lugares"},
                {"title": "Material Top", "value": top_material.material if top_material else "Ninguno", "subtitle": "Más frecuente"},
                {"title": "Mi Rango", "value": "Colaborador", "subtitle": "Usuario activo"}
            ]
        }
    except Exception as e:
        print(f"Error en stats/my: {e}")
        return {"stats": []}
