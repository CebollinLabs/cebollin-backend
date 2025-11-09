from abc import ABC, abstractmethod
import uuid
from typing import Optional, List, Any
from pydantic import EmailStr
from .entities import DiagnosisRequest, User, Plot, Prediction


class IDiagnosisRequestRepository(ABC):
    """Defines the contract for diagnosis data persistence."""

    @abstractmethod
    def add(self, request: DiagnosisRequest) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, request_id: uuid.UUID) -> Optional[DiagnosisRequest]:
        raise NotImplementedError

    @abstractmethod
    def update(self, request: DiagnosisRequest) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_by_user_id(self, user_id: uuid.UUID) -> List[DiagnosisRequest]:
        raise NotImplementedError

    @abstractmethod
    def list_by_company_id(self, company_id: uuid.UUID) -> List[DiagnosisRequest]:
        raise NotImplementedError


class IUserRepository(ABC):
    """Defines the contract for user data persistence."""

    @abstractmethod
    def add(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, email: EmailStr) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def list_by_company(self, company_id: uuid.UUID) -> List[User]:
        raise NotImplementedError

    @abstractmethod
    def update(self, user: User) -> None:
        raise NotImplementedError


class IPlotRepository(ABC):
    """Defines the contract for plot data persistence."""

    @abstractmethod
    def add(self, plot: Plot) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, plot_id: uuid.UUID) -> Optional[Plot]:
        raise NotImplementedError

    @abstractmethod
    def list_by_company(self, company_id: uuid.UUID) -> List[Plot]:
        raise NotImplementedError

    @abstractmethod
    def update(self, plot: Plot) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, plot_id: uuid.UUID) -> None:
        raise NotImplementedError
