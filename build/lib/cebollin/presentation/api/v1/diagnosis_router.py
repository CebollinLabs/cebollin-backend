import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, status, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from ....application.dto import (
    DiagnosisRequestViewDTO,
    DiagnosisUpdateDTO,
    PresignedUrlDTO,
)
from ....application.services import DiagnosisService, CreateDiagnosisService
from ...container import get_db, get_diagnosis_service, get_create_diagnosis_service
from ...auth import get_current_user, AuthenticatedUser

router = APIRouter(prefix="/diagnosis-requests", tags=["Diagnosis"])


@router.post(
    "/", response_model=DiagnosisRequestViewDTO, status_code=status.HTTP_201_CREATED
)
async def create_diagnosis_request(
    image: UploadFile = File(..., description="Image file of the onion crop."),
    name: Optional[str] = Form(None, description="A custom name for the evaluation."),
    plot_id: Optional[uuid.UUID] = Form(None, description="The ID of the plot."),
    comments: Optional[str] = Form(None, description="Additional comments."),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    create_service: CreateDiagnosisService = Depends(get_create_diagnosis_service),
    read_service: DiagnosisService = Depends(get_diagnosis_service),
):
    """Submits an onion crop image for diagnosis."""
    try:
        created_entity = await create_service.create_diagnosis_request(
            image_file=image,
            user_id=current_user.id,
            name=name,
            plot_id=plot_id,
            comments=comments,
        )

        db.commit()

        # --- THIS IS THE FIX ---
        # We pass the ID from the created entity, not the whole object.
        final_dto = read_service.get_diagnosis_by_id(created_entity.id, current_user)
        if not final_dto:
            raise HTTPException(
                status_code=404, detail="Could not retrieve newly created diagnosis."
            )

        return final_dto

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )


@router.get(
    "/", response_model=List[DiagnosisRequestViewDTO], summary="Get diagnosis history"
)
def get_diagnosis_history(
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: DiagnosisService = Depends(get_diagnosis_service),
):
    """
    Retrieves the history of diagnosis requests.
    - Owners see all requests for their company.
    - Farmers see only their own requests.
    """
    return service.list_requests_for_user(current_user)


@router.get(
    "/{request_id}",
    response_model=DiagnosisRequestViewDTO,
    summary="Get a single diagnosis request",
)
def get_diagnosis_request(
    request_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: DiagnosisService = Depends(get_diagnosis_service),
):
    """Retrieves a single diagnosis by its ID, checking for company access."""
    diagnosis = service.get_diagnosis_by_id(request_id, current_user)
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis not found or access denied.",
        )
    return diagnosis


@router.put(
    "/{request_id}",
    response_model=DiagnosisRequestViewDTO,
    summary="Update a diagnosis request",
)
def update_diagnosis_request(
    request_id: uuid.UUID,
    update_data: DiagnosisUpdateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: DiagnosisService = Depends(get_diagnosis_service),
):
    """Updates the name, plot, and comments of a diagnosis request."""
    try:
        updated_dto = service.update_diagnosis(request_id, update_data, current_user)
        db.commit()
        return updated_dto
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        )


@router.get(
    "/{request_id}/download-url",
    response_model=PresignedUrlDTO,
    summary="Get a temporary URL to view a diagnosis image",
)
def get_image_download_url(
    request_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: DiagnosisService = Depends(get_diagnosis_service),
):
    """
    Generates a secure, temporary presigned URL to view a private S3 image.
    """
    url_dto = service.get_presigned_image_url(request_id, current_user)
    if not url_dto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis not found or access denied.",
        )
    return url_dto
