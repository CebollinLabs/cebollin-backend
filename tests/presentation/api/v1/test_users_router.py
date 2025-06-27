import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Generator  # Importamos el tipo Generator
from cebollin.presentation.main import app
from cebollin.presentation.container import get_db

# Importamos la sesión y el motor de prueba desde nuestro conftest
from tests.conftest import TestingSessionLocal, engine, Base


def override_get_db() -> Generator[Session, None, None]:
    """
    Una dependencia sobreescrita que usa la base de datos de prueba
    en lugar de la de producción para las peticiones del API.
    """
    db = None
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        if db:
            db.close()


# Le decimos a nuestra app de FastAPI que use esta función `override_get_db`
# cada vez que un endpoint pida la dependencia `get_db`.
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_teardown_module():
    """
    Este fixture se ejecuta una vez por cada módulo de prueba.
    Crea todas las tablas antes de las pruebas y las elimina después.
    """
    # Crea todas las tablas definidas en nuestro Base de SQLAlchemy
    Base.metadata.create_all(bind=engine)
    yield
    # Elimina todas las tablas después de que las pruebas del módulo hayan terminado
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_list_company_users_as_owner():
    """
    Verifica que un Owner puede listar los usuarios de su compañía.
    """
    # En un test real, también sobreescribiríamos `get_current_user`
    # para asegurar que el usuario que hace la petición existe en la BD de prueba.

    response = client.get("/api/v1/users/")

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), list)
