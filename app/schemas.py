"""Pydantic request and response models."""

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Error response used by all failed API operations."""

    result: bool = False
    error_type: str
    error_message: str


class TweetCreate(BaseModel):
    """Request body for creating a tweet."""

    tweet_data: str = Field(min_length=1, max_length=500)
    tweet_media_ids: list[int] = Field(default_factory=list)


class TweetCreatedResponse(BaseModel):
    """Response returned after tweet creation."""

    result: bool = True
    tweet_id: int


class SuccessResponse(BaseModel):
    """Generic successful operation response."""

    result: bool = True


class MediaCreatedResponse(BaseModel):
    """Response returned after media upload."""

    result: bool = True
    media_id: int


class UserBrief(BaseModel):
    """Short user representation."""

    id: int
    name: str


class LikeAuthor(BaseModel):
    """User who liked a tweet."""

    user_id: int
    name: str


class TweetInFeed(BaseModel):
    """Tweet item returned in a feed."""

    id: int
    content: str
    attachments: list[str]
    author: UserBrief
    likes: list[LikeAuthor]


class FeedResponse(BaseModel):
    """User feed response."""

    result: bool = True
    tweets: list[TweetInFeed]


class UserProfile(BaseModel):
    """Detailed user profile."""

    id: int
    name: str
    followers: list[UserBrief]
    following: list[UserBrief]


class ProfileResponse(BaseModel):
    """User profile response."""

    result: bool = True
    user: UserProfile
