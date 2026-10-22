import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from servicios.servicio_reportes import ServicioReportes

class TestReportesSubzonasValidacion:
    """Pruebas unitarias para las reglas de integridad de Reporte y Subzona."""

    @pytest.fixture
    def servicio_mock(self):
        """Instancia ServicioReportes con dependencias simuladas."""
        db_mock = MagicMock()
        servicio = ServicioReportes(db_mock)
        servicio.repositorio_reportes = MagicMock()
        servicio.repositorio_usuarios = MagicMock()
        servicio.repositorio_tipos = MagicMock()
        servicio.repositorio_mats = MagicMock()
        servicio.repositorio_zonas = MagicMock()
        servicio.repositorio_subzonas = MagicMock()
        servicio.repositorio_tamanos = MagicMock()
        servicio.repositorio_logs = MagicMock()
        servicio.repositorio_fotos = MagicMock()
        servicio.repositorio_geos = MagicMock()
        return servicio

    def test_reporte_rechaza_subzona_que_no_pertenece_a_la_zona_seleccionada(self, servicio_mock):
        """Debe fallar con 400 si la subzona seleccionada no corresponde al edificio del reporte."""
        # Configurar mocks de entidades existentes
        servicio_mock.repositorio_usuarios.obtener_activo_por_id.return_value = MagicMock(id=1)
        servicio_mock.repositorio_tipos.obtener_activo_por_id.return_value = MagicMock(id=1)
        servicio_mock.repositorio_mats.obtener_activo_por_id.return_value = MagicMock(id=1)
        servicio_mock.repositorio_zonas.obtener_activa_por_id.return_value = MagicMock(id=1) # Zona 1 (ej: Edificio Académico)
        servicio_mock.repositorio_tamanos.obtener_activo_por_id.return_value = MagicMock(id=1)

        # Subzona 10 pertenece a la Zona 2 (ej: Bloque de Enfermería), NO a la Zona 1
        subzona_incongruente = MagicMock(id=10, nombre_subzona="Laboratorio Piso 2", zona_id=2)
        servicio_mock.repositorio_subzonas.obtener_activa_por_id.return_value = subzona_incongruente

        datos_reporte = {
            "usuario_id": 1,
            "tipo_residuo_id": 1,
            "material_id": 1,
            "zona_id": 1,       # Se envía Zona 1
            "subzona_id": 10,   # Pero la subzona pertenece a Zona 2
            "tamano_id": 1,
            "descripcion": "Residuo junto a la puerta",
        }

        with pytest.raises(HTTPException) as exc_info:
            servicio_mock.crear(datos=datos_reporte, usuario_id=1)

        assert exc_info.value.status_code == 400
        assert "no pertenece a la zona seleccionada" in exc_info.value.detail

    def test_reporte_acepta_subzona_coherente_con_la_zona(self, servicio_mock):
        """Debe permitir el registro si la subzona sí pertenece a la zona seleccionada."""
        servicio_mock.repositorio_usuarios.obtener_activo_por_id.return_value = MagicMock(id=1)
        servicio_mock.repositorio_tipos.obtener_activo_por_id.return_value = MagicMock(id=1)
        servicio_mock.repositorio_mats.obtener_activo_por_id.return_value = MagicMock(id=1)
        servicio_mock.repositorio_zonas.obtener_activa_por_id.return_value = MagicMock(id=1)
        servicio_mock.repositorio_tamanos.obtener_activo_por_id.return_value = MagicMock(id=1)

        # Subzona pertenece a Zona 1
        subzona_valida = MagicMock(
            id=5,
            nombre_subzona="Aula 204",
            piso="2",
            zona_id=1,
            tipo_subzona=MagicMock(nombre_tipo="Aula")
        )
        servicio_mock.repositorio_subzonas.obtener_activa_por_id.return_value = subzona_valida

        # Mock de creación del reporte
        mock_reporte_creado = MagicMock(
            id=100,
            usuario_id=1,
            tipo_residuo_id=1,
            material_id=1,
            zona_id=1,
            subzona_id=5,
            tamano_id=1,
            descripcion="Papel en Aula 204",
            fecha_reporte="2026-10-21 10:00:00",
            usuario=MagicMock(nombre="Estudiante Test"),
            tipo_residuo=MagicMock(nombre_tipo="Aprovechable"),
            material=MagicMock(nombre_material="Plástico"),
            zona=MagicMock(nombre_zona="Edificio Académico"),
            subzona=subzona_valida,
            tamano=MagicMock(nombre_tamano="Mediano"),
            foto=None,
            geolocalizacion=None
        )
        servicio_mock.repositorio_reportes.crear.return_value = mock_reporte_creado
        servicio_mock.repositorio_reportes.obtener_activo_por_id.return_value = mock_reporte_creado

        datos_reporte = {
            "usuario_id": 1,
            "tipo_residuo_id": 1,
            "material_id": 1,
            "zona_id": 1,
            "subzona_id": 5,
            "tamano_id": 1,
            "descripcion": "Papel en Aula 204",
        }

        res = servicio_mock.crear(datos=datos_reporte, usuario_id=1)
        assert res["id"] == 100
        assert res["subzona_id"] == 5
        servicio_mock.repositorio_reportes.crear.assert_called_once()

        # Verificar formateo detallado con subzona vía obtener_por_id
        reporte_detallado = servicio_mock.obtener_por_id(100)
        assert reporte_detallado["subzona"]["nombre_subzona"] == "Aula 204"
        assert reporte_detallado["subzona"]["piso"] == "2"

    def test_reporte_rechaza_zona_inexistente(self, servicio_mock):
        """Debe fallar con 404 si la zona no existe en la base de datos."""
        servicio_mock.repositorio_usuarios.obtener_activo_por_id.return_value = MagicMock(id=1)
        servicio_mock.repositorio_tipos.obtener_activo_por_id.return_value = MagicMock(id=1)
        servicio_mock.repositorio_mats.obtener_activo_por_id.return_value = MagicMock(id=1)
        servicio_mock.repositorio_zonas.obtener_activa_por_id.return_value = None # Zona no encontrada
        servicio_mock.repositorio_tamanos.obtener_activo_por_id.return_value = MagicMock(id=1)

        datos = {
            "usuario_id": 1, "tipo_residuo_id": 1, "material_id": 1,
            "zona_id": 999, "tamano_id": 1
        }
        with pytest.raises(HTTPException) as exc_info:
            servicio_mock.crear(datos=datos, usuario_id=1)

        assert exc_info.value.status_code == 404
        assert "Zona con id 999 no existe" in exc_info.value.detail
