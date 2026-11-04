from uuid import uuid4

from src.catalogs.config import UCATALOGS_DIR


async def create_directory() -> str:
    name_directory = uuid4().hex
    directory = UCATALOGS_DIR / name_directory
    directory.mkdir(parents=True, exist_ok=True)
    return name_directory
