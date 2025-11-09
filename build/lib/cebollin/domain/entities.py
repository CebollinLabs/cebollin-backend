import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from .enums import DiagnosisStatus, Role


def generate_default_name() -> str:
    return f"cebollin_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"


class Plot(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    company_id: uuid.UUID

    class Config:
        from_attributes = True


class Prediction(BaseModel):
    class_name: str
    confidence: float

    class Config:
        from_attributes = True


class TreatmentPlan(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    description: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class Company(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str


class User(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    firebase_uid: str
    name: str
    email: EmailStr
    role: Role
    company_id: uuid.UUID
    is_active: bool = True

    class Config:
        from_attributes = True

    def deactivate(self):
        self.is_active = False

    def activate(self):
        self.is_active = True


class DiagnosisRequest(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str = Field(default_factory=generate_default_name)
    plot_id: Optional[uuid.UUID] = None
    comments: Optional[str] = None
    image_url: str
    status: DiagnosisStatus
    submitted_by_id: uuid.UUID
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    diagnosis_result: Optional[str] = None
    predictions: List[Prediction] = []
    treatment_plan: Optional[TreatmentPlan] = None
    plot: Optional[Plot] = None

    class Config:
        from_attributes = True

    def add_treatment_plan(self, plan_description: str):
        if self.status != DiagnosisStatus.COMPLETED:
            raise ValueError("Cannot add treatment plan to an incomplete diagnosis.")
        self.treatment_plan = TreatmentPlan(description=plan_description)

    def update_details(
        self, name: str, plot_id: Optional[uuid.UUID], comments: Optional[str]
    ):
        self.name = name
        self.plot_id = plot_id
        self.comments = comments
