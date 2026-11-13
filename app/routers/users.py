from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import ProfileResponse, SuccessResponse, UserProfile
from app.services import user_service

router = APIRouter(prefix="/api/users", tags=["Users"])


def _to_profile(user: User) -> ProfileResponse:
    """Convert an ORM user into the profile response."""
    return ProfileResponse(
        user=UserProfile(
            id=user.id,
            name=user.name,
            followers=[
                {"id": follower.id, "name": follower.name}
                for follower in user.followers
            ],
            following=[
                {"id": following.id, "name": following.name}
                for following in user.following
            ],
        )
    )


@router.get(
    "/me",
    response_model=ProfileResponse,
    summary="Получить свой профиль",
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    """Return the authenticated user's profile."""
    user = user_service.get_profile(db, current_user.id)
    return _to_profile(user)


@router.get(
    "/{user_id}",
    response_model=ProfileResponse,
    summary="Получить профиль пользователя",
)
def get_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    """Return another user's profile by ID."""
    user = user_service.get_profile(db, user_id)
    return _to_profile(user)


@router.post(
    "/{user_id}/follow",
    response_model=SuccessResponse,
    summary="Подписаться на пользователя",
)
def follow(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """Follow another user."""
    user_service.follow_user(db, current_user, user_id)
    return SuccessResponse()


@router.delete(
    "/{user_id}/follow",
    response_model=SuccessResponse,
    summary="Отписаться от пользователя",
)
def unfollow(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """Unfollow another user."""
    user_service.unfollow_user(db, current_user, user_id)
    return SuccessResponse()