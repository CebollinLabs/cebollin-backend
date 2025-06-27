from fastapi.testclient import TestClient
from cebollin.presentation.main import app

# Crea una instancia del cliente de prueba que usaremos en todos los tests de este archivo
client = TestClient(app)


def test_list_company_users_as_owner():
    """
    Verifica que un Owner puede listar los usuarios de su compañía.
    DADO que el sistema está funcionando.
    CUANDO se hace una petición GET a /api/v1/users/ (con un token de Owner).
    ENTONCES la respuesta debe ser 200 OK y contener una lista de usuarios.
    """
    # Arrange
    # En un test real, sobreescribiríamos la dependencia `get_current_user`
    # para simular un Owner autenticado. Por ahora, confiamos en el mock.

    # Act
    response = client.get("/api/v1/users/")

    # Assert
    assert response.status_code == 200
    # Verificamos que la respuesta es una lista (puede estar vacía o no)
    assert isinstance(response.json(), list)
