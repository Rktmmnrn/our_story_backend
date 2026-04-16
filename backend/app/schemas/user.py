"""User schemas for Notre Histoire API."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    display_name: str = Field(..., min_length=2, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    display_name: Optional[str] = Field(None, min_length=2, max_length=100)
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response (no password!)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    display_name: str
    avatar_url: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime


class UserAdminResponse(UserResponse):
    """Extended user response for admin endpoints."""

    model_config = ConfigDict(from_attributes=True)

    updated_at: datetime