from typing import List
import uuid
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

# Add ProfileUpdateDTO to the imports
from ....application.dto import (
    UserViewDTO,
    UserCreateDTO,
    UserUpdateDTO,
    ProfileUpdateDTO,
)
from ....application.services import UserService
from ....domain.enums import Role
from ...container import get_db
from ...auth import get_current_user, AuthenticatedUser


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    from ....infrastructure.persistence.sqlalchemy_repositories import (
        SQLAlchemyUserRepository,
    )

    return UserService(user_repo=SQLAlchemyUserRepository(session=db))


router = APIRouter(prefix="/users", tags=["User Management"])


# --- ADD THIS NEW ENDPOINT ---
@router.put("/me", response_model=UserViewDTO, summary="Update own user profile")
def update_own_profile(
    profile_data: ProfileUpdateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
    db: Session = Depends(get_db),
):
    """
    Allows the currently authenticated user to update their own name and email.
    """
    try:
        updated_user = service.update_own_profile(current_user.id, profile_data)
        db.commit()
        return updated_user
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ... (The other endpoints: GET /, POST /, GET /{id}, PUT /{id}, POST /{id}/suspend are unchanged) ...
@router.get(
    "/", response_model=List[UserViewDTO], summary="List all users in the company"
)
def list_company_users(
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    if current_user.role != Role.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    return service.get_users_in_company(current_user.company_id)


@router.post(
    "/",
    response_model=UserViewDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Farmer user",
)
def create_farmer_user(
    new_user: UserCreateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
    db: Session = Depends(get_db),
):
    if current_user.role != Role.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    try:
        created_user = service.create_farmer(
            new_user_data=new_user, owner_company_id=current_user.company_id
        )
        db.commit()
        return created_user
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=UserViewDTO, summary="Get a single user by ID")
def get_user(
    user_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    if current_user.role != Role.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    user = service.get_user_by_id(user_id, current_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put(
    "/{user_id}", response_model=UserViewDTO, summary="Update a user's information"
)
def update_user(
    user_id: uuid.UUID,
    update_data: UserUpdateDTO,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
    db: Session = Depends(get_db),
):
    if current_user.role != Role.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    updated_user = service.update_user(user_id, update_data, current_user)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    db.commit()
    return updated_user


@router.post(
    "/{user_id}/suspend", response_model=UserViewDTO, summary="Suspend a user's account"
)
def suspend_user(
    user_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
    db: Session = Depends(get_db),
):
    if current_user.role != Role.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    suspended_user = service.suspend_user(user_id, current_user)
    if not suspended_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    db.commit()
    return suspended_user
