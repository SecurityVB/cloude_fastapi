from fastapi import APIRouter, Request

from src.users.schemas import UserCreate, UserIn

UsersRouter = APIRouter(
    prefix="/users",
)

@UsersRouter.post("/registration", tags=["registration"])
async def registration(data: UserCreate, request: Request):
    print(data.username)
    print(data.password)
    print(data.email)
    return {"status": "200"}

@UsersRouter.post("/login", tags=["login"])
async def login(data: UserIn, request: Request):
    print(data.username)
    print(data.password)
    return {"status": "200"}