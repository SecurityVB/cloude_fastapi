from typing import Annotated
from uuid import uuid4
from fastapi import APIRouter, UploadFile, Request
from fastapi import File as UploadField

from catalogs.database import db_delete_files
from src.catalogs.utils import delete_files, get_filenames
from src.database.database import Session
from src.catalogs.models import File
from src.catalogs.config import UCATALOGS_DIR
from src.users.database import update_user_storage_usage
from src.users.user_manager import CurrentUser
from src.users.service import check_auth


CatalogsRouter = APIRouter(
    prefix="/catalogs",
    tags=["catalogs"]
)


@CatalogsRouter.post("/upload")
@check_auth()
async def get_files(
        request: Request,
        ufiles: Annotated[
            list[UploadFile],
            UploadField(json_schema_extra={"items": {"type": "string", "format": "binary"}}),
        ],
        path: str,
        user: CurrentUser,
        session: Session
):
    directory = UCATALOGS_DIR / user.directory / path if path != "/" else UCATALOGS_DIR / user.directory
    directory.mkdir(parents=True, exist_ok=True)
    created = []
    total_bytes = 0
    try:
        for ufile in ufiles:
            filename = uuid4().hex
            destination = directory / filename
            with destination.open("xb") as output:
                created.append(destination)
                while chunk := await ufile.read(1024 * 1024):
                    output.write(chunk)
                size_bytes = output.tell()

            total_bytes += size_bytes
            session.add(File(
                filename=ufile.filename,
                server_filename=filename,
                size_bytes=size_bytes,
                path=f"{user.directory}/{path}" if path != "/" else user.directory,
                owner=user.id,
            ))

        await update_user_storage_usage(user.id, total_bytes, session)
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
    path = UCATALOGS_DIR / user.directory / path if path != "/" else UCATALOGS_DIR / user.directory
    answer = await get_filenames(path, session)
    return {
        "status": "200",
        "files": answer
    }


@CatalogsRouter.post("/delete", tags=["catalogs"])
@check_auth()
async def delete_content(
        request: Request,
        path: str,
        user: CurrentUser,
        session: Session,
):
    files = await delete_files(path, user, session)
    return {"status": "200", "deleted_count": len(files)}
