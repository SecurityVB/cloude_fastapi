from fastapi import FastAPI
from src.sharing.router import FilesRouter
from src.users.router import UsersRouter
from src.catalogs.router import CatalogsRouter


app = FastAPI()

app.include_router(FilesRouter)
app.include_router(UsersRouter)
app.include_router(CatalogsRouter)