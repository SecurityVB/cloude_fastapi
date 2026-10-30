from fastapi import FastAPI

from src.files.router import FilesRouter
from src.users.router import UsersRouter


app = FastAPI()

app.include_router(FilesRouter)
app.include_router(UsersRouter)