
# Este archivo ensambla todo el proyecto:
#   1. Crea la app FastAPI
#   2. Crea las tablas al arrancar
#   3. Registra todas las rutas
#
# Instalar los requerimientos primero 
#   pip install -r requirements.txt     
#
# Para correrlo:
#   uvicorn main:app --reload --port=3000
#
# Swagger disponible en:
#   http://localhost:3000/docs


from fastapi import FastAPI
from models import init_db
from routes import (
    router_roles, router_usuarios, router_sesiones, router_logs,
    router_tipos, router_materiales, router_zonas, router_tamanos,
    router_reportes, router_geos
)


# Crear la app con título y descripción para el Swagger

app = FastAPI(
    title=" API Recidron",
    description="""
    Backend de **Recidron App** — Sistema de reporte y gestión de residuos sólidos.
    Universidad de Cundinamarca, Seccional Girardot.

    ### Tablas de Seguridad Informática
    - **Roles** — Tipos de usuario
    - **Usuarios** — Personas que usan la app
    - **Sesiones** — Control de acceso por token
    - **Logs Auditoría** — Registro de acciones del sistema

    ### Tablas del PGC — Recidron App
    - **Tipos de Residuo** — Clasificación del residuo
    - **Materiales** — Material del residuo
    - **Zonas del Campus** — Ubicación en la universidad
    - **Tamaños** — Tamaño estimado del residuo
    - **Reportes** — Reportes de residuos
    - **Geolocalizaciones** — Coordenadas GPS
    """,
    version="1.0.0",
)


# Crear tablas al arrancar

@app.on_event("startup")
def startup():
    init_db()


# Ruta raíz — solo para verificar que la API funciona

@app.get("/", tags=["Estado"])
def root():
    """Verifica que la API está funcionando correctamente."""
    return {
        "mensaje": " Recidron API funcionando",
        "swagger": "http://localhost:3000/docs",
        "tablas": 10,
        "rutas": 50
    }


# Registrar todos los routers (grupos de rutas)

# Seguridad Informática
app.include_router(router_roles)
app.include_router(router_usuarios)
app.include_router(router_sesiones)
app.include_router(router_logs)

# PGC — Recidron App
app.include_router(router_tipos)
app.include_router(router_materiales)
app.include_router(router_zonas)
app.include_router(router_tamanos)
app.include_router(router_reportes)
app.include_router(router_geos)