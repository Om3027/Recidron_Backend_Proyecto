import pytest
from unittest.mock import patch
import resend
from utils.email import enviar_email_recuperacion, DEFAULT_FROM

class TestEmailService:
    """
    Pruebas de integración para el servicio de envío de correos electrónicos transaccionales con Resend API.
    Valida la conformación del payload, el contenido del OTP y la gestión de excepciones de la API.
    """

    def test_configuracion_resend_establecida(self):
        """Verifica que el remitente por defecto y la configuración de Resend estén definidos."""
        assert DEFAULT_FROM is not None
        assert len(DEFAULT_FROM) > 0
        assert hasattr(resend, "api_key")

    @pytest.mark.anyio
    async def test_envio_email_recuperacion_construye_payload_resend_correcto(self):
        """Verifica que enviar_email_recuperacion envíe los parámetros adecuados a resend.Emails.send."""
        email_test = "usuario_prueba@recidron.com"
        codigo_otp = "849201"

        with patch("resend.Emails.send") as mock_send:
            mock_send.return_value = {"id": "resend_msg_12345"}

            res = await enviar_email_recuperacion(email_destino=email_test, codigo=codigo_otp)

            mock_send.assert_called_once()
            params = mock_send.call_args[0][0]

            # Verificación del destinatario, remitente y asunto
            assert params["to"] == [email_test]
            assert params["subject"] == "Tu Código de Recuperación de Contraseña"
            assert params["from"] == DEFAULT_FROM

            # Verificación del contenido de la plantilla HTML
            assert codigo_otp in params["html"]
            assert "Recuperación de Contraseña - Recidron" in params["html"]
            assert "Este código expirará en 15 minutos" in params["html"]

            # Verificación de respuesta
            assert res["id"] == "resend_msg_12345"

    @pytest.mark.anyio
    async def test_envio_email_falla_si_api_resend_arroja_error(self):
        """Verifica que cualquier fallo en la llamada a Resend API se propague adecuadamente."""
        email_test = "falla@recidron.com"
        codigo_otp = "999999"

        with patch("resend.Emails.send", side_effect=Exception("Resend API Key Invalid")):
            with pytest.raises(Exception) as exc_info:
                await enviar_email_recuperacion(email_destino=email_test, codigo=codigo_otp)

            assert "Resend API Key Invalid" in str(exc_info.value)
