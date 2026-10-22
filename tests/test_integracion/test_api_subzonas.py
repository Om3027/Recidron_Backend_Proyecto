import pytest
from main import app
from routes.auth import obtener_usuario_actual

class TestApiSubzonas:
    """
    Pruebas de integración para los endpoints de la API de Subzonas y Tipos de Subzona (/subzonas, /tipos-subzona).
    """

    def test_listar_subzonas_sin_token_retorna_401(self, client):
        """Verifica que solicitar /subzonas sin header de autenticación retorne 401."""
        response = client.get("/subzonas")
        assert response.status_code == 401
        assert "Token no proporcionado" in response.json().get("detail", "")

    def test_listar_tipos_subzona_autenticado_retorna_200(self, client):
        """Verifica que /tipos-subzona retorne el catálogo precargado de tipos (Aula, Laboratorio, etc.)."""
        # Rol 3 es 'admin' en la base de datos (posee permiso reportes:leer)
        usuario_mock = {"id": 1, "nombre": "Admin Test", "rol_id": 3, "email": "admin@recidron.com"}

        app.dependency_overrides[obtener_usuario_actual] = lambda: usuario_mock
        try:
            response = client.get("/tipos-subzona")
            assert response.status_code == 200
            tipos = response.json()
            assert isinstance(tipos, list)
            assert len(tipos) > 0

            nombres_tipos = [t["nombre_tipo"] for t in tipos]
            assert "Aula" in nombres_tipos
            assert "Laboratorio" in nombres_tipos
        finally:
            app.dependency_overrides.clear()

    def test_listar_subzonas_filtradas_por_zona(self, client):
        """Verifica que /subzonas soporte filtrado por edificio/zona_id."""
        usuario_mock = {"id": 1, "nombre": "Admin Test", "rol_id": 3, "email": "admin@recidron.com"}
        app.dependency_overrides[obtener_usuario_actual] = lambda: usuario_mock

        try:
            response = client.get("/subzonas?zona_id=1")
            assert response.status_code == 200
            subzonas = response.json()
            assert isinstance(subzonas, list)
            for sub in subzonas:
                assert sub["zona_id"] == 1
        finally:
            app.dependency_overrides.clear()

    def test_obtener_subzona_inexistente_retorna_404(self, client):
        """Verifica que consultar un ID inexistente retorne 404."""
        usuario_mock = {"id": 1, "nombre": "Admin Test", "rol_id": 3, "email": "admin@recidron.com"}
        app.dependency_overrides[obtener_usuario_actual] = lambda: usuario_mock

        try:
            response = client.get("/subzonas/999999")
            assert response.status_code == 404
            assert "no encontrada" in response.json().get("detail", "").lower()
        finally:
            app.dependency_overrides.clear()
