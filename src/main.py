from fastapi import FastAPI
from src.config import MAX_UPLOAD_REQUEST_BYTES
from src.upload_limit import UploadSizeLimit
from src.sharing.router import FilesRouter
from src.users.router import UsersRouter
from src.catalogs.router import CatalogsRouter


app = FastAPI()
app.add_middleware(UploadSizeLimit, max_bytes=MAX_UPLOAD_REQUEST_BYTES)

app.include_router(FilesRouter)
app.include_router(UsersRouter)
app.include_router(CatalogsRouter)