#  Recidron App - Backend

Backend de **Recidron App** — Sistema de reporte y gestión de residuos sólidos desarrollado para la **Universidad de Cundinamarca, Seccional Girardot**.

##  Tecnologías

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Servidor ASGI:** Uvicorn
- **Validación de Datos:** Pydantic
- **Base de Datos:** SQLite (`recidron.db`)


##  Estructura del Proyecto

El sistema está dividido en dos grandes módulos, cada uno conformado por diferentes modelos y rutas:

###  Seguridad Informática
Gestiona el acceso y la trazabilidad de los usuarios en el sistema:
- **Roles:** Niveles de acceso y permisos.
- **Usuarios:** Personas registradas que usan la aplicación.
- **Sesiones:** Control de accesos y tiempo de sesión activa.
- **Logs Auditoría:** Registro de acciones y eventos realizados dentro del sistema.

###  PGC — Recidron App
Contiene las entidades principales para el control y reporte y gestión de residuos:
- **Tipos de Residuo:** Clasificación técnica de los residuos.
- **Materiales:** Tipos de materiales (plástico, papel, cartón, orgánico, etc.).
- **Zonas del Campus:** Diferentes ubicaciones dentro de la universidad.
- **Tamaños:** Estimación del volumen o tamaño del residuo.
- **Reportes:** Registro detallado de incidentes o hallazgos.
- **Geolocalizaciones:** Coordenadas de los reportes en el mapa.

##  Instalación y Configuración

Sigue estos pasos para levantar un entorno de desarrollo en tu máquina local:

1. **Clona o descarga el proyecto** y navega a la carpeta principal:
   ```bash
   cd Backend_Recidron
   ```

2. **Crea y activa un entorno virtual (opcional pero recomendado):**
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En macOS/Linux:
   source .venv/bin/activate
   ```

3. **Instala las dependencias del proyecto:**
   ```bash
   pip install -r requirements.txt
   ```

##  Ejecución del Servidor Local

Para iniciar el servidor de desarrollo, ejecuta el siguiente comando:

```bash
uvicorn main:app --reload --port=3000
```
> *Nota: El parámetro `--reload` hará que el servidor se reinicie automáticamente cada vez que modifiques código.*

##  Documentación Interactiva de la API

FastAPI genera automáticamente documentación interactiva basada en los estándares OpenAPI. Una vez el servidor esté corriendo, puedes explorar y realizar peticiones de prueba a través de tu navegador:

- **Swagger UI:** [http://localhost:3000/docs](http://localhost:3000/docs)
- **ReDoc (Documentación estática):** [http://localhost:3000/redoc](http://localhost:3000/redoc)

---
*Desarrollado para la Universidad de Cundinamarca, Seccional Girardot.*
