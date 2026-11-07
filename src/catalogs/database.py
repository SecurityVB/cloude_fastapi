from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalogs.models import File
from src.users.database import update_user_storage_usage


async def get_file_by_server_name(
    server_filename: str,
    session: AsyncSession
) -> File | None:

    result = await session.execute(
        select(File).where(File.server_filename == server_filename)
    )
    return result.scalar_one_or_none()


async def db_delete_files(
    files: list[str], user_id: int, deleted_bytes: int, session: AsyncSession
) -> None:
    if files:
        result = await session.execute(
            delete(File).where(File.owner == user_id, File.server_filename.in_(files))
        )
        if result.rowcount != len(files):
            await session.rollback()
            raise HTTPException(409, "Содержимое каталога не совпадает с записями в базе")
        await update_user_storage_usage(user_id, -deleted_bytes, session)
        await session.commit()
