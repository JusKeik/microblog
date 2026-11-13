"""Unit tests for demo seeding and service error paths."""

from unittest.mock import patch

import pytest
from sqlalchemy import func, select

from app.exceptions import ConflictError, NotFoundError
from app.models import Like, Tweet, User
from app.seed import seed_demo_data
from app.services import tweet_service, user_service


def test_seed_demo_data_is_idempotent(db):
    for user in db.scalars(select(User)).all():
        db.delete(user)
    db.commit()
    with patch("app.seed.SessionLocal", return_value=db):
        seed_demo_data()
        seed_demo_data()
    assert db.scalar(select(func.count(User.id))) == 3
    assert db.scalar(select(func.count(Tweet.id))) == 2
    assert db.scalar(select(func.count(Like.id))) == 2
    alice = db.scalar(select(User).where(User.api_key == "test-key-alice"))
    assert len(alice.following) == 2
    assert len(tweet_service.get_feed(db, alice)) == 2


def test_missing_resources_and_invalid_subscriptions(db):
    alice = db.get(User, 1)
    with pytest.raises(NotFoundError):
        tweet_service.get_tweet_or_404(db, 999)
    with pytest.raises(NotFoundError):
        user_service.get_user_or_404(db, 999)
    with pytest.raises(NotFoundError):
        user_service.get_profile(db, 999)
    user_service.follow_user(db, alice, 2)
    with pytest.raises(ConflictError):
        user_service.follow_user(db, alice, 2)
    user_service.unfollow_user(db, alice, 2)
    with pytest.raises(ConflictError):
        user_service.unfollow_user(db, alice, 2)
    tweet = tweet_service.create_tweet(db, alice, "test", [])
    with pytest.raises(Exception) as error:
        tweet_service.unlike_tweet(db, alice, tweet.id)
    assert error.value.status_code == 403
