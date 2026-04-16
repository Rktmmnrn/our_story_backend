"""
CRUD operations package for Notre Histoire API.
SQLAlchemy 2.0 async operations.
"""

from .user import CRUDUser
from .couple import CRUDCouple
from .media_item import CRUDMediaItem
from .music_track import CRUDMusicTrack
from .special_date import CRUDSpecialDate
from .quote import CRUDQuote
from .refresh_token import CRUDRefreshToken

# Singleton instances
user = CRUDUser()
couple = CRUDCouple()
media_item = CRUDMediaItem()
music_track = CRUDMusicTrack()
special_date = CRUDSpecialDate()
quote = CRUDQuote()
refresh_token = CRUDRefreshToken()

__all__ = [
    "user",
    "couple",
    "media_item",
    "music_track",
    "special_date",
    "quote",
    "refresh_token",
    "CRUDUser",
    "CRUDCouple",
    "CRUDMediaItem",
    "CRUDMusicTrack",
    "CRUDSpecialDate",
    "CRUDQuote",
    "CRUDRefreshToken",
]