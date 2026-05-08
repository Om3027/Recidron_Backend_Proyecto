import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from dotenv import load_dotenv

load_dotenv()

# Configuración de fastapi-mail
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM=os.getenv("MAIL_FROM", os.getenv("MAIL_USERNAME", "")),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "Recidron"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True").lower() in ("true", "1", "yes"),
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False").lower() in ("true", "1", "yes"),
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fast_mail = FastMail(conf)

async def enviar_correo_recuperacion(email_destino: str, token: str):
    """
    Genera y envía el correo con el Deep Link para recuperación de contraseña.
    Se ejecuta de forma asíncrona (se recomienda usar BackgroundTasks).
    """
    scheme = os.getenv("DEEP_LINK_SCHEME", "recidron://reset-password")
    link = f"{scheme}?token={token}"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                <h2 style="color: #2E7D32; text-align: center;">Recuperación de Contraseña</h2>
                <p>Hola,</p>
                <p>Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en <strong>Recidron</strong>.</p>
                <p>Por favor, haz clic en el siguiente botón para continuar (el enlace se abrirá directamente en la aplicación si la tienes instalada):</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{link}" style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">
                        Restablecer Contraseña
                    </a>
                </div>
                <p><em>Por tu seguridad, este enlace expirará en 15 minutos. Si no fuiste tú quien solicitó esto, puedes ignorar este correo.</em></p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
                <p style="font-size: 12px; color: #777;">
                    Si el botón no funciona, intenta copiar y pegar este enlace en tu navegador:<br>
                    <a href="{link}" style="color: #2E7D32;">{link}</a>
                </p>
            </div>
        </body>
    </html>
    """
    
    message = MessageSchema(
        subject="Recuperación de Contraseña - Recidron",
        recipients=[email_destino],
        body=html_content,
        subtype=MessageType.html
    )
    
    # Enviar el mensaje
    await fast_mail.send_message(message)
