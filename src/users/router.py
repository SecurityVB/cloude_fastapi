from fastapi import APIRouter, Request

from src.users.schemas import UserCreate, UserIn
from users.jwt import create_jwt

UsersRouter = APIRouter(
    prefix="/users",
)

@UsersRouter.post("/registration", tags=["registration"])
async def registration(data: UserCreate, request: Request):
    user_id =
    create_jwt()
    return {"status": "200"}

@UsersRouter.post("/login", tags=["login"])
async def login(data: UserIn, request: Request):
    print(data.username)
    print(data.password)
    return {"status": "200"}