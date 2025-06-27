import uuid
from cebollin.domain.entities import User
from cebollin.domain.enums import Role


def test_user_deactivate():
    """
    Verifica que el método deactivate() cambia el estado is_active a False.
    DADO un usuario activo.
    CUANDO se llama al método deactivate().
    ENTONCES el atributo is_active del usuario debe ser False.
    """
    # Arrange: Crear una instancia de la entidad User
    user = User(
        id=uuid.uuid4(),
        firebase_uid="test_uid",
        name="Test User",
        email="test@example.com",
        role=Role.FARMER,
        company_id=uuid.uuid4(),
        is_active=True,
    )

    # Act: Ejecutar el método que queremos probar
    user.deactivate()

    # Assert: Verificar que el resultado es el esperado
    assert user.is_active is False
