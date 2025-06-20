from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from ....application.dto import TreatmentPlanCreateDTO, TreatmentPlanViewDTO
from ....application.services import TreatmentService
from ...container import get_db, get_treatment_service

router = APIRouter(prefix="/treatment-plans", tags=["Treatment Plans"])

@router.post("/", response_model=TreatmentPlanViewDTO, status_code=status.HTTP_201_CREATED)
def create_treatment_plan(
    request: TreatmentPlanCreateDTO,
    db: Session = Depends(get_db),
    # The service is now injected directly by FastAPI using our container
    service: TreatmentService = Depends(get_treatment_service)
):
    """
    Generates a treatment plan for a given diagnosis request ID.
    """
    try:
        # We use the injected service directly
        result_dto = service.generate_plan_for_diagnosis(request.diagnosis_request_id)
        db.commit()
        return result_dto
    except ValueError as e:
        # Catch specific errors from the service for better HTTP status codes
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        # Catch any other unexpected errors
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
