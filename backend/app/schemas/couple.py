"""Couple schemas for Notre Histoire API."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .user import UserResponse


class CoupleCreate(BaseModel):
    """Schema for creating a new couple."""

    anniversary_date: date
    couple_name: Optional[str] = None


class CoupleUpdate(BaseModel):
    """Schema for updating couple information."""

    anniversary_date: Optional[date] = None
    couple_name: Optional[str] = None


class CoupleResponse(BaseModel):
    """Schema for couple response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    couple_name: Optional[str] = None
    anniversary_date: date
    user1: UserResponse
    user2: Optional[UserResponse] = None
    is_active: bool
    created_at: datetime


class CoupleTimerResponse(BaseModel):
    """Schema for couple timer/anniversary information."""

    days_together: int
    anniversary_date: date
    next_anniversary_in_days: int


class InviteResponse(BaseModel):
    """Schema for couple invite link."""

    invite_link: str
    expires_at: datetime