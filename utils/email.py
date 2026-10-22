import os
import resend
from dotenv import load_dotenv

load_dotenv()

# Configurar API Key de Resend
resend.api_key = os.getenv("RESEND_API_KEY", "")

# Remitente configurado (usa onboarding@resend.dev en sandbox/desarrollo por defecto o dominio verificado)
DEFAULT_FROM = os.getenv("MAIL_FROM", "Recidron <onboarding@resend.dev>")


async def enviar_email_recuperacion(email_destino: str, codigo: str) -> dict:
    """
    Envía el código de recuperación (OTP) al usuario por correo electrónico mediante la API de Resend.
    """
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2>Recuperación de Contraseña - Recidron</h2>
            <p>Hola,</p>
            <p>Has solicitado restablecer tu contraseña. Ingresa el siguiente código temporal en la aplicación:</p>
            <div style="background-color: #f4f4f4; padding: 15px; border-radius: 8px; display: inline-block; margin: 20px 0;">
                <h1 style="margin: 0; color: #1e3a8a; letter-spacing: 5px;">{codigo}</h1>
            </div>
            <p><strong>Nota:</strong> Este código expirará en 15 minutos por seguridad.</p>
            <p>Si no fuiste tú quien solicitó este cambio, puedes ignorar este correo.</p>
            <br>
            <p>Saludos,<br>Equipo Recidron</p>
        </body>
    </html>
    """

    params: resend.Emails.SendParams = {
        "from": DEFAULT_FROM,
        "to": [email_destino],
        "subject": "Tu Código de Recuperación de Contraseña",
        "html": html,
    }

    try:
        response = resend.Emails.send(params)
        return response
    except Exception as e:
        print(f"Error enviando correo con Resend a {email_destino}: {e}")
        raise
