"""
Media router: /api/v1/media
"""
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_couple, get_current_user, get_db
from app.services import media_service

router = APIRouter(prefix="/media", tags=["Médias"])


@router.get("/")
async def list_media(
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
    couple=Depends(get_current_couple),
):
    from app.crud.media_item import crud_media_item

    skip = (page - 1) * per_page
    items = await crud_media_item.list_by_couple(db, couple.id, skip=skip, limit=per_page)
    total = await crud_media_item.count_by_couple(db, couple.id)

    return {
        "data": [
            {
                "id": str(i.id),
                "media_type": i.media_type,
                "original_filename": i.original_filename,
                "title": i.title,
                "description": i.description,
                "file_size_bytes": i.file_size_bytes,
                "mime_type": i.mime_type,
                "taken_at": i.taken_at,
                "created_at": i.created_at,
            }
            for i in items
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "message": "success",
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_media(
    media_type: str = Form(...),
    file: UploadFile = File(...),
    title: str | None = Form(None),
    description: str | None = Form(None),
    taken_at: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    couple=Depends(get_current_couple),
):
    from datetime import datetime

    taken_at_dt = None
    if taken_at:
        try:
            taken_at_dt = datetime.fromisoformat(taken_at)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format taken_at invalide. Utilisez ISO 8601.",
            )

    item = await media_service.upload_media(
        db, file, media_type, couple.id, current_user.id,
        title, description, taken_at_dt
    )
    return {"data": {"id": str(item.id)}, "message": "Média uploadé avec succès"}


@router.get("/{item_id}")
async def get_media(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    couple=Depends(get_current_couple),
):
    from app.crud.media_item import crud_media_item

    item = await crud_media_item.get_by_id(db, item_id)
    if not item or item.couple_id != couple.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Média introuvable")

    return {
        "data": {
            "id": str(item.id),
            "media_type": item.media_type,
            "original_filename": item.original_filename,
            "title": item.title,
            "description": item.description,
            "file_size_bytes": item.file_size_bytes,
            "mime_type": item.mime_type,
            "taken_at": item.taken_at,
            "created_at": item.created_at,
        },
        "message": "success",
    }


@router.patch("/{item_id}")
async def update_media(
    item_id: UUID,
    title: str | None = None,
    description: str | None = None,
    db: AsyncSession = Depends(get_db),
    couple=Depends(get_current_couple),
):
    from app.crud.media_item import crud_media_item
    from app.schemas.media_item import MediaItemUpdate

    item = await crud_media_item.get_by_id(db, item_id)
    if not item or item.couple_id != couple.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Média introuvable")

    obj_in = MediaItemUpdate(title=title, description=description)
    updated = await crud_media_item.update(db, item, obj_in)
    return {"data": {"id": str(updated.id), "title": updated.title}, "message": "Média mis à jour"}


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    couple=Depends(get_current_couple),
):
    await media_service.delete_media(db, item_id, couple.id)


@router.get("/{item_id}/file")
async def stream_media(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    couple=Depends(get_current_couple),
):
    abs_path, mime_type, filename = await media_service.get_media_file_path(
        db, item_id, couple.id
    )
    return FileResponse(
        path=str(abs_path),
        media_type=mime_type,
        filename=filename,
    )