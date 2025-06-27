import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cebollin.infrastructure.persistence.orm import Base
from cebollin.infrastructure.config import settings

# Crea un motor de base de datos que apunta a la BD de prueba
engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db_session():
    """
    Un fixture de pytest que gestiona el ciclo de vida de una sesión de BD para una prueba.
    """
    # Antes de la prueba: crea todas las tablas
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Pasa la sesión de BD a la prueba
        yield db
    finally:
        # Después de la prueba: cierra la sesión y elimina todas las tablas
        db.close()
        Base.metadata.drop_all(bind=engine)
