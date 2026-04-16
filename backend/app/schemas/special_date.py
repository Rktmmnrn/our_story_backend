"""Special date schemas for Notre Histoire API."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from .user import UserResponse


class SpecialDateCreate(BaseModel):
    """Schema for creating a special date."""

    title: str = Field(..., min_length=1)
    event_date: date
    description: Optional[str] = None
    emoji: Optional[str] = None


class SpecialDateUpdate(BaseModel):
    """Schema for updating a special date."""

    title: Optional[str] = Field(None, min_length=1)
    event_date: Optional[date] = None
    description: Optional[str] = None
    emoji: Optional[str] = None


class SpecialDateResponse(BaseModel):
    """Schema for special date response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    event_date: date
    description: Optional[str] = None
    emoji: Optional[str] = None
    created_by: UserResponse
    created_at: datetime