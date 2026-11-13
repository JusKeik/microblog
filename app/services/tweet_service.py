"""Business logic for tweets, likes and the user feed."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.exceptions import ForbiddenError, NotFoundError
from app.models import Like, Media, Tweet, User, followers


def create_tweet(
    db: Session,
    author: User,
    content: str,
    media_ids: list[int],
) -> Tweet:
    """Create a tweet and attach media uploaded by its author."""
    tweet = Tweet(content=content, author_id=author.id)

    if media_ids:
        found_media = db.scalars(
            select(Media).where(
                Media.id.in_(media_ids),
                Media.owner_id == author.id,
                Media.tweet_id.is_(None),
            )
        ).all()

        found_ids = {item.id for item in found_media}
        missing_ids = sorted(set(media_ids) - found_ids)

        if missing_ids:
            raise NotFoundError(
                f"Картинки недоступны для прикрепления: {missing_ids}"
            )

        tweet.media.extend(found_media)

    db.add(tweet)
    db.commit()
    db.refresh(tweet)
    return tweet


def get_tweet_or_404(db: Session, tweet_id: int) -> Tweet:
    """Return a tweet or raise a not-found error."""
    tweet = db.get(Tweet, tweet_id)

    if tweet is None:
        raise NotFoundError("Твит не найден")

    return tweet


def delete_tweet(
    db: Session,
    current_user: User,
    tweet_id: int,
) -> None:
    """Delete a tweet only if it belongs to the current user."""
    tweet = get_tweet_or_404(db, tweet_id)

    if tweet.author_id != current_user.id:
        raise ForbiddenError("Можно удалять только свои твиты")

    db.delete(tweet)
    db.commit()


def like_tweet(
    db: Session,
    current_user: User,
    tweet_id: int,
) -> None:
    """Add a like from the current user."""
    tweet = get_tweet_or_404(db, tweet_id)

    existing_like = db.scalar(
        select(Like).where(
            Like.user_id == current_user.id,
            Like.tweet_id == tweet.id,
        )
    )

    if existing_like:
        raise ForbiddenError("Твит уже понравился пользователю")

    db.add(
        Like(
            user_id=current_user.id,
            tweet_id=tweet.id,
        )
    )
    db.commit()


def unlike_tweet(
    db: Session,
    current_user: User,
    tweet_id: int,
) -> None:
    """Remove the current user's like from a tweet."""
    tweet = get_tweet_or_404(db, tweet_id)

    like = db.scalar(
        select(Like).where(
            Like.user_id == current_user.id,
            Like.tweet_id == tweet.id,
        )
    )

    if like is None:
        raise ForbiddenError("Лайк не найден")

    db.delete(like)
    db.commit()


def get_feed(db: Session, current_user: User) -> list[Tweet]:
    """Return followed users' tweets sorted by popularity."""
    following_ids = select(followers.c.followed_id).where(
        followers.c.follower_id == current_user.id
    )

    likes_count = (
        select(func.count(Like.id))
        .where(Like.tweet_id == Tweet.id)
        .correlate(Tweet)
        .scalar_subquery()
    )

    statement = (
        select(Tweet)
        .where(Tweet.author_id.in_(following_ids))
        .options(
            selectinload(Tweet.author),
            selectinload(Tweet.media),
            selectinload(Tweet.likes).selectinload(Like.user),
        )
        .order_by(
            likes_count.desc(),
            Tweet.created_at.desc(),
            Tweet.id.desc(),
        )
    )

    return list(db.scalars(statement).all())