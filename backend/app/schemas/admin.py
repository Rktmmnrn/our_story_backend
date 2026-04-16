"""Admin schemas for Notre Histoire API."""

from typing import Generic, TypeVar

from pydantic import BaseModel

from .user import UserAdminResponse

T = TypeVar("T")


class AdminStatsResponse(BaseModel):
    """Schema for admin statistics response."""

    total_users: int
    active_users: int
    total_couples: int
    active_couples: int
    total_media: int
    total_photos: int
    total_videos: int
    total_music_tracks: int
    total_special_dates: int
    total_quotes: int
    media_disk_usage_mb: float
    recent_users: list[UserAdminResponse]


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""

    data: list[T]
    total: int
    page: int
    per_page: int


class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper."""

    data: T
    message: str = "success"


class PaginatedAPIResponse(BaseModel, Generic[T]):
    """Generic paginated API response wrapper."""

    data: list[T]
    total: int
    page: int
    per_page: int
    message: str = "success"