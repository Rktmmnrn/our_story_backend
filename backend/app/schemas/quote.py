"""Quote schemas for Notre Histoire API."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from .user import UserResponse


class QuoteCreate(BaseModel):
    """Schema for creating a quote."""

    text: str = Field(..., min_length=1)
    author: Optional[str] = None


class QuoteUpdate(BaseModel):
    """Schema for updating a quote."""

    text: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = None
    is_favorite: Optional[bool] = None


class QuoteResponse(BaseModel):
    """Schema for quote response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    author: Optional[str] = None
    is_favorite: bool
    created_by: UserResponse
    created_at: datetime