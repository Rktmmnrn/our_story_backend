"""Music track schemas for Notre Histoire API."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from .user import UserResponse


class MusicTrackCreate(BaseModel):
    """Schema for creating a music track."""

    title: str = Field(..., min_length=1)
    artist: Optional[str] = None


class MusicTrackUpdate(BaseModel):
    """Schema for updating a music track."""

    title: Optional[str] = Field(None, min_length=1)
    artist: Optional[str] = None
    duration_seconds: Optional[int] = None
    is_active: Optional[bool] = None


class MusicTrackResponse(BaseModel):
    """Schema for music track response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    artist: Optional[str] = None
    duration_seconds: Optional[int] = None
    is_active: bool
    uploaded_by: UserResponse
    created_at: datetime