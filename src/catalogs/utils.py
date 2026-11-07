import shutil
from pathlib import Path
from tempfile import mkdtemp
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from src.catalogs.database import db_delete_files, get_filename
from src.catalogs.models import File
from src.users.models import User
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


async def delete_files(path: str, user: User, session: AsyncSession) -> list[str]:
    root = UCATALOGS_DIR / user.directory
    relative = Path(path)
    if path != "/" and (relative.is_absolute() or not relative.parts or ".." in relative.parts):
        raise HTTPException(400, "Укажи путь внутри своего каталога")

    target = root if path == "/" else root / relative

    try:
        if target == root:
            targets = list(root.iterdir())
        elif target.is_dir():
            targets = [target]
        else:
            rows = await session.execute(select(File.server_filename, File.path).where(
                File.owner == user.id, File.filename == relative.name,
            ))
            parent = Path(user.directory) / relative.parent
            targets = [target.with_name(name) for name, folder in rows if Path(folder) == parent]
            if not targets:
                raise HTTPException(404, "Файл или каталог не найден")

        if not targets:
            return []

        staging = Path(mkdtemp(prefix=".deleting-", dir=UCATALOGS_DIR))
        moved = []
        files = []
        deleted_bytes = 0
        try:
            for source in targets:
                staged = staging / source.name
                source.rename(staged)
                moved.append((source, staged))
                if staged.is_dir():
                    for directory, _, names in staged.walk(on_error=_raise_walk_error):
                        for name in names:
                            deleted_bytes += (directory / name).stat().st_size
                            files.append(name)
                else:
                    deleted_bytes += staged.stat().st_size
                    files.append(staged.name)
            await db_delete_files(files, user.id, deleted_bytes, session)
        except BaseException:
            for source, staged in reversed(moved):
                staged.rename(source)
            staging.rmdir()
            raise

        await run_in_threadpool(shutil.rmtree, staging)
        return files
    except FileNotFoundError:
        raise HTTPException(404, "Файл или каталог не найден")
    except PermissionError:
        raise HTTPException(403, "Нет доступа для удаления")


def _raise_walk_error(error: OSError) -> None:
    raise error
