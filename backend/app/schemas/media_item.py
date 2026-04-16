"""Media item schemas for Notre Histoire API."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .user import UserResponse


class MediaItemCreate(BaseModel):
    """Schema for creating a media item."""

    title: Optional[str] = None
    description: Optional[str] = None
    taken_at: Optional[datetime] = None


class MediaItemUpdate(BaseModel):
    """Schema for updating a media item."""

    title: Optional[str] = None
    description: Optional[str] = None
    taken_at: Optional[datetime] = None


class MediaItemResponse(BaseModel):
    """Schema for media item response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    media_type: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    taken_at: Optional[datetime] = None
    uploaded_by: UserResponse
    created_at: datetime