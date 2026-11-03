from uuid import uuid4
from fastapi import APIRouter, UploadFile

from src.database.database import Session
from src.catalogs.models import File
from src.catalogs.config import UCATALOGS_DIR
from src.users.user_manager import CurrentUser


CatalogsRouter = APIRouter(
    prefix="/catalogs",
)


# add a decorator that checks the user for authentication and authorization
@CatalogsRouter.get("/upload", tags=["catalogs"]) # add param - choice of directory for files
async def get_directories(
        ufiles: list[UploadFile],
        user: CurrentUser,
        session: Session
):
    directory = UCATALOGS_DIR / user.directory
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

# add a decorator that checks the user for authentication and authorization
@CatalogsRouter.get("/get", tags=["catalogs"]) # add param - choice of directory for files
async def get_content(
        user: CurrentUser,
):
    pass