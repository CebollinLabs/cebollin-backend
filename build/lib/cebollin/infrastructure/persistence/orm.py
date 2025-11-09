import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    create_engine,
    Column,
    String,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
    Text,
    Boolean,
    Float,
)
from sqlalchemy.orm import (
    declarative_base,
    relationship,
    sessionmaker,
    Mapped,
    mapped_column,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from ...domain.enums import Role, DiagnosisStatus
from ..config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ... CompanyORM and UserORM are unchanged ...
class CompanyORM(Base):
    __tablename__ = "companies"
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    users: Mapped[List["UserORM"]] = relationship(back_populates="company")
    plots: Mapped[List["PlotORM"]] = relationship(back_populates="company")


class UserORM(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    firebase_uid: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    role: Mapped[Role] = mapped_column(SAEnum(Role, name="role"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    company: Mapped["CompanyORM"] = relationship(back_populates="users")
    diagnoses: Mapped[List["DiagnosisRequestORM"]] = relationship(
        back_populates="submitted_by"
    )


# --- NEW: Plot ORM model ---
class PlotORM(Base):
    __tablename__ = "plots"
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    company: Mapped["CompanyORM"] = relationship(back_populates="plots")
    diagnoses: Mapped[List["DiagnosisRequestORM"]] = relationship(back_populates="plot")


# ... PredictionORM and TreatmentPlanORM are unchanged ...
class PredictionORM(Base):
    __tablename__ = "predictions"
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    class_name: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    diagnosis_request_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("diagnosis_requests.id"), nullable=False
    )


class TreatmentPlanORM(Base):
    __tablename__ = "treatment_plans"
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    diagnosis_request_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("diagnosis_requests.id"), nullable=False
    )
    diagnosis_request: Mapped["DiagnosisRequestORM"] = relationship(
        back_populates="treatment_plan"
    )


class DiagnosisRequestORM(Base):
    __tablename__ = "diagnosis_requests"
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # --- CHANGED: Remove old 'plot' column ---
    # plot: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[DiagnosisStatus] = mapped_column(
        SAEnum(DiagnosisStatus, name="diagnosisstatus"), nullable=False
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    diagnosis_result: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    submitted_by_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # --- ADDED: Foreign key to the new plots table ---
    plot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("plots.id"), nullable=True
    )

    submitted_by: Mapped["UserORM"] = relationship(back_populates="diagnoses")
    predictions: Mapped[List["PredictionORM"]] = relationship(
        cascade="all, delete-orphan"
    )
    treatment_plan: Mapped[Optional["TreatmentPlanORM"]] = relationship(
        back_populates="diagnosis_request", cascade="all, delete-orphan"
    )
    # --- ADDED: Relationship to the Plot ORM ---
    plot: Mapped[Optional["PlotORM"]] = relationship(back_populates="diagnoses")
