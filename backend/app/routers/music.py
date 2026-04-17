"""
Music router: /api/v1/music
"""
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_couple, get_current_user, get_db
from app.services import music_service

router = APIRouter(prefix="/music", tags=["Musique"])


@router.get("/")
async def list_music(
    db: AsyncSession = Depends(get_db),
    couple=Depends(get_current_couple),
):
    from app.crud.music_track import crud_music_track

    tracks = await crud_music_track.list_by_couple(db, couple.id)
    return {
        "data": [
            {
                "id": str(t.id),
                "title": t.title,
                "artist": t.artist,
                "duration_seconds": t.duration_seconds,
                "is_active": t.is_active,
                "created_at": t.created_at,
            }
            for t in tracks
        ],
        "message": "success",
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_music(
    file: UploadFile = File(...),
    title: str = Form(...),
    artist: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    couple=Depends(get_current_couple),
):
    track = await music_service.upload_music(
        db, file, couple.id, current_user.id, title, artist
    )
    return {"data": {"id": str(track.id), "title": track.title}, "message": "Musique uploadée"}


@router.patch("/{track_id}")
async def update_music(
    track_id: UUID,
    title: str | None = None,
    artist: str | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
    couple=Depends(get_current_couple),
):
    from app.crud.music_track import crud_music_track
    from app.schemas.music_track import MusicTrackUpdate

    track = await crud_music_track.get_by_id(db, track_id)
    if not track or track.couple_id != couple.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Musique introuvable")

    obj_in = MusicTrackUpdate(title=title, artist=artist, is_active=is_active)
    updated = await crud_music_track.update(db, track, obj_in)
    return {"data": {"id": str(updated.id)}, "message": "Musique mise à jour"}


@router.delete("/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_music(
    track_id: UUID,
    db: AsyncSession = Depends(get_db),
    couple=Depends(get_current_couple),
):
    await music_service.delete_music(db, track_id, couple.id)


@router.get("/{track_id}/file")
async def stream_music(
    track_id: UUID,
    db: AsyncSession = Depends(get_db),
    couple=Depends(get_current_couple),
):
    abs_path, mime_type, title = await music_service.get_music_file_path(
        db, track_id, couple.id
    )
    return FileResponse(path=str(abs_path), media_type=mime_type, filename=title)