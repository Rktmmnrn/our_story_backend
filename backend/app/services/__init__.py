"""
Services package for Notre Histoire API.
"""
from . import auth_service, couple_service, media_service, music_service, admin_service

__all__ = [
    "auth_service",
    "couple_service",
    "media_service",
    "music_service",
    "admin_service",
]