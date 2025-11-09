import uuid
from typing import Optional, List
from sqlalchemy.orm import Session, selectinload
from pydantic import EmailStr

from ...domain.entities import User, DiagnosisRequest, Plot
from ...domain.repositories import (
    IUserRepository,
    IDiagnosisRequestRepository,
    IPlotRepository,
)
from .orm import UserORM, DiagnosisRequestORM, PredictionORM, TreatmentPlanORM, PlotORM


class SQLAlchemyUserRepository(IUserRepository):
    """SQLAlchemy implementation of the user repository."""

    def __init__(self, session: Session):
        self._session = session

    def add(self, user: User) -> None:
        orm_user = UserORM(
            id=user.id,
            firebase_uid=user.firebase_uid,
            name=user.name,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            company_id=user.company_id,
        )
        self._session.add(orm_user)

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        orm_user = self._session.query(UserORM).filter_by(id=user_id).first()
        return User.model_validate(orm_user) if orm_user else None

    def get_by_email(self, email: EmailStr) -> Optional[User]:
        orm_user = self._session.query(UserORM).filter_by(email=email).first()
        return User.model_validate(orm_user) if orm_user else None

    def list_by_company(self, company_id: uuid.UUID) -> List[User]:
        orm_users = (
            self._session.query(UserORM)
            .filter_by(company_id=company_id)
            .order_by(UserORM.name)
            .all()
        )
        return [User.model_validate(user) for user in orm_users]

    def update(self, user: User) -> None:
        orm_user = self._session.query(UserORM).filter_by(id=user.id).first()
        if orm_user:
            orm_user.name = user.name
            orm_user.email = user.email
            orm_user.role = user.role
            orm_user.is_active = user.is_active
            self._session.add(orm_user)


class SQLAlchemyDiagnosisRequestRepository(IDiagnosisRequestRepository):
    """SQLAlchemy implementation of the diagnosis request repository."""

    def __init__(self, session: Session):
        self._session = session

    def add(self, request: DiagnosisRequest) -> None:
        """
        Builds the ORM object for the request and its child predictions,
        and adds them to the session to be inserted.
        """
        orm_obj = DiagnosisRequestORM(
            id=request.id,
            name=request.name,
            plot_id=request.plot_id,
            comments=request.comments,
            image_url=request.image_url,
            status=request.status,
            submitted_at=request.submitted_at,
            diagnosis_result=request.diagnosis_result,
            submitted_by_id=request.submitted_by_id,
            predictions=[
                PredictionORM(class_name=p.class_name, confidence=p.confidence)
                for p in request.predictions
            ],
        )
        self._session.add(orm_obj)

    def get_by_id(self, request_id: uuid.UUID) -> Optional[DiagnosisRequest]:
        orm_obj = (
            self._session.query(DiagnosisRequestORM)
            .options(
                selectinload(DiagnosisRequestORM.predictions),
                selectinload(DiagnosisRequestORM.treatment_plan),
                selectinload(DiagnosisRequestORM.plot),
            )
            .filter_by(id=request_id)
            .first()
        )
        return DiagnosisRequest.model_validate(orm_obj) if orm_obj else None

    def update(self, request: DiagnosisRequest) -> None:
        orm_request = (
            self._session.query(DiagnosisRequestORM).filter_by(id=request.id).first()
        )
        if orm_request:
            orm_request.name = request.name
            orm_request.plot_id = request.plot_id
            orm_request.comments = request.comments
            if request.treatment_plan and not orm_request.treatment_plan:
                orm_plan = TreatmentPlanORM(
                    id=request.treatment_plan.id,
                    description=request.treatment_plan.description,
                    generated_at=request.treatment_plan.generated_at,
                )
                orm_request.treatment_plan = orm_plan
            self._session.add(orm_request)

    def list_by_user_id(self, user_id: uuid.UUID) -> List[DiagnosisRequest]:
        orm_requests = (
            self._session.query(DiagnosisRequestORM)
            .options(selectinload(DiagnosisRequestORM.plot))
            .filter_by(submitted_by_id=user_id)
            .order_by(DiagnosisRequestORM.submitted_at.desc())
            .all()
        )
        return [DiagnosisRequest.model_validate(req) for req in orm_requests]

    def list_by_company_id(self, company_id: uuid.UUID) -> List[DiagnosisRequest]:
        orm_requests = (
            self._session.query(DiagnosisRequestORM)
            .join(UserORM)
            .options(selectinload(DiagnosisRequestORM.plot))
            .filter(UserORM.company_id == company_id)
            .order_by(DiagnosisRequestORM.submitted_at.desc())
            .all()
        )
        return [DiagnosisRequest.model_validate(req) for req in orm_requests]


class SQLAlchemyPlotRepository(IPlotRepository):
    """SQLAlchemy implementation of the plot repository."""

    def __init__(self, session: Session):
        self._session = session

    def add(self, plot: Plot) -> None:
        orm_plot = PlotORM(id=plot.id, name=plot.name, company_id=plot.company_id)
        self._session.add(orm_plot)

    def get_by_id(self, plot_id: uuid.UUID) -> Optional[Plot]:
        orm_plot = self._session.query(PlotORM).filter_by(id=plot_id).first()
        return Plot.model_validate(orm_plot) if orm_plot else None

    def list_by_company(self, company_id: uuid.UUID) -> List[Plot]:
        orm_plots = (
            self._session.query(PlotORM)
            .filter_by(company_id=company_id)
            .order_by(PlotORM.name)
            .all()
        )
        return [Plot.model_validate(plot) for plot in orm_plots]

    def update(self, plot: Plot) -> None:
        orm_plot = self._session.query(PlotORM).filter_by(id=plot.id).first()
        if orm_plot:
            orm_plot.name = plot.name
            self._session.add(orm_plot)

    def delete(self, plot_id: uuid.UUID) -> None:
        orm_plot = self._session.query(PlotORM).filter_by(id=plot_id).first()
        if orm_plot:
            self._session.delete(orm_plot)
