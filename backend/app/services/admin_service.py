"""
Admin service: aggregated statistics and user/couple management.
"""
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.file_manager import disk_usage_mb


async def get_dashboard_stats(db: AsyncSession) -> dict:
    from app.crud.user import crud_user
    from app.crud.couple import crud_couple
    from app.crud.media_item import crud_media_item
    from app.crud.music_track import crud_music_track
    from app.crud.special_date import crud_special_date
    from app.crud.quote import crud_quote

    total_users = await crud_user.count(db)
    active_users = await crud_user.count_active(db)
    total_couples = await crud_couple.count(db)
    active_couples = await crud_couple.count_active(db)
    total_media = await crud_media_item.count_all(db)
    total_photos = await crud_media_item.count_by_type(db, "photo")
    total_videos = await crud_media_item.count_by_type(db, "video")
    total_music = await crud_music_track.count_all(db)
    total_dates = await crud_special_date.count_all(db)
    total_quotes = await crud_quote.count_all(db)
    recent_users = await crud_user.list_recent(db, limit=5)
    usage = disk_usage_mb()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_couples": total_couples,
        "active_couples": active_couples,
        "total_media": total_media,
        "total_photos": total_photos,
        "total_videos": total_videos,
        "total_music_tracks": total_music,
        "total_special_dates": total_dates,
        "total_quotes": total_quotes,
        "disk_usage_mb": usage,
        "recent_users": recent_users,
    }


async def admin_delete_user(db: AsyncSession, user_id: UUID, current_admin_id: UUID):
    from app.crud.user import crud_user
    from app.crud.couple import crud_couple
    from app.crud.media_item import crud_media_item
    from app.crud.music_track import crud_music_track
    from app.utils.file_manager import delete_file

    if user_id == current_admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas supprimer votre propre compte admin",
        )

    user = await crud_user.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")

    # Clean couple and files if user1
    couple = await crud_couple.get_active_by_user_id(db, user_id)
    if couple and couple.user1_id == user_id:
        # Delete all media files
        media_items = await crud_media_item.list_by_couple(db, couple.id, skip=0, limit=99999)
        for item in media_items:
            delete_file(item.file_path)

        music_tracks = await crud_music_track.list_by_couple(db, couple.id)
        for track in music_tracks:
            delete_file(track.file_path)

    await crud_user.delete(db, user)


async def admin_delete_couple(db: AsyncSession, couple_id: UUID):
    from app.crud.couple import crud_couple
    from app.crud.media_item import crud_media_item
    from app.crud.music_track import crud_music_track
    from app.utils.file_manager import delete_file

    couple = await crud_couple.get_by_id(db, couple_id)
    if not couple:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couple introuvable")

    media_items = await crud_media_item.list_by_couple(db, couple_id, skip=0, limit=99999)
    for item in media_items:
        delete_file(item.file_path)

    music_tracks = await crud_music_track.list_by_couple(db, couple_id)
    for track in music_tracks:
        delete_file(track.file_path)

    await crud_couple.dissolve(db, couple)