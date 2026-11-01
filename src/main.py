from fastapi import FastAPI

from src.files.router import FilesRouter
from src.users.router import UsersRouter


app = FastAPI()
from typing import Annotated
from fastapi import Depends

CurrentUser = Annotated[User, Depends(get_current_user)]

app.include_router(FilesRouter)
app.include_router(UsersRouter)