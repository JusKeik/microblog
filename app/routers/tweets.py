from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Tweet, User
from app.schemas import (
    FeedResponse,
    LikeAuthor,
    SuccessResponse,
    TweetCreate,
    TweetCreatedResponse,
    TweetInFeed,
    UserBrief,
)
from app.services import tweet_service

router = APIRouter(prefix="/api/tweets", tags=["Tweets"])


@router.post(
    "",
    response_model=TweetCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать твит",
)
def create_tweet(
    payload: TweetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TweetCreatedResponse:
    """Create a new tweet for the authenticated user."""
    tweet = tweet_service.create_tweet(
        db=db,
        author=current_user,
        content=payload.tweet_data,
        media_ids=payload.tweet_media_ids,
    )
    return TweetCreatedResponse(tweet_id=tweet.id)


@router.get(
    "",
    response_model=FeedResponse,
    summary="Получить ленту",
)
def get_feed(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FeedResponse:
    """Return a feed of tweets from users followed by the current user."""
    tweets = tweet_service.get_feed(db, current_user)

    return to_feed_response(tweets)


def to_feed_response(tweets: list[Tweet]) -> FeedResponse:
    """Serialize tweets consistently for feeds and profiles."""
    items = [
        TweetInFeed(
            id=tweet.id,
            content=tweet.content,
            attachments=[media.file_path for media in tweet.media],
            author=UserBrief(id=tweet.author.id, name=tweet.author.name),
            likes=[
                LikeAuthor(user_id=like.user.id, name=like.user.name)
                for like in tweet.likes
            ],
        )
        for tweet in tweets
    ]
    return FeedResponse(tweets=items)


@router.delete(
    "/{tweet_id}",
    response_model=SuccessResponse,
    summary="Удалить свой твит",
)
def delete_tweet(
    tweet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """Delete a tweet owned by the authenticated user."""
    tweet_service.delete_tweet(db, current_user, tweet_id)
    return SuccessResponse()


@router.post(
    "/{tweet_id}/likes",
    response_model=SuccessResponse,
    summary="Поставить лайк",
)
def like_tweet(
    tweet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """Mark a tweet as liked by the authenticated user."""
    tweet_service.like_tweet(db, current_user, tweet_id)
    return SuccessResponse()


@router.delete(
    "/{tweet_id}/likes",
    response_model=SuccessResponse,
    summary="Убрать лайк",
)
def unlike_tweet(
    tweet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    """Remove the authenticated user's like from a tweet."""
    tweet_service.unlike_tweet(db, current_user, tweet_id)
    return SuccessResponse()
