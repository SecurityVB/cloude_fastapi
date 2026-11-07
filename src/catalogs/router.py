from typing import Annotated
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, HTTPException, UploadFile, Request
from fastapi import File as UploadField
from sqlalchemy import select

from src.catalogs.config import UCATALOGS_DIR
from src.catalogs.utils import catalog_path, delete_files, get_filenames
from src.database.database import Session
from src.catalogs.models import File
from src.users.database import available_bytes, reserve_upload_bytes
from src.users.user_manager import CurrentUser
from src.users.service import check_auth


CatalogsRouter = APIRouter(
    prefix="/catalogs",
    tags=["catalogs"]
)


@CatalogsRouter.get("/quota")
async def get_quota(user: CurrentUser, session: Session):
    return {"available_bytes": await available_bytes(user.id, session)}


@CatalogsRouter.post("/upload")
@check_auth()
async def upload_files(
        request: Request,
        ufiles: Annotated[
            list[UploadFile],
            UploadField(json_schema_extra={"items": {"type": "string", "format": "binary"}}),
        ],
        path: str,
        user: CurrentUser,
        session: Session
):
    directory = catalog_path(user, path)
    folder = directory.relative_to(UCATALOGS_DIR)
    names = set()
    total_bytes = 0
    for ufile in ufiles:
        if ufile.filename in names:
            raise HTTPException(409, f"Файл «{ufile.filename}» указан дважды для каталога «{path}»")
        names.add(ufile.filename)
        if ufile.size is None:
            raise HTTPException(400, "Не удалось определить размер файла")
        total_bytes += ufile.size

    created = []
    try:
        if not await reserve_upload_bytes(user.id, total_bytes, session):
            raise HTTPException(413, "Недостаточно места для загрузки")
        existing = await session.execute(
            select(File.filename, File.path).where(File.owner == user.id, File.filename.in_(names))
        )
        for name, stored_path in existing:
            if Path(stored_path) == folder:
                raise HTTPException(409, f"Файл «{name}» уже существует в каталоге «{path}»")
        directory.mkdir(parents=True, exist_ok=True)
        for ufile in ufiles:
            filename = uuid4().hex
            destination = directory / filename
            with destination.open("xb") as output:
                created.append(destination)
                while chunk := await ufile.read(1024 * 1024):
                    output.write(chunk)
                size_bytes = output.tell()

            if size_bytes != ufile.size:
                raise HTTPException(400, "Размер записанного файла отличается от полученного")
            session.add(File(
                filename=ufile.filename,
                server_filename=filename,
                size_bytes=size_bytes,
                path=str(folder),
                owner=user.id,
            ))

        await session.commit()
    except BaseException:
        await session.rollback()
        for destination in created:
            destination.unlink(missing_ok=True)
        raise

    return {
        "status": "200"
    }


@CatalogsRouter.post("/get", tags=["catalogs"])
@check_auth()
async def get_content(
        request: Request,
        path: str,
        user: CurrentUser,
        session: Session
):
    path = catalog_path(user, path)
    answer = await get_filenames(path, session)
    return {
        "status": "200",
        "files": answer,
    }


@CatalogsRouter.post("/delete", tags=["catalogs"])
@check_auth()
async def delete_content(
        request: Request,
        path: str,
        user: CurrentUser,
        session: Session,
        file_id: int | None = None,
):
    files = await delete_files(path, user, session, file_id)
    return {"status": "200", "deleted_count": len(files)}
