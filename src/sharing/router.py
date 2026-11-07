import shutil
from pathlib import Path
from typing import Annotated
from uuid import uuid4
from zipfile import ZipFile, ZIP_DEFLATED

from fastapi import APIRouter, File, HTTPException, UploadFile
from starlette.responses import FileResponse

from src.sharing.config import UFILES_DIR


FilesRouter = APIRouter(prefix="/sharing", tags=["sharing"])


@FilesRouter.post("/upload")
def upload_file(
    ufiles: Annotated[
        list[UploadFile],
        File(json_schema_extra={"items": {"type": "string", "format": "binary"}}),
    ],
):
    for upload in ufiles:
        name = upload.filename
        if not name or name in {".", ".."} or Path(name).name != name or "\\" in name or ":" in name or "\x00" in name:
            raise HTTPException(400, "Недопустимое имя файла")

    share_id = uuid4().hex
    directory = UFILES_DIR / share_id
    directory.mkdir(parents=True)
    try:
        if len(ufiles) == 1:
            upload = ufiles[0]
            with (directory / upload.filename).open("xb") as output:
                shutil.copyfileobj(upload.file, output, length=1024 * 1024)
        else:
            with ZipFile(directory / f"{share_id}.zip", "x", ZIP_DEFLATED) as archive:
                for upload in ufiles:
                    with archive.open(upload.filename, "w") as output:
                        shutil.copyfileobj(upload.file, output, length=1024 * 1024)
    except BaseException:
        shutil.rmtree(directory)
        raise
    return {"status": "200", "id": share_id}


@FilesRouter.get("/download/{id}")
def get_files(id: str):
    if len(id) != 32 or any(c not in "0123456789abcdef" for c in id):
        raise HTTPException(404, "Файл не найден")
    directory = UFILES_DIR / id
    if not directory.is_dir():
        raise HTTPException(404, "Файл не найден")
    file_path = next(directory.iterdir(), None)
    if file_path is None:
        raise HTTPException(404, "Файл не найден")
    return FileResponse(file_path, filename=file_path.name)
