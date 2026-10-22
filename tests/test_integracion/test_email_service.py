import pytest
from unittest.mock import AsyncMock, patch
from utils.email import enviar_email_recuperacion, fast_mail, conf
from fastapi_mail import MessageType

class TestEmailService:
    """
    Pruebas de integración para el servicio de envío de correos electrónicos (fastapi-mail).
    Valida la conformación de los mensajes, el contenido del OTP y la configuración SMTP.
    """

    def test_configuracion_smtp_establecida(self):
        """Verifica que los parámetros esenciales de configuración SMTP estén definidos."""
        assert conf.MAIL_SERVER is not None
        assert conf.MAIL_PORT in [465, 587, 25, 2525]
        assert conf.MAIL_FROM is not None
        assert conf.MAIL_FROM_NAME in ["Recidron", "Soporte Recidron"]

    @pytest.mark.anyio
    async def test_envio_email_recuperacion_construye_mensaje_correcto(self):
        """Verifica que enviar_email_recuperacion arma el mensaje con el destinatario y código OTP correctos."""
        email_test = "usuario_prueba@recidron.com"
        codigo_otp = "849201"

        with patch.object(fast_mail, "send_message", new_callable=AsyncMock) as mock_send:
            await enviar_email_recuperacion(email_destino=email_test, codigo=codigo_otp)

            mock_send.assert_awaited_once()
            mensaje_enviado = mock_send.call_args[0][0]

            # Verificación del destinatario y asunto
            destinatarios = [r if isinstance(r, str) else r.email for r in mensaje_enviado.recipients]
            assert email_test in destinatarios
            assert mensaje_enviado.subject == "Tu Código de Recuperación de Contraseña"
            assert mensaje_enviado.subtype == MessageType.html

            # Verificación del contenido de la plantilla HTML
            assert codigo_otp in mensaje_enviado.body
            assert "Recuperación de Contraseña - Recidron" in mensaje_enviado.body
            assert "Este código expirará en 15 minutos" in mensaje_enviado.body

    @pytest.mark.anyio
    async def test_envio_email_falla_si_servicio_smtp_cae(self):
        """Verifica que cualquier fallo en el transporte SMTP se propague adecuadamente."""
        email_test = "falla@recidron.com"
        codigo_otp = "999999"

        with patch.object(fast_mail, "send_message", new_callable=AsyncMock, side_effect=ConnectionError("Error SMTP")):
            with pytest.raises(ConnectionError) as exc_info:
                await enviar_email_recuperacion(email_destino=email_test, codigo=codigo_otp)

            assert "Error SMTP" in str(exc_info.value)
