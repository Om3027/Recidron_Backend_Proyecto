import os
import sys
import pytest
from fastapi.testclient import TestClient

# Asegurar que la raíz del backend esté en sys.path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app
from models.database import SessionLocal, engine

@pytest.fixture(scope="session")
def client():
    """Cliente HTTP de pruebas para los endpoints de FastAPI."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def db_session():
    """Proporciona una sesión de base de datos para pruebas que lo requieran."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
