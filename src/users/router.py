from fastapi import APIRouter, HTTPException, Request, Response, status
import hashlib

from src.catalogs.utils import create_directory
from src.database.database import Session
from src.users.schemas import UserCreate, UserIn

from src.users.database import get_user
from src.users.models import User
from src.users.service import set_auth_cookie

UsersRouter = APIRouter(
    prefix="/users",
)


@UsersRouter.post("/registration", status_code=status.HTTP_201_CREATED, tags=["registration"])
async def registration(
        data: UserCreate,
        request: Request,
        response: Response,
        session: Session
):
    password_hash = hashlib.sha256(
        data.password.encode("utf-8")
    ).hexdigest()

    directory = await create_directory()

    user = User(
        username=data.username,
        email=data.email,
        password=password_hash,
        directory=directory
    )
    session.add(user)
    await session.commit()

    set_auth_cookie(response, request, user.id)
    return {"status": "200"}

@UsersRouter.get("/login", tags=["login"])
async def login_info():
    return {"detail": "Для входа отправьте username и password в JSON на POST /users/login"}


@UsersRouter.post("/login", tags=["login"])
async def login(
        data: UserIn,
        request: Request,
        response: Response,
        session: Session
):
    password_hash = hashlib.sha256(
        data.password.encode("utf-8")
    ).hexdigest()

    user = await get_user(data.username, password_hash, session)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный логин или пароль")

    set_auth_cookie(response, request, user.id)
    return {"status": "200"}

@UsersRouter.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    return {"status": "200"}
