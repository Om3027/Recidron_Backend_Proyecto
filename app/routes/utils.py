from fastapi import HTTPException

def error_404(recurso: str, id: int):
    """Lanza error 404 estándar cuando no se encuentra un registro."""
    raise HTTPException(status_code=404, detail=f"{recurso} con id {id} no encontrado")
