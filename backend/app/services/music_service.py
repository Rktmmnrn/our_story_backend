"""
Music service: upload validation, save to disk, link to DB.
"""
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.file_manager import (
    FileSizeExceeded, InvalidMimeType,
    delete_file, get_absolute_path,
    save_upload, validate_audio,
)


async def upload_music(
    db: AsyncSession,
    file: UploadFile,
    couple_id: UUID,
    uploaded_by: UUID,
    title: str,
    artist: str | None,
):
    from app.crud.music_track import crud_music_track
    from app.schemas.music_track import MusicTrackCreate

    try:
        validate_audio(file)
    except InvalidMimeType as e:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(e))

    try:
        file_path, _ = await save_upload(file, "music")
    except FileSizeExceeded as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(e))

    obj_in = MusicTrackCreate(title=title, artist=artist)

    track = await crud_music_track.create(
        db,
        couple_id=couple_id,
        uploaded_by=uploaded_by,
        file_path=file_path,
        obj_in=obj_in,
    )
    return track


async def delete_music(db: AsyncSession, track_id: UUID, couple_id: UUID):
    from app.crud.music_track import crud_music_track

    track = await crud_music_track.get_by_id(db, track_id)
    if not track or track.couple_id != couple_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Musique introuvable")

    file_path = await crud_music_track.delete(db, track)
    delete_file(file_path)


async def get_music_file_path(db: AsyncSession, track_id: UUID, couple_id: UUID):
    from app.crud.music_track import crud_music_track

    track = await crud_music_track.get_by_id(db, track_id)
    if not track or track.couple_id != couple_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Musique introuvable")

    abs_path = get_absolute_path(track.file_path)
    if not abs_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fichier audio introuvable")

    return abs_path, "audio/mpeg", track.title