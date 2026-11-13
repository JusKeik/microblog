"""Database models for the microblog service."""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""


followers = Table(
    "followers",
    Base.metadata,
    Column(
        "follower_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "followed_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    CheckConstraint(
        "follower_id <> followed_id",
        name="ck_followers_not_self",
    ),
)


class User(Base):
    """Corporate user identified by an external API key."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    api_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    tweets: Mapped[list["Tweet"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )
    likes: Mapped[list["Like"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    following: Mapped[list["User"]] = relationship(
        secondary=followers,
        primaryjoin="User.id == followers.c.follower_id",
        secondaryjoin="User.id == followers.c.followed_id",
        back_populates="followers",
    )
    followers: Mapped[list["User"]] = relationship(
        secondary=followers,
        primaryjoin="User.id == followers.c.followed_id",
        secondaryjoin="User.id == followers.c.follower_id",
        back_populates="following",
    )


class Tweet(Base):
    """Tweet with an author, likes and optional images."""

    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(String(500))
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    author: Mapped[User] = relationship(back_populates="tweets")
    media: Mapped[list["Media"]] = relationship(
        back_populates="tweet",
        cascade="all, delete-orphan",
    )
    likes: Mapped[list["Like"]] = relationship(
        back_populates="tweet",
        cascade="all, delete-orphan",
    )


class Media(Base):
    """Uploaded image that can be attached to a tweet."""

    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_path: Mapped[str] = mapped_column(String(500))
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    tweet_id: Mapped[int | None] = mapped_column(
        ForeignKey("tweets.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    tweet: Mapped[Tweet | None] = relationship(back_populates="media")


class Like(Base):
    """Unique user reaction to a tweet."""

    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "tweet_id",
            name="uq_likes_user_tweet",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    tweet_id: Mapped[int] = mapped_column(
        ForeignKey("tweets.id", ondelete="CASCADE"),
        index=True,
    )

    user: Mapped[User] = relationship(back_populates="likes")
    tweet: Mapped[Tweet] = relationship(back_populates="likes")