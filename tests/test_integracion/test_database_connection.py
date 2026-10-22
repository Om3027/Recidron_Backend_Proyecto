import pytest
from sqlalchemy import text, inspect
from models.database import engine, SessionLocal, get_connection
from models import Role

class TestDatabaseConnection:
    """
    Pruebas de integración para la conexión con la base de datos MySQL (Aiven Cloud)
    y la integridad del esquema relacional.
    """

    def test_conexion_activa_y_ping(self):
        """Verifica que el motor de SQLAlchemy conecta exitosamente y ejecuta un ping."""
        with engine.connect() as conn:
            resultado = conn.execute(text("SELECT 1")).scalar()
            assert resultado == 1

    def test_driver_mysql_connector_directo(self):
        """Verifica que la función get_connection() con mysql.connector abre y cierra sesión."""
        conn = get_connection()
        try:
            assert conn.is_connected() is True
            cursor = conn.cursor()
            cursor.execute("SELECT 1 + 1")
            (suma,) = cursor.fetchone()
            assert suma == 2
        finally:
            conn.close()

    def test_esquema_tablas_principales_existen(self):
        """Verifica que todas las tablas esenciales del modelo relacional existan."""
        inspector = inspect(engine)
        tablas_existentes = set(inspector.get_table_names())

        tablas_requeridas = {
            "usuarios",
            "roles",
            "permisos",
            "reportes",
            "zonas_campus",
            "subzonas_campus",
            "tipos_subzona",
            "tipos_residuo",
            "materiales",
            "tamanos",
            "fotos_reporte",
            "geolocalizaciones",
            "logs_auditoria",
            "recuperacion_passwords",
            "sesiones"
        }

        tablas_faltantes = tablas_requeridas - tablas_existentes
        assert not tablas_faltantes, f"Faltan tablas requeridas en la base de datos: {tablas_faltantes}"

    def test_columnas_subzonas_campus(self):
        """Verifica que la tabla subzonas_campus contenga las columnas correctas."""
        inspector = inspect(engine)
        columnas = {col["name"] for col in inspector.get_columns("subzonas_campus")}
        columnas_esperadas = {"id", "nombre_subzona", "piso", "zona_id", "tipo_subzona_id", "es_activo"}
        assert columnas_esperadas.issubset(columnas), f"Columnas incompletas en subzonas_campus: {columnas}"

    def test_sesion_orm_funcional(self, db_session):
        """Verifica que una sesión ORM (SessionLocal) puede consultar registros de la base de datos."""
        roles = db_session.query(Role).all()
        assert isinstance(roles, list)
        assert len(roles) > 0, "Debe existir al menos un rol registrado en la base de datos"
