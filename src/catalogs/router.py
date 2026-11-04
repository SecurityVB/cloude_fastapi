from typing import Annotated
from uuid import uuid4
from fastapi import APIRouter, UploadFile, Request
from fastapi import File as UploadField

from src.catalogs.utils import get_filenames
from src.database.database import Session
from src.catalogs.models import File
from src.catalogs.config import UCATALOGS_DIR
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
    for ufile in ufiles:
        file = ufile.file
        filename = uuid4().hex

        directory.mkdir(parents=True, exist_ok=True)
        with open(directory / filename, 'wb') as f:
            f.write(file.read())

        _file = File(
            filename=ufile.filename,
            server_filename=filename,
            path=f"{user.directory}/{path}" if path else user.directory,
            owner=user.id
        )
        session.add(_file)
        await session.commit()

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
