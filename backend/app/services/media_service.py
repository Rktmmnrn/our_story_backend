"""
Media service: upload validation, save to disk, link to DB, streaming.
"""
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.file_manager import (
    FileSizeExceeded, InvalidMimeType,
    delete_file, get_absolute_path,
    save_upload, validate_photo, validate_video,
)


async def upload_media(
    db: AsyncSession,
    file: UploadFile,
    media_type: str,  # "photo" | "video"
    couple_id: UUID,
    uploaded_by: UUID,
    title: str | None,
    description: str | None,
    taken_at,
):
    from app.crud.media_item import crud_media_item
    from app.schemas.media_item import MediaItemCreate

    # Validate MIME
    try:
        if media_type == "photo":
            validate_photo(file)
        elif media_type == "video":
            validate_video(file)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="media_type doit être 'photo' ou 'video'",
            )
    except InvalidMimeType as e:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(e))

    # Save to disk
    category = media_type  # "photo" or "video"
    try:
        file_path, file_size = await save_upload(file, category)
    except FileSizeExceeded as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(e))

    obj_in = MediaItemCreate(title=title, description=description, taken_at=taken_at)

    item = await crud_media_item.create(
        db,
        couple_id=couple_id,
        uploaded_by=uploaded_by,
        media_type=media_type,
        file_path=file_path,
        original_filename=file.filename or "unknown",
        file_size_bytes=file_size,
        mime_type=file.content_type or "application/octet-stream",
        obj_in=obj_in,
    )
    return item


async def delete_media(db: AsyncSession, item_id: UUID, couple_id: UUID):
    from app.crud.media_item import crud_media_item

    item = await crud_media_item.get_by_id(db, item_id)
    if not item or item.couple_id != couple_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Média introuvable")

    file_path = await crud_media_item.delete(db, item)
    delete_file(file_path)


async def get_media_file_path(db: AsyncSession, item_id: UUID, couple_id: UUID):
    from app.crud.media_item import crud_media_item

    item = await crud_media_item.get_by_id(db, item_id)
    if not item or item.couple_id != couple_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Média introuvable")

    abs_path = get_absolute_path(item.file_path)
    if not abs_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fichier physique introuvable")

    return abs_path, item.mime_type, item.original_filename