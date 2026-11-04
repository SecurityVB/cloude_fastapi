import os
from uuid import uuid4
from fastapi import APIRouter, UploadFile, Request

from src.database.database import Session
from src.catalogs.models import File
from src.catalogs.config import UCATALOGS_DIR
from src.users.user_manager import CurrentUser
from src.users.service import check_auth


CatalogsRouter = APIRouter(
    prefix="/catalogs",
)


@check_auth()
@CatalogsRouter.get("/upload/{path}", tags=["catalogs"])
async def get_files(
        request: Request,
        ufiles: list[UploadFile],
        path: str,
        user: CurrentUser,
        session: Session
):
    directory = UCATALOGS_DIR / user.directory / path
    for ufile in ufiles:
        file = ufile.file
        filename = uuid4().hex

        directory.mkdir(parents=True, exist_ok=True)
        with open(directory / filename, 'wb') as f:
            f.write(file.read())

        _file = File(
            filename=ufile.filename,
            server_filename=filename,
            catalog=directory,
            owner=user.id
        )
        session.add(_file)
        await session.commit()

    return {
        "status": "200"
    }

@check_auth()
@CatalogsRouter.get("/get/{path}", tags=["catalogs"])
async def get_content(
        request: Request,
        path: str,
        user: CurrentUser,
):
    answer = [file for _, _, file in os.walk(UCATALOGS_DIR / user.directory / path)]
    return {
        "status": "200",
        "files": "".join(answer)
    }