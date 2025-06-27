import uuid
from cebollin.domain.entities import User
from cebollin.domain.enums import Role
from cebollin.infrastructure.persistence.sqlalchemy_repositories import (
    SQLAlchemyUserRepository,
)


def test_user_repository_add_and_get(test_db_session):
    """
    Verifica que un usuario puede ser añadido y recuperado de la base de datos.
    DADO una sesión de BD de prueba y un repositorio.
    CUANDO se añade un usuario y luego se recupera por su ID.
    ENTONCES el usuario recuperado debe ser el mismo que el añadido.
    """
    # Arrange
    user_repo = SQLAlchemyUserRepository(session=test_db_session)
    company_id = uuid.uuid4()
    new_user = User(
        id=uuid.uuid4(),
        firebase_uid="integration_test_uid",
        name="Integration Test User",
        email="integration@test.com",
        role=Role.FARMER,
        company_id=company_id,
    )

    # Act
    user_repo.add(new_user)
    test_db_session.commit()  # Guardamos la transacción

    retrieved_user = user_repo.get_by_id(new_user.id)

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.name == new_user.name
    assert retrieved_user.email == new_user.email
