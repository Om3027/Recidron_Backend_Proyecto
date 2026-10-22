import pytest
from unittest.mock import patch
import cloudinary
from fastapi import HTTPException
from utils.cloudinary_upload import subir_imagen_cloudinary

class TestCloudinaryIntegration:
    """
    Pruebas de integración para el servicio de almacenamiento multimedia en Cloudinary.
    Valida la configuración del cliente y el flujo de subida de imágenes.
    """

    def test_configuracion_cloudinary_activa(self):
        """Verifica que el cliente de Cloudinary tenga las credenciales y el flag seguro habilitado."""
        config = cloudinary.config()
        assert config.secure is True
        assert config.cloud_name is not None

    def test_subir_imagen_valida_directorio_de_destino(self):
        """Verifica que el archivo se envíe a la carpeta designada 'recidron/reportes'."""
        bytes_simulados = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        url_esperada = "https://res.cloudinary.com/recidron/image/upload/v1/recidron/reportes/test.png"

        with patch("cloudinary.uploader.upload") as mock_upload:
            mock_upload.return_value = {
                "secure_url": url_esperada,
                "public_id": "recidron/reportes/test",
                "format": "png",
                "bytes": len(bytes_simulados)
            }

            url_resultado = subir_imagen_cloudinary(bytes_simulados)

            assert url_resultado == url_esperada
            mock_upload.assert_called_once_with(
                bytes_simulados,
                folder="recidron/reportes"
            )

    def test_subir_imagen_maneja_error_y_lanza_http_500(self):
        """Verifica que ante un fallo de conexión o cuota de Cloudinary, se capture y lance HTTP 500."""
        bytes_simulados = b"datos_corruptos"

        with patch("cloudinary.uploader.upload", side_effect=Exception("Error de conexión con Cloudinary")):
            with pytest.raises(HTTPException) as exc_info:
                subir_imagen_cloudinary(bytes_simulados)

            assert exc_info.value.status_code == 500
            assert "Error al subir la imagen" in exc_info.value.detail
