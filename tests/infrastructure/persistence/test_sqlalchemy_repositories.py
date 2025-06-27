import uuid
from cebollin.domain.entities import User
from cebollin.domain.enums import Role
from cebollin.infrastructure.persistence.sqlalchemy_repositories import (
    SQLAlchemyUserRepository,
)
from cebollin.infrastructure.persistence.orm import (
    CompanyORM,
)  # Importamos el modelo ORM


def test_user_repository_add_and_get(test_db_session):
    """
    Verifica que un usuario puede ser añadido y recuperado de la base de datos.
    """
    # Arrange
    user_repo = SQLAlchemyUserRepository(session=test_db_session)

    # Primero, creamos y guardamos la compañía para satisfacer la clave foránea.
    company_orm = CompanyORM(id=uuid.uuid4(), name="Finca de Prueba S.A.")
    test_db_session.add(company_orm)
    test_db_session.commit()
    test_db_session.refresh(company_orm)

    new_user = User(
        id=uuid.uuid4(),
        firebase_uid="integration_test_uid",
        name="Usuario de Integración",
        email="integration@test.com",
        role=Role.FARMER,
        company_id=company_orm.id,  # Usamos el ID real de la compañía que acabamos de crear.
    )

    # Act
    user_repo.add(new_user)
    test_db_session.commit()

    retrieved_user = user_repo.get_by_id(new_user.id)

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.name == new_user.name
    assert retrieved_user.email == new_user.email
