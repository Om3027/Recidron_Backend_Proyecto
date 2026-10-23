import gzip
import json
import os
import tempfile
from datetime import datetime, date
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import get_connection, AuditLog
from repositorios import RepositorioLogs


def _formatear_tamano(tamano_bytes: int) -> str:
    """Convierte un tamaño en bytes a formato legible (B, KB, MB, GB)."""
    if tamano_bytes < 1024:
        return f"{tamano_bytes} B"
    elif tamano_bytes < 1024 * 1024:
        return f"{tamano_bytes / 1024:.1f} KB"
    elif tamano_bytes < 1024 * 1024 * 1024:
        return f"{tamano_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{tamano_bytes / (1024 * 1024 * 1024):.2f} GB"


def _escapar_valor_sql(valor) -> str:
    """Escapa de forma segura un valor de Python para su inclusión en una sentencia SQL."""
    if valor is None:
        return "NULL"
    if isinstance(valor, bool):
        return "1" if valor else "0"
    if isinstance(valor, (int, float)):
        return str(valor)
    if isinstance(valor, (datetime, date)):
        return f"'{valor.isoformat()}'"
    if isinstance(valor, (bytes, bytearray)):
        return f"X'{valor.hex()}'"
    
    # Cadenas de texto: escapar barras invertidas, comillas simples y saltos de línea
    s = (
        str(valor)
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\r", "\\r")
        .replace("\n", "\\n")
        .replace("\x00", "\\0")
    )
    return f"'{s}'"


class ServicioBackups:
    """
    Capa de negocio para la generación y gestión de copias de seguridad de la base de datos.
    Genera volcados completos de MySQL en formato comprimido (.sql.gz) al vuelo,
    garantizando 0 consumo de almacenamiento permanente en el servidor.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repositorio_logs = RepositorioLogs(db)

    def generar_volcado_temporal(self, usuario_auth: dict) -> tuple[str, str, int, str]:
        """
        Genera un volcado completo de la base de datos MySQL comprimido con gzip (.sql.gz)
        en un archivo temporal seguro. Registra la acción en la bitácora de auditoría.
        
        Retorna:
            (ruta_temporal, nombre_archivo, tamano_bytes, tamano_formateado)
        """
        conn = None
        temp_file = None
        try:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"recidron_backup_{timestamp_str}.sql.gz"

            temp_file = tempfile.NamedTemporaryFile(suffix=".sql.gz", delete=False)
            ruta_temporal = temp_file.name
            temp_file.close()

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SHOW TABLES")
            tablas = [fila[0] for fila in cursor.fetchall()]

            with gzip.open(ruta_temporal, "wt", encoding="utf-8") as gz:
                gz.write("-- ============================================================\n")
                gz.write("-- Recidron Database Backup (Full Dump)\n")
                gz.write(f"-- Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                gz.write(f"-- Solicitado por: {usuario_auth.get('email', 'Admin')}\n")
                gz.write("-- Sistema: Recidron - Gestión de Residuos (UniCundinamarca)\n")
                gz.write("-- ============================================================\n\n")
                gz.write("SET NAMES utf8mb4;\n")
                gz.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

                for tabla in tablas:
                    # Estructura DDL de la tabla
                    cursor.execute(f"SHOW CREATE TABLE `{tabla}`")
                    resultado_ddl = cursor.fetchone()
                    ddl_sql = resultado_ddl[1] if resultado_ddl else ""

                    gz.write(f"-- Estructura de tabla para `{tabla}`\n")
                    gz.write(f"DROP TABLE IF EXISTS `{tabla}`;\n")
                    gz.write(f"{ddl_sql};\n\n")

                    # Datos DML de la tabla
                    cursor.execute(f"SELECT * FROM `{tabla}`")
                    filas = cursor.fetchall()
                    if filas:
                        cursor.execute(f"SHOW COLUMNS FROM `{tabla}`")
                        columnas = [f"`{col[0]}`" for col in cursor.fetchall()]
                        cols_str = ", ".join(columnas)

                        gz.write(f"-- Volcado de datos para `{tabla}` ({len(filas)} registros)\n")
                        gz.write(f"INSERT INTO `{tabla}` ({cols_str}) VALUES\n")

                        lotes_valores = []
                        for fila in filas:
                            valores_sql = [_escapar_valor_sql(v) for v in fila]
                            lotes_valores.append(f"({', '.join(valores_sql)})")

                        gz.write(",\n".join(lotes_valores))
                        gz.write(";\n\n")

                gz.write("SET FOREIGN_KEY_CHECKS = 1;\n")
                gz.write("-- Fin del respaldo de base de datos Recidron\n")

            tamano_bytes = os.path.getsize(ruta_temporal)
            tamano_formateado = _formatear_tamano(tamano_bytes)

            # Registrar en logs de auditoría
            self.repositorio_logs.registrar(
                usuario_id=usuario_auth.get("id"),
                accion="BACKUP",
                recurso="base_de_datos",
                detalles=f"Generación y descarga de respaldo de base de datos ({nombre_archivo})",
                valor_nuevo={
                    "archivo": nombre_archivo,
                    "tamano_bytes": tamano_bytes,
                    "tamano_formateado": tamano_formateado,
                    "formato": "sql.gz",
                    "total_tablas": len(tablas),
                    "generado_por": usuario_auth.get("email"),
                },
            )

            return ruta_temporal, nombre_archivo, tamano_bytes, tamano_formateado

        except Exception as e:
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.remove(temp_file.name)
                except OSError:
                    pass
            raise HTTPException(
                status_code=500,
                detail=f"Error durante la generación de la copia de seguridad: {str(e)}",
            )
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def obtener_historial(self, limite: int = 50) -> list[dict]:
        """
        Obtiene el historial de respaldos registrados en la tabla de logs de auditoría.
        Retorna la información formateada para alimentar el panel web de Backups.
        """
        logs = (
            self.db.query(AuditLog)
            .filter(AuditLog.accion == "BACKUP")
            .order_by(AuditLog.fecha.desc())
            .limit(limite)
            .all()
        )

        historial = []
        for log in logs:
            datos_nuevos = {}
            if log.valor_nuevo:
                try:
                    datos_nuevos = json.loads(log.valor_nuevo)
                except Exception:
                    datos_nuevos = {}

            nombre_archivo = datos_nuevos.get("archivo")
            if not nombre_archivo:
                fecha_str = log.fecha.strftime("%Y%m%d_%H%M%S") if log.fecha else str(log.id)
                nombre_archivo = f"recidron_backup_{fecha_str}.sql.gz"

            tamano = datos_nuevos.get("tamano_formateado") or "N/A"

            historial.append({
                "id": log.id,
                "fecha": log.fecha.isoformat() if log.fecha else None,
                "usuario_id": log.usuario_id,
                "usuario_nombre": log.usuario.nombre if log.usuario else "Administrador Maestro",
                "usuario_email": log.usuario.email if log.usuario else "admin@recidron.com",
                "archivo": nombre_archivo,
                "tamano": tamano,
                "detalles": log.detalles or "Copia de seguridad de la base de datos",
                "estado": "Completado",
            })

        return historial
