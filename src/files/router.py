import hashlib
import shutil
import time
from zipfile import ZipFile, ZIP_DEFLATED

from fastapi import APIRouter, UploadFile
from starlette.responses import FileResponse

from src.files.config import UFILES_DIR


FilesRouter = APIRouter(
    prefix="/files",
)

@FilesRouter.post("/upload")
async def upload_file(ufiles: list[UploadFile]):
    id_for_files = hashlib.md5(str(time.time()).encode("utf-8")).hexdigest()
    directory = UFILES_DIR / id_for_files
    if len(ufiles) <= 1:
        for ufile in ufiles:
            file = ufile.file
            filename = ufile.filename
            directory.mkdir(parents=True, exist_ok=True)
            with open(directory / filename, 'wb') as f:
                f.write(file.read())
    else:
        directory.mkdir(parents=True, exist_ok=True)
        with ZipFile(directory / f"{id_for_files}.zip", "w", ZIP_DEFLATED) as archive:
            for ufile in ufiles:
                filename = ufile.filename

                with archive.open(filename, "w") as archive_file:
                    shutil.copyfileobj(ufile.file, archive_file)

    return {
        "status": True,
        "id": id_for_files,
    }

@FilesRouter.get("/files/download/{id}")
async def get_files(id: str):
    directory = UFILES_DIR / id
    file_path = next(directory.iterdir())
    return FileResponse(
        path=file_path,
        filename=file_path.name
    )