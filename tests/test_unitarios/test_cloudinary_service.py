import pytest
from unittest.mock import patch
from fastapi import HTTPException
from utils.cloudinary_upload import subir_imagen_cloudinary

class TestCloudinaryService:
    """Pruebas unitarias para el servicio de almacenamiento de imágenes en Cloudinary."""

    @patch("cloudinary.uploader.upload")
    def test_subir_imagen_retorna_url_segura(self, mock_upload):
        """Verifica que la subida exitosa retorne la URL segura HTTPS de Cloudinary."""
        expected_url = "https://res.cloudinary.com/recidron/image/upload/v12345/recidron/reportes/evidencia.jpg"
        mock_upload.return_value = {
            "secure_url": expected_url,
            "public_id": "recidron/reportes/evidencia",
            "format": "jpg",
            "bytes": 20480
        }

        imagen_bytes = b"fake-image-binary-content-12345"
        resultado_url = subir_imagen_cloudinary(imagen_bytes)

        assert resultado_url == expected_url
        mock_upload.assert_called_once_with(
            imagen_bytes,
            folder="recidron/reportes"
        )

    @patch("cloudinary.uploader.upload")
    def test_subir_imagen_lanza_http_500_en_caso_de_error(self, mock_upload):
        """Verifica que si la API de Cloudinary falla, se capture la excepción y se lance HTTP 500."""
        mock_upload.side_effect = Exception("Connection timeout / Cloudinary unavailable")

        imagen_bytes = b"fake-image-bytes"
        with pytest.raises(HTTPException) as exc_info:
            subir_imagen_cloudinary(imagen_bytes)

        assert exc_info.value.status_code == 500
        assert "Error al subir la imagen al servidor" in exc_info.value.detail
