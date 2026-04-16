from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy import func
from datetime import datetime
from typing import Optional

class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all database models."""
    
    __abstract__ = True
    
    def __repr__(self) -> str:
        """Simple repr for debugging."""
        return f"<{self.__class__.__name__}>"

# Import all models so Alembic can detect them
from app.models.user import User
from app.models.couple import Couple
from app.models.media_item import MediaItem
from app.models.music_track import MusicTrack
from app.models.special_date import SpecialDate
from app.models.quote import Quote
from app.models.refresh_token import RefreshToken

__all__ = [
    "Base",
    "User",
    "Couple", 
    "MediaItem",
    "MusicTrack",
    "SpecialDate",
    "Quote",
    "RefreshToken",
]