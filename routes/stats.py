from fastapi import APIRouter, Depends, HTTPException
from models import get_connection
from .auth import check_permission

# Router para manejar todas las consultas estadísticas del sistema
router_stats = APIRouter(prefix="/stats", tags=["Estadísticas"])

@router_stats.get("/dashboard", dependencies=[Depends(check_permission("reportes:leer"))])
def obtener_estadisticas_dashboard():
    """
    Breve descripción: Obtiene KPIs globales (conteo de reportes y usuarios) y 
    la distribución por tipo y zona para alimentar los gráficos del administrador.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Conteos básicos (KPIs)
        cursor.execute("SELECT COUNT(*) as total FROM reportes WHERE es_activo = 1")
        total_reportes = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE es_activo = 1")
        total_usuarios = cursor.fetchone()['total']
        
        # Gráfico de Dona: Por tipo de residuo
        query_tipos = """
            SELECT t.nombre_tipo as label, COUNT(r.id) as value
            FROM tipos_residuo t
            LEFT JOIN reportes r ON t.id = r.tipo_residuo_id AND r.es_activo = 1
            WHERE t.es_activo = 1
            GROUP BY t.id, t.nombre_tipo
        """
        cursor.execute(query_tipos)
        dist_tipos = cursor.fetchall()
        
        # Gráfico de Barras: Por zona del campus
        query_zonas = """
            SELECT z.nombre_zona as label, COUNT(r.id) as value
            FROM zonas_campus z
            LEFT JOIN reportes r ON z.id = r.zona_id AND r.es_activo = 1
            WHERE z.es_activo = 1
            GROUP BY z.id, z.nombre_zona
        """
        cursor.execute(query_zonas)
        dist_zonas = cursor.fetchall()

        # Gráfico de Barras Horizontales: Por material
        query_materiales = """
            SELECT m.nombre_material as label, COUNT(r.id) as value
            FROM materiales m
            LEFT JOIN reportes r ON m.id = r.material_id AND r.es_activo = 1
            WHERE m.es_activo = 1
            GROUP BY m.id, m.nombre_material
            ORDER BY value DESC
            LIMIT 5
        """
        cursor.execute(query_materiales)
        dist_materiales = cursor.fetchall()

        return {
            "total_reportes": total_reportes,
            "usuarios_activos": total_usuarios,
            "distribucion_tipos": dist_tipos,
            "distribucion_zonas": dist_zonas,
            "distribucion_materiales": dist_materiales
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular estadísticas: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router_stats.get("/tendencia", dependencies=[Depends(check_permission("reportes:leer"))])
def obtener_tendencia_reportes():
    """
    Breve descripción: Obtiene el conteo de reportes diarios de los últimos 30 días 
    para alimentar el gráfico de líneas (tendencia histórica).
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT DATE(fecha_reporte) as fecha, COUNT(*) as cantidad
            FROM reportes
            WHERE es_activo = 1 AND fecha_reporte >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(fecha_reporte)
            ORDER BY fecha ASC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
