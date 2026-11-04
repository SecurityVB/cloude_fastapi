from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalogs.models import File


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