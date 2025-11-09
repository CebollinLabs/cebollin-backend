import uuid
from typing import Optional, List
from pathlib import Path
from fastapi import UploadFile
from pydantic import EmailStr

from ..domain.entities import (
    DiagnosisRequest,
    generate_default_name,
    Prediction,
    User,
    Plot,
)
from ..domain.repositories import (
    IDiagnosisRequestRepository,
    IUserRepository,
    IPlotRepository,
)
from ..domain.enums import DiagnosisStatus, Role
from ..infrastructure.services.ai_model_client import AIModelClient
from ..infrastructure.services.file_storage import IFileStorage
from ..infrastructure.services.llm_client import GeminiClient
from .dto import (
    DiagnosisRequestViewDTO,
    TreatmentPlanViewDTO,
    UserViewDTO,
    UserCreateDTO,
    AuthenticatedUser,
    UserUpdateDTO,
    ProfileUpdateDTO,
    DiagnosisUpdateDTO,
    PlotDTO,
    PlotCreateDTO,
    PlotUpdateDTO,
    PresignedUrlDTO,
)


class CreateDiagnosisService:
    """Service responsible only for the use case of creating a new diagnosis."""

    def __init__(
        self,
        diagnosis_repo: IDiagnosisRequestRepository,
        ai_client: AIModelClient,
        file_storage: IFileStorage,
    ):
        self._repo = diagnosis_repo
        self._ai_client = ai_client
        self._file_storage = file_storage

    async def create_diagnosis_request(
        self,
        image_file: UploadFile,
        user_id: uuid.UUID,
        name: Optional[str],
        plot_id: Optional[uuid.UUID],
        comments: Optional[str],
    ) -> DiagnosisRequest:

        image_bytes = await image_file.read()
        model_response = await self._ai_client.get_prediction(
            image_bytes, image_file.filename or "image.jpg"
        )

        # This now correctly returns just the object key, not the full URL
        object_key = self._file_storage.save_image(
            image_bytes=image_bytes,
            original_filename=image_file.filename or "image.jpg",
            content_type=image_file.content_type or "image/jpeg",
        )

        domain_predictions = [
            Prediction(class_name=p.class_name, confidence=float(p.confidence))
            for p in model_response.predictions
        ]
        top_result = (
            domain_predictions[0].class_name if domain_predictions else "Undetermined"
        )

        diagnosis_request = DiagnosisRequest(
            name=name if name else generate_default_name(),
            plot_id=plot_id,
            comments=comments,
            image_url=object_key,
            submitted_by_id=user_id,
            status=DiagnosisStatus.COMPLETED,
            diagnosis_result=top_result,
            predictions=domain_predictions,
        )

        self._repo.add(diagnosis_request)
        return diagnosis_request


class DiagnosisService:
    """Service for reading and updating existing diagnosis data."""

    def __init__(
        self,
        diagnosis_repo: IDiagnosisRequestRepository,
        user_repo: IUserRepository,
        file_storage: IFileStorage,
    ):
        self._repo = diagnosis_repo
        self._user_repo = user_repo
        self._file_storage = file_storage

    def list_requests_for_user(
        self, user: AuthenticatedUser
    ) -> List[DiagnosisRequestViewDTO]:
        diagnoses = []
        if user.role == Role.OWNER:
            diagnoses = self._repo.list_by_company_id(user.company_id)
        else:
            diagnoses = self._repo.list_by_user_id(user.id)
        return [DiagnosisRequestViewDTO.from_orm(d) for d in diagnoses]

    def get_diagnosis_by_id(
        self, request_id: uuid.UUID, user: AuthenticatedUser
    ) -> Optional[DiagnosisRequestViewDTO]:
        diagnosis = self._repo.get_by_id(request_id)
        if diagnosis:
            submitter = self._user_repo.get_by_id(diagnosis.submitted_by_id)
            if submitter and submitter.company_id == user.company_id:
                return DiagnosisRequestViewDTO.from_orm(diagnosis)
        return None

    def update_diagnosis(
        self,
        request_id: uuid.UUID,
        update_data: DiagnosisUpdateDTO,
        user: AuthenticatedUser,
    ) -> DiagnosisRequestViewDTO:
        diagnosis = self._repo.get_by_id(request_id)
        if not diagnosis or diagnosis.submitted_by_id != user.id:
            raise ValueError("Diagnosis request not found or access denied.")

        diagnosis.update_details(
            name=update_data.name,
            plot_id=update_data.plot_id,
            comments=update_data.comments,
        )
        self._repo.update(diagnosis)

        updated_diagnosis = self._repo.get_by_id(request_id)
        if not updated_diagnosis:
            raise ValueError("Failed to retrieve updated diagnosis.")
        return DiagnosisRequestViewDTO.from_orm(updated_diagnosis)

    def get_presigned_image_url(
        self, request_id: uuid.UUID, user: AuthenticatedUser
    ) -> Optional[PresignedUrlDTO]:
        """
        Checks authorization and generates a temporary presigned URL for a diagnosis image.
        """
        diagnosis = self._repo.get_by_id(request_id)
        if not diagnosis:
            return None

        submitter = self._user_repo.get_by_id(diagnosis.submitted_by_id)
        if not submitter or submitter.company_id != user.company_id:
            return None

        object_key = diagnosis.image_url
        presigned_url = self._file_storage.generate_presigned_download_url(object_key)

        return PresignedUrlDTO(url=presigned_url)


