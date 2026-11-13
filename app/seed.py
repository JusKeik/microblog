"""Create a small connected demo dataset on the first database startup."""

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Like, Tweet, User


def seed_demo_data() -> None:
    """Seed only an empty user database; preserve existing user data."""
    with SessionLocal() as db:
        if db.scalar(select(User).limit(1)):
            return
        alice = User(name="Alice", api_key="test-key-alice")
        bob = User(name="Bob", api_key="test-key-bob")
        carol = User(name="Carol", api_key="test-key-carol")
        alice.following.extend([bob, carol])
        bob.following.append(alice)
        carol.following.append(alice)
        db.add_all([alice, bob, carol])
        db.flush()
        popular = Tweet(content="Welcome to the corporate microblog!", author=bob)
        other = Tweet(content="Share updates with your colleagues here.", author=carol)
        db.add_all([popular, other])
        db.flush()
        db.add_all(
            [
                Like(user_id=alice.id, tweet_id=popular.id),
                Like(user_id=carol.id, tweet_id=popular.id),
            ]
        )
        db.commit()
