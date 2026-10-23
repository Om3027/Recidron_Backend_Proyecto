import gzip
import os
import tempfile
import pytest
from unittest.mock import patch
from main import app
from routes.auth import obtener_usuario_actual
from servicios.servicio_backups import ServicioBackups


class TestApiBackups:
    """
    Pruebas de integración para los endpoints de Copias de Seguridad (/admin/backups/).
    """

    def test_descargar_backup_sin_token_retorna_401(self, client):
        """Verifica que solicitar /admin/backups/descargar sin token retorne 401."""
        response = client.get("/admin/backups/descargar")
        assert response.status_code == 401
        assert "Token no proporcionado" in response.json().get("detail", "")

    def test_descargar_backup_usuario_no_admin_retorna_403(self, client):
        """Verifica que un usuario estándar (rol autor) reciba 403."""
        usuario_mock = {
            "id": 2,
            "nombre": "Estudiante Prueba",
            "rol_id": 2,
            "nombre_rol": "autor",
            "email": "estudiante@ucundinamarca.edu.co",
        }
        app.dependency_overrides[obtener_usuario_actual] = lambda: usuario_mock

        try:
            response = client.get("/admin/backups/descargar")
            assert response.status_code == 403
            assert "Administrador Maestro" in response.json().get("detail", "")
        finally:
            app.dependency_overrides.pop(obtener_usuario_actual, None)

    def test_descargar_backup_admin_secundario_retorna_403(self, client):
        """Verifica que un admin cuyo correo NO sea el de super admin reciba 403."""
        admin_secundario = {
            "id": 5,
            "nombre": "Admin Secundario",
            "rol_id": 1,
            "nombre_rol": "admin",
            "email": "otro_admin@recidron.com",
        }
        app.dependency_overrides[obtener_usuario_actual] = lambda: admin_secundario

        try:
            response = client.get("/admin/backups/descargar")
            assert response.status_code == 403
            assert "Administrador Maestro" in response.json().get("detail", "")
        finally:
            app.dependency_overrides.pop(obtener_usuario_actual, None)

    def test_descargar_backup_super_admin_exitoso(self, client):
        """Verifica que el Super Administrador reciba el archivo comprimido .sql.gz."""
        super_admin = {
            "id": 1,
            "nombre": "Admin Maestro",
            "rol_id": 1,
            "nombre_rol": "admin",
            "email": "admin@recidron.com",
        }
        app.dependency_overrides[obtener_usuario_actual] = lambda: super_admin

        with tempfile.NamedTemporaryFile(suffix=".sql.gz", delete=False) as tf:
            temp_path = tf.name

        with gzip.open(temp_path, "wt", encoding="utf-8") as gz:
            gz.write("-- Mock dump\n")

        with patch.object(
            ServicioBackups,
            "generar_volcado_temporal",
            return_value=(temp_path, "recidron_backup_mock.sql.gz", 50, "50 B"),
        ):
            try:
                response = client.get("/admin/backups/descargar")
                assert response.status_code == 200
                assert response.headers.get("content-type") == "application/gzip"
                assert "recidron_backup_mock.sql.gz" in response.headers.get("content-disposition", "")
            finally:
                app.dependency_overrides.pop(obtener_usuario_actual, None)

    def test_historial_backups_sin_token_retorna_401(self, client):
        """Verifica que solicitar /admin/backups/historial sin token retorne 401."""
        response = client.get("/admin/backups/historial")
        assert response.status_code == 401

    def test_historial_backups_super_admin_retorna_lista(self, client):
        """Verifica que el Super Administrador pueda consultar la lista de eventos de backup."""
        super_admin = {
            "id": 1,
            "nombre": "Admin Maestro",
            "rol_id": 1,
            "nombre_rol": "admin",
            "email": "admin@recidron.com",
        }
        app.dependency_overrides[obtener_usuario_actual] = lambda: super_admin

        mock_historial = [
            {
                "id": 1,
                "fecha": "2026-10-22T19:00:00",
                "usuario_id": 1,
                "usuario_nombre": "Admin Maestro",
                "usuario_email": "admin@recidron.com",
                "archivo": "recidron_backup_20261022_190000.sql.gz",
                "tamano": "2.5 MB",
                "detalles": "Generación de respaldo",
                "estado": "Completado",
            }
        ]

        with patch.object(ServicioBackups, "obtener_historial", return_value=mock_historial):
            try:
                response = client.get("/admin/backups/historial")
                assert response.status_code == 200
                data = response.json()
                assert isinstance(data, list)
                assert len(data) == 1
                assert data[0]["archivo"] == "recidron_backup_20261022_190000.sql.gz"
                assert data[0]["estado"] == "Completado"
            finally:
                app.dependency_overrides.pop(obtener_usuario_actual, None)
