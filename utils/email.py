import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from dotenv import load_dotenv

load_dotenv()

# Configuración de conexión para fastapi-mail
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM=os.getenv("MAIL_FROM", ""),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "Soporte Recidron"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True") == "True",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False") == "True",
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fast_mail = FastMail(conf)

async def enviar_email_recuperacion(email_destino: str, codigo: str):
    """
    Envía el código de recuperación (OTP) al usuario por correo electrónico.
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

    message = MessageSchema(
        subject="Tu Código de Recuperación de Contraseña",
        recipients=[email_destino],
        body=html,
        subtype=MessageType.html
    )

    await fast_mail.send_message(message)
