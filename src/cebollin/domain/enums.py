from enum import Enum


class DiagnosisStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Role(str, Enum):
    """Defines the roles a user can have within the system."""

    OWNER = "OWNER"
    FARMER = "FARMER"
