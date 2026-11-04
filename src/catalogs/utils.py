from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.catalogs.database import get_filename
from src.catalogs.config import UCATALOGS_DIR


async def create_directory() -> str:
    name_directory = uuid4().hex
    directory = UCATALOGS_DIR / name_directory
    directory.mkdir(parents=True, exist_ok=True)
    return name_directory


async def get_filenames(path, session: AsyncSession) -> list[str]:
    answer = []
    for item in path.iterdir():
        if item.is_file():
            filename = await get_filename(item.name, session)
            if filename:
                answer.append(
                    filename
                )
        else:
            answer.append(item.name)
    return answer