class TreatmentService:
    def __init__(
        self, diagnosis_repo: IDiagnosisRequestRepository, llm_client: GeminiClient
    ):
        self._repo = diagnosis_repo
        self._llm_client = llm_client

    def generate_plan_for_diagnosis(
        self, diagnosis_id: uuid.UUID
    ) -> TreatmentPlanViewDTO:
        diagnosis_request = self._repo.get_by_id(diagnosis_id)
        if not diagnosis_request or not diagnosis_request.diagnosis_result:
            raise ValueError("Diagnosis not found or not completed.")
        if diagnosis_request.treatment_plan:
            return TreatmentPlanViewDTO.from_orm(diagnosis_request.treatment_plan)
        plan_description = self._llm_client.generate_treatment_plan(
            disease_name=diagnosis_request.diagnosis_result
        )
        diagnosis_request.add_treatment_plan(plan_description)
        self._repo.update(diagnosis_request)
        if diagnosis_request.treatment_plan:
            return TreatmentPlanViewDTO.from_orm(diagnosis_request.treatment_plan)
        else:
            raise ValueError("Failed to create and retrieve treatment plan.")


class UserService:
    def __init__(self, user_repo: IUserRepository):
        self._repo = user_repo

    def create_farmer(
        self, new_user_data: UserCreateDTO, owner_company_id: uuid.UUID
    ) -> UserViewDTO:
        if self._repo.get_by_email(new_user_data.email):
            raise ValueError(f"User with email {new_user_data.email} already exists.")
        fake_firebase_uid = f"fake_firebase_uid_{uuid.uuid4()}"
        new_user = User(
            firebase_uid=fake_firebase_uid,
            name=new_user_data.name,
            email=new_user_data.email,
            role=Role.FARMER,
            company_id=owner_company_id,
            is_active=True,
        )
        self._repo.add(new_user)
        return UserViewDTO.from_orm(new_user)

    def get_users_in_company(self, company_id: uuid.UUID) -> List[UserViewDTO]:
        users = self._repo.list_by_company(company_id)
        return [UserViewDTO.from_orm(user) for user in users]

    def get_user_by_id(
        self, user_id: uuid.UUID, requester: AuthenticatedUser
    ) -> Optional[UserViewDTO]:
        user = self._repo.get_by_id(user_id)
        if user and user.company_id == requester.company_id:
            return UserViewDTO.from_orm(user)
        return None

    def update_user(
        self,
        user_id: uuid.UUID,
        update_data: UserUpdateDTO,
        requester: AuthenticatedUser,
    ) -> Optional[UserViewDTO]:
        user_to_update = self._repo.get_by_id(user_id)
        if not user_to_update or user_to_update.company_id != requester.company_id:
            return None
        if update_data.name is not None:
            user_to_update.name = update_data.name
        if update_data.email is not None:
            user_to_update.email = update_data.email
        if update_data.role is not None:
            user_to_update.role = update_data.role
        self._repo.update(user_to_update)
        return UserViewDTO.from_orm(user_to_update)

    def suspend_user(
        self, user_id: uuid.UUID, requester: AuthenticatedUser
    ) -> Optional[UserViewDTO]:
        user_to_suspend = self._repo.get_by_id(user_id)
        if not user_to_suspend or user_to_suspend.company_id != requester.company_id:
            return None
        user_to_suspend.deactivate()
        self._repo.update(user_to_suspend)
        return UserViewDTO.from_orm(user_to_suspend)

    def update_own_profile(
        self, user_id: uuid.UUID, profile_data: ProfileUpdateDTO
    ) -> UserViewDTO:
        user = self._repo.get_by_id(user_id)
        if not user:
            raise ValueError("Authenticated user not found in database.")
        if profile_data.name is not None:
            user.name = profile_data.name
        if profile_data.email is not None:
            user.email = profile_data.email
        self._repo.update(user)
        return UserViewDTO.from_orm(user)


class PlotService:
    def __init__(self, plot_repo: IPlotRepository):
        self._repo = plot_repo

    def create_plot(self, plot_data: PlotCreateDTO, user: AuthenticatedUser) -> PlotDTO:
        plot = Plot(name=plot_data.name, company_id=user.company_id)
        self._repo.add(plot)
        return PlotDTO.from_orm(plot)

    def list_plots_for_company(self, user: AuthenticatedUser) -> List[PlotDTO]:
        plots = self._repo.list_by_company(user.company_id)
        return [PlotDTO.from_orm(p) for p in plots]

    def update_plot(
        self, plot_id: uuid.UUID, plot_data: PlotUpdateDTO, user: AuthenticatedUser
    ) -> Optional[PlotDTO]:
        plot = self._repo.get_by_id(plot_id)
        if not plot or plot.company_id != user.company_id:
            return None
        plot.name = plot_data.name
        self._repo.update(plot)
        return PlotDTO.from_orm(plot)

    def delete_plot(self, plot_id: uuid.UUID, user: AuthenticatedUser) -> bool:
        plot = self._repo.get_by_id(plot_id)
        if not plot or plot.company_id != user.company_id:
            return False
        self._repo.delete(plot_id)
        return True
