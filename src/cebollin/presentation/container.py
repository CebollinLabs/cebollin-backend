from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Generator

from ..application.services import (
    DiagnosisService,
    TreatmentService,
    UserService,
    CreateDiagnosisService,
    PlotService,
)
from ..infrastructure.persistence.orm import SessionLocal
from ..infrastructure.persistence.sqlalchemy_repositories import (
    SQLAlchemyDiagnosisRequestRepository,
    SQLAlchemyUserRepository,
    SQLAlchemyPlotRepository,
)
from ..infrastructure.services.ai_model_client import AIModelClient
from ..infrastructure.services.file_storage import S3FileStorage
from ..infrastructure.services.llm_client import GeminiClient
from ..infrastructure.config import settings


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_create_diagnosis_service(
    db: Session = Depends(get_db),
) -> CreateDiagnosisService:
    """Builds the service responsible for creating new diagnoses."""
    return CreateDiagnosisService(
        diagnosis_repo=SQLAlchemyDiagnosisRequestRepository(session=db),
        ai_client=AIModelClient(base_url=settings.MODEL_API_BASE_URL),
        file_storage=S3FileStorage(),
    )


def get_diagnosis_service(db: Session = Depends(get_db)) -> DiagnosisService:
    """Builds the service for reading/updating existing diagnoses."""
    return DiagnosisService(
        diagnosis_repo=SQLAlchemyDiagnosisRequestRepository(session=db),
        user_repo=SQLAlchemyUserRepository(session=db),
        file_storage=S3FileStorage(),
    )


def get_treatment_service(db: Session = Depends(get_db)) -> TreatmentService:
    """Builds the TreatmentService with all its real dependencies."""
    return TreatmentService(
        diagnosis_repo=SQLAlchemyDiagnosisRequestRepository(session=db),
        llm_client=GeminiClient(),
    )


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Builds the UserService."""
    return UserService(user_repo=SQLAlchemyUserRepository(session=db))


def get_plot_service(db: Session = Depends(get_db)) -> PlotService:
    """Builds the PlotService."""
    return PlotService(plot_repo=SQLAlchemyPlotRepository(session=db))
