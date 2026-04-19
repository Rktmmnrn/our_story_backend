"""
Local filesystem storage for media files.
All paths are relative to settings.MEDIA_ROOT.
Physical files are stored in: {MEDIA_ROOT}/{folder}/{uuid}.{ext}
"""
import asyncio
import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from app.config import settings

ALLOWED_PHOTO_MIME = {
    "image/jpeg", "image/png", "image/webp", "image/gif", "image/heic"
}
ALLOWED_VIDEO_MIME = {
    "video/mp4", "video/quicktime", "video/x-msvideo", "video/webm", "video/mpeg"
}
ALLOWED_AUDIO_MIME = {
    "audio/mpeg", "audio/mp4", "audio/wav", "audio/ogg", "audio/flac", "audio/aac"
}

FOLDER_MAP = {
    "photo": "photos",
    "video": "videos",
    "music": "music",
}

MAX_SIZES = {
    "photo": settings.MAX_PHOTO_SIZE_MB * 1024 * 1024,
    "video": settings.MAX_VIDEO_SIZE_MB * 1024 * 1024,
    "music": settings.MAX_AUDIO_SIZE_MB * 1024 * 1024,
}

CHUNK_SIZE = 4 * 1024 * 1024


class FileSizeExceeded(Exception):
    pass


class InvalidMimeType(Exception):
    pass


def _media_root() -> Path:
    return Path(settings.MEDIA_ROOT)


def _ext_from_mime(mime: str) -> str:
    mapping = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
        "image/gif": "gif",
        "image/heic": "heic",
        "video/mp4": "mp4",
        "video/quicktime": "mov",
        "video/x-msvideo": "avi",
        "video/webm": "webm",
        "video/mpeg": "mpeg",
        "audio/mpeg": "mp3",
        "audio/mp4": "m4a",
        "audio/wav": "wav",
        "audio/ogg": "ogg",
        "audio/flac": "flac",
        "audio/aac": "aac",
    }
    return mapping.get(mime, "bin")


def validate_photo(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_PHOTO_MIME:
        raise InvalidMimeType(
            f"Type MIME non autorisé pour une photo: {file.content_type}"
        )


def validate_video(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_VIDEO_MIME:
        raise InvalidMimeType(
            f"Type MIME non autorisé pour une vidéo: {file.content_type}"
        )


def validate_audio(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_AUDIO_MIME:
        raise InvalidMimeType(
            f"Type MIME non autorisé pour un audio: {file.content_type}"
        )


async def save_upload(file: UploadFile, category: str) -> tuple[str, int]:
    folder = FOLDER_MAP[category]
    dest_dir = _media_root() / folder
    dest_dir.mkdir(parents=True, exist_ok=True)

    ext = _ext_from_mime(file.content_type or "")
    filename = f"{uuid.uuid4()}.{ext}"
    dest_path = dest_dir / filename
    relative_path = f"{folder}/{filename}"

    max_size = MAX_SIZES[category]
    total_size = 0

    try:
        async with aiofiles.open(dest_path, "wb") as out:
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > max_size:
                    dest_path.unlink(missing_ok=True)
                    raise FileSizeExceeded(
                        f"Fichier trop volumineux. Max: {max_size // (1024 * 1024)} Mo"
                    )
                await out.write(chunk)
                await asyncio.sleep(0)
    except FileSizeExceeded:
        raise
    except Exception as e:
        dest_path.unlink(missing_ok=True)
        raise RuntimeError(f"Erreur lors de l'écriture du fichier: {e}") from e

    return relative_path, total_size


def delete_file(relative_path: str) -> None:
    full_path = _media_root() / relative_path
    if full_path.exists():
        full_path.unlink()


def get_absolute_path(relative_path: str) -> Path:
    return _media_root() / relative_path


def disk_usage_mb() -> dict[str, float]:
    result = {}
    root = _media_root()
    for folder in FOLDER_MAP.values():
        folder_path = root / folder
        if not folder_path.exists():
            result[folder] = 0.0
            continue
        total = sum(
            f.stat().st_size
            for f in folder_path.iterdir()
            if f.is_file()
        )
        result[folder] = round(total / (1024 * 1024), 2)
    return result