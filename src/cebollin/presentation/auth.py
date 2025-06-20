import uuid
from ..application.dto import AuthenticatedUser
from ..domain.enums import Role


def get_current_user() -> AuthenticatedUser:
    """
    MOCK DEPENDENCY: Returns a hardcoded 'Owner' user for testing.
    In a real app, this function would validate a Firebase JWT token.
    """
    return AuthenticatedUser(
        id=uuid.UUID("8f4e2f9d-3b7c-4a1d-8b3e-2b6c4b2a1c7e"),
        company_id=uuid.UUID("a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6"),
        role=Role.OWNER,
    )
