# Import Base from database — single source of truth
# Do NOT redefine Base here, it lives in app.database
from app.database import Base  # noqa: F401

# Import all models so Alembic detects them via Base.metadata
from app.models.user import User  # noqa: F401
from app.models.couple import Couple  # noqa: F401
from app.models.media_item import MediaItem  # noqa: F401
from app.models.music_track import MusicTrack  # noqa: F401
from app.models.special_date import SpecialDate  # noqa: F401
from app.models.quote import Quote  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401

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