import os
from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from models import get_db
from servicios import ServicioBackups
from routes.auth import verificar_super_admin

router_backups = APIRouter(prefix="/admin/backups", tags=["Copias de Seguridad (Super Admin)"])


def _eliminar_archivo_temporal(ruta_archivo: str):
    """Tarea en segundo plano que elimina el archivo temporal tras la descarga."""
    try:
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
    except OSError:
        pass


@router_backups.get("/descargar", summary="Generar y descargar copia de seguridad (.sql.gz)")
def descargar_backup(
    background_tasks: BackgroundTasks,
    usuario_auth: dict = Depends(verificar_super_admin),
    db: Session = Depends(get_db),
):
    """
    Genera un volcado completo de la base de datos MySQL en formato comprimido (.sql.gz)
    y lo envía directamente al navegador para su descarga inmediata.
    
    El archivo temporal se elimina automáticamente del servidor en segundo plano
    tan pronto finaliza la transmisión, garantizando cero consumo de disco permanente.
    """
    servicio = ServicioBackups(db)
    ruta_temp, nombre_archivo, tamano_bytes, tamano_formateado = servicio.generar_volcado_temporal(usuario_auth)

    # Añadir tarea para eliminar el archivo tras el envío al cliente
    background_tasks.add_task(_eliminar_archivo_temporal, ruta_temp)

    return FileResponse(
        path=ruta_temp,
        filename=nombre_archivo,
        media_type="application/gzip",
        background=background_tasks,
        # "filename" ya genera el Content-Disposition; el frontend lo lee gracias a expose_headers en main.py
        headers={
            "Cache-Control": "no-store",
            "X-Backup-Size": str(tamano_bytes),
            "X-Backup-Size-Formatted": tamano_formateado,
        },
    )


@router_backups.get("/historial", summary="Obtener historial de copias de seguridad")
def obtener_historial_backups(
    usuario_auth: dict = Depends(verificar_super_admin),
    db: Session = Depends(get_db),
):
    """
    Retorna el historial de copias de seguridad generadas y descargadas,
    obtenido a partir de la bitácora de auditoría del sistema.
    """
    servicio = ServicioBackups(db)
    return servicio.obtener_historial()
