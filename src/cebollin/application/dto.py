import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, HttpUrl
from ..domain.enums import DiagnosisStatus, Role


class AuthenticatedUser(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    role: Role


class PredictionDTO(BaseModel):
    class_name: str
    confidence: float

    class Config:
        from_attributes = True


class PlotDTO(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        from_attributes = True


class DiagnosisRequestViewDTO(BaseModel):
    id: uuid.UUID
    name: str
    status: DiagnosisStatus
    diagnosis_result: Optional[str] = None
    submitted_at: datetime
    predictions: List[PredictionDTO] = []
    image_url: str
    comments: Optional[str] = None
    plot: Optional[PlotDTO] = None

    class Config:
        from_attributes = True


class DiagnosisUpdateDTO(BaseModel):
    name: str
    plot_id: Optional[uuid.UUID] = None
    comments: Optional[str] = None


class TreatmentPlanCreateDTO(BaseModel):
    diagnosis_request_id: uuid.UUID


class TreatmentPlanViewDTO(BaseModel):
    id: uuid.UUID
    description: str
    generated_at: datetime

    class Config:
        from_attributes = True


class UserViewDTO(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: Role
    is_active: bool
    company_id: uuid.UUID

    class Config:
        from_attributes = True


class UserCreateDTO(BaseModel):
    name: str
    email: EmailStr


class UserUpdateDTO(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Role] = None


class ProfileUpdateDTO(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class PlotCreateDTO(BaseModel):
    name: str


class PlotUpdateDTO(BaseModel):
    name: str


class PresignedUrlDTO(BaseModel):
    """DTO for returning a presigned URL."""

    url: str  # Changed from HttpUrl to str for simplicity


DiagnosisRequestViewDTO.model_rebuild()
