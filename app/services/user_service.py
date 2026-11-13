"""Business logic for user profiles and subscriptions."""

from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session, selectinload

from app.exceptions import ConflictError, NotFoundError
from app.models import User, followers


def get_user_or_404(db: Session, user_id: int) -> User:
    """Return a user or raise a not-found error."""
    user = db.get(User, user_id)

    if user is None:
        raise NotFoundError("Пользователь не найден")

    return user


def get_profile(db: Session, user_id: int) -> User:
    """Return a user with followers and following collections."""
    statement = (
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.followers),
            selectinload(User.following),
        )
    )

    user = db.scalar(statement)

    if user is None:
        raise NotFoundError("Пользователь не найден")

    return user


def follow_user(
    db: Session,
    current_user: User,
    target_id: int,
) -> None:
    """Create a subscription from the current user to another user."""
    target = get_user_or_404(db, target_id)

    if target.id == current_user.id:
        raise ConflictError("Нельзя подписаться на себя")

    existing_follow = db.scalar(
        select(followers.c.follower_id).where(
            followers.c.follower_id == current_user.id,
            followers.c.followed_id == target.id,
        )
    )

    if existing_follow is not None:
        raise ConflictError("Вы уже подписаны на этого пользователя")

    db.execute(
        insert(followers).values(
            follower_id=current_user.id,
            followed_id=target.id,
        )
    )
    db.commit()


def unfollow_user(
    db: Session,
    current_user: User,
    target_id: int,
) -> None:
    """Remove a subscription from the current user."""
    target = get_user_or_404(db, target_id)

    result = db.execute(
        delete(followers).where(
            followers.c.follower_id == current_user.id,
            followers.c.followed_id == target.id,
        )
    )

    if result.rowcount == 0:
        raise ConflictError("Вы не подписаны на этого пользователя")

    db.commit()