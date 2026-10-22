import pytest
from main import app
from routes.auth import obtener_usuario_actual

class TestApiReportes:
    """
    Pruebas de integración para los endpoints de la API de Reportes (/reportes/).
    """

    def test_listar_reportes_sin_token_retorna_401(self, client):
        """Verifica que solicitar /reportes/ sin header de autenticación retorne 401."""
        response = client.get("/reportes/")
        assert response.status_code == 401
        assert "Token no proporcionado" in response.json().get("detail", "")

    def test_listar_reportes_autenticado_retorna_200(self, client):
        """Verifica que un usuario con permiso reportes:leer obtenga la lista de reportes activos."""
        usuario_mock = {"id": 1, "nombre": "Admin Test", "rol_id": 3, "email": "admin@recidron.com"}
        app.dependency_overrides[obtener_usuario_actual] = lambda: usuario_mock

        try:
            response = client.get("/reportes/?limit=5")
            assert response.status_code == 200
            reportes = response.json()
            assert isinstance(reportes, list)
            if len(reportes) > 0:
                reporte = reportes[0]
                assert "id" in reporte
                assert "descripcion" in reporte
                assert "zona_id" in reporte
        finally:
            app.dependency_overrides.clear()

    def test_obtener_reporte_inexistente_retorna_404(self, client):
        """Verifica que solicitar un ID de reporte que no existe retorne 404."""
        usuario_mock = {"id": 1, "nombre": "Admin Test", "rol_id": 3, "email": "admin@recidron.com"}
        app.dependency_overrides[obtener_usuario_actual] = lambda: usuario_mock

        try:
            response = client.get("/reportes/999999")
            assert response.status_code == 404
            assert "no encontrado" in response.json().get("detail", "").lower()
        finally:
            app.dependency_overrides.clear()

    def test_mis_estadisticas_retorna_200(self, client):
        """Verifica que /reportes/stats/my retorne el balance métrico del usuario autenticado."""
        usuario_mock = {"id": 1, "nombre": "Admin Test", "rol_id": 3, "email": "admin@recidron.com"}
        app.dependency_overrides[obtener_usuario_actual] = lambda: usuario_mock

        try:
            response = client.get("/reportes/stats/my")
            assert response.status_code == 200
            stats = response.json()
            assert "stats" in stats
            assert isinstance(stats["stats"], list)
            assert any(item.get("title") == "Mis Reportes" for item in stats["stats"])
        finally:
            app.dependency_overrides.clear()
