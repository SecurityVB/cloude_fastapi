from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalogs.models import File
from src.users.database import update_user_storage_usage


async def get_filename(
    server_filename: str,
    session: AsyncSession
) -> str | None:

    result = await session.execute(
        select(File).where(File.server_filename == server_filename)
    )
    file = result.scalar_one_or_none()
    if file is None:
        return None
    return file.filename


async def db_delete_files(
    files: list[str], user_id: int, deleted_bytes: int, session: AsyncSession
) -> None:
    if files:
        await session.execute(
            delete(File).where(File.owner == user_id, File.server_filename.in_(files))
        )
        await update_user_storage_usage(user_id, -deleted_bytes, session)
        await session.commit()
