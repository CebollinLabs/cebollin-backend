import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cebollin.infrastructure.persistence.orm import Base

# --- Forzar la carga de variables de entorno de .env.test ---
# Esto es crucial para que SQLAlchemy use la base de datos de prueba.
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.test")

# Re-importamos 'settings' DESPUÉS de cargar .env.test
from cebollin.infrastructure.config import settings

# Crea un motor de base de datos que apunta a la BD de prueba
engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db_session():
    """
    Gestiona el ciclo de vida de una sesión de BD para una prueba.
    Crea todas las tablas antes de la prueba y las elimina después.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
