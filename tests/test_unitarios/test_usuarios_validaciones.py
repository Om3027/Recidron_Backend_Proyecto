import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from servicios.servicio_usuarios import ServicioUsuarios

class TestUsuariosValidaciones:
    """Pruebas unitarias para las reglas de negocio y validaciones de ServicioUsuarios."""

    @pytest.fixture
    def servicio_mock(self):
        """Instancia ServicioUsuarios con sesión y repositorios simulados."""
        db_mock = MagicMock()
        servicio = ServicioUsuarios(db_mock)
        servicio.repositorio_usuarios = MagicMock()
        servicio.repositorio_roles = MagicMock()
        servicio.repositorio_logs = MagicMock()
        return servicio

    def test_cambio_password_rechaza_si_falta_confirmacion(self, servicio_mock):
        """Debe fallar con 422 si se envía nueva_password sin confirmar_password."""
        servicio_mock.repositorio_usuarios.obtener_activo_por_id.return_value = MagicMock(id=1)
        
        datos = {"nueva_password": "PasswordSeguro123"}
        with pytest.raises(HTTPException) as exc_info:
            servicio_mock.actualizar_perfil_propio(usuario_id=1, datos=datos)

        assert exc_info.value.status_code == 422
        assert "Debes enviar nueva_password y confirmar_password juntos" in exc_info.value.detail

    def test_cambio_password_rechaza_si_no_coinciden(self, servicio_mock):
        """Debe fallar con 422 si nueva_password y confirmar_password son diferentes."""
        servicio_mock.repositorio_usuarios.obtener_activo_por_id.return_value = MagicMock(id=1)
        
        datos = {
            "nueva_password": "PasswordUno123",
            "confirmar_password": "PasswordDos123"
        }
        with pytest.raises(HTTPException) as exc_info:
            servicio_mock.actualizar_perfil_propio(usuario_id=1, datos=datos)

        assert exc_info.value.status_code == 422
        assert "Las contraseñas no coinciden" in exc_info.value.detail

    def test_cambio_password_rechaza_longitud_menor_a_8(self, servicio_mock):
        """Debe fallar con 422 si la contraseña tiene menos de 8 caracteres."""
        servicio_mock.repositorio_usuarios.obtener_activo_por_id.return_value = MagicMock(id=1)
        
        datos = {
            "nueva_password": "12345",
            "confirmar_password": "12345"
        }
        with pytest.raises(HTTPException) as exc_info:
            servicio_mock.actualizar_perfil_propio(usuario_id=1, datos=datos)

        assert exc_info.value.status_code == 422
        assert "al menos 8 caracteres" in exc_info.value.detail

    def test_cambio_password_exitoso_cuando_cumple_todas_las_reglas(self, servicio_mock):
        """Debe pasar y llamar a actualizar cuando cumple longitud y coincidencia."""
        mock_user = MagicMock(id=1, nombre="Test User", email="test@recidron.com", codigo_estudiantil="123")
        servicio_mock.repositorio_usuarios.obtener_activo_por_id.return_value = mock_user

        datos = {
            "nueva_password": "PasswordSeguro123",
            "confirmar_password": "PasswordSeguro123"
        }
        res = servicio_mock.actualizar_perfil_propio(usuario_id=1, datos=datos)

        assert res["mensaje"] == "Perfil actualizado correctamente"
        servicio_mock.repositorio_usuarios.actualizar.assert_called_once()

    def test_bloqueo_auto_desactivacion_cuenta_propia(self, servicio_mock):
        """Debe fallar con 400 si un usuario autenticado intenta desactivar su propia cuenta."""
        mock_admin = MagicMock(id=5, email="admin_secundario@recidron.com")
        servicio_mock.repositorio_usuarios.obtener_activo_por_id.return_value = mock_admin
        servicio_mock.repositorio_usuarios.obtener_por_id.return_value = mock_admin

        datos = {"es_activo": False}
        with pytest.raises(HTTPException) as exc_info:
            # usuario_id == auth_usuario_id (5 == 5)
            servicio_mock.actualizar(usuario_id=5, datos=datos, auth_usuario_id=5)

        assert exc_info.value.status_code == 400
        assert "No puedes desactivar tu propia cuenta" in exc_info.value.detail
