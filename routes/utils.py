from fastapi import HTTPException
from models import get_connection
import json

def error_404(recurso: str, id: int):
    """Lanza error 404 estándar cuando no se encuentra un registro."""
    raise HTTPException(status_code=404, detail=f"{recurso} con id {id} no encontrado")

def registrar_log(usuario_id: int, accion: str, recurso: str, detalles: str = None, v_anterior: dict = None, v_nuevo: dict = None):
    """
    Registra una acción en la tabla de auditoría logs_auditoria.
    Permite guardar el estado anterior y nuevo para trazabilidad administrativa.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        INSERT INTO logs_auditoria (usuario_id, accion, recurso, detalles, valor_anterior, valor_nuevo)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    # Convertir dicts a JSON string si existen
    anterior_json = json.dumps(v_anterior, default=str) if v_anterior else None
    nuevo_json = json.dumps(v_nuevo, default=str) if v_nuevo else None
    
    cursor.execute(query, (usuario_id, accion, recurso, detalles, anterior_json, nuevo_json))
    
    conn.commit()
    cursor.close()
    conn.close()
