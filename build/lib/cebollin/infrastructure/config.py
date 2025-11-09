import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Robust .env loading logic for Docker and local ---
# Inside Docker, WORKDIR is /home/app, and .env is copied there.
# For local development, calculate relative to this file.
DOCKER_ENV_FILE_PATH = Path("/home/app/.env")

if DOCKER_ENV_FILE_PATH.exists() and os.environ.get(
    "RUNNING_IN_DOCKER"
):  # You'd set RUNNING_IN_DOCKER in Dockerfile
    ENV_FILE_PATH = DOCKER_ENV_FILE_PATH
    print(f"Running in Docker, using .env from: {ENV_FILE_PATH}")
elif (
    Path(".env").resolve().exists()
):  # Check relative to current WORKDIR (good for /home/app)
    ENV_FILE_PATH = Path(".env").resolve()
    print(f"Found .env relative to CWD: {ENV_FILE_PATH}")
else:  # Fallback for local dev if CWD is not project root
    PROJECT_ROOT_LOCAL = Path(__file__).resolve().parents[3]
    ENV_FILE_PATH = PROJECT_ROOT_LOCAL / ".env"
    print(f"Fallback for local dev, calculated .env path: {ENV_FILE_PATH}")


print(f"Attempting to load .env file from: {ENV_FILE_PATH}")

if ENV_FILE_PATH.exists():
    print(f".env file found at {ENV_FILE_PATH}. Loading it.")
    load_dotenv(dotenv_path=ENV_FILE_PATH, override=True)
    # Debug: Check if a key variable is loaded
    print(f"DB_HOST after load_dotenv: {os.getenv('DB_HOST')}")
    print(f"GEMINI_API_KEY after load_dotenv: {os.getenv('GEMINI_API_KEY')}")
else:
    print(
        f"Critical Warning: .env file NOT found at {ENV_FILE_PATH}. Settings will likely fail to load."
    )


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(extra="ignore")

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    GEMINI_API_KEY: str

    S3_BUCKET_NAME: str

    MODEL_API_BASE_URL: str

    @property
    def database_url(self) -> str:
        """Constructs the SQLAlchemy-compatible database connection URL."""
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()  # type: ignore
