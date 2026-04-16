"""
Schemas package for Notre Histoire API.
Pydantic v2 models for request/response validation.
"""

from .user import UserCreate, UserUpdate, UserResponse, UserAdminResponse
from .couple import (
    CoupleCreate,
    CoupleUpdate,
    CoupleResponse,
    CoupleTimerResponse,
    InviteResponse,
)
from .media_item import MediaItemCreate, MediaItemUpdate, MediaItemResponse
from .music_track import MusicTrackCreate, MusicTrackUpdate, MusicTrackResponse
from .special_date import SpecialDateCreate, SpecialDateUpdate, SpecialDateResponse
from .quote import QuoteCreate, QuoteUpdate, QuoteResponse
from .auth import TokenResponse, RefreshRequest, LoginRequest, RegisterRequest
from .admin import AdminStatsResponse, PaginatedResponse, APIResponse, PaginatedAPIResponse

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserAdminResponse",
    # Couple
    "CoupleCreate",
    "CoupleUpdate",
    "CoupleResponse",
    "CoupleTimerResponse",
    "InviteResponse",
    # Media
    "MediaItemCreate",
    "MediaItemUpdate",
    "MediaItemResponse",
    # Music
    "MusicTrackCreate",
    "MusicTrackUpdate",
    "MusicTrackResponse",
    # Special Date
    "SpecialDateCreate",
    "SpecialDateUpdate",
    "SpecialDateResponse",
    # Quote
    "QuoteCreate",
    "QuoteUpdate",
    "QuoteResponse",
    # Auth
    "TokenResponse",
    "RefreshRequest",
    "LoginRequest",
    "RegisterRequest",
    # Admin
    "AdminStatsResponse",
    "PaginatedResponse",
    "APIResponse",
    "PaginatedAPIResponse",
]