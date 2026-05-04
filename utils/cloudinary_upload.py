import os
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

# Configuración de Cloudinary usando variables de entorno
cloudinary.config( 
  cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
  api_key = os.getenv("CLOUDINARY_API_KEY"), 
  api_secret = os.getenv("CLOUDINARY_API_SECRET"),
  secure = True
)

def subir_imagen_cloudinary(archivo_bytes: bytes) -> str:
    """
    Sube una imagen en bytes a Cloudinary y retorna la URL segura.
    Organiza los archivos en la carpeta 'recidron/reportes'.
    """
    try:
        # Subir el archivo usando los bytes en memoria
        response = cloudinary.uploader.upload(
            archivo_bytes,
            folder="recidron/reportes"
        )
        # Retorna la URL segura (https)
        return response.get("secure_url")
    except Exception as e:
        print(f"Error subiendo a Cloudinary: {e}")
        raise HTTPException(status_code=500, detail="Error al subir la imagen al servidor.")
