from fastapi import APIRouter, Request, status
import hashlib

from src.database.database import Session
from src.users.schemas import UserCreate, UserIn
from src.users.jwt import create_jwt
from src.users.database import get_user
from src.users.models import User
from src.users.user_manager import CurrentUser

UsersRouter = APIRouter(
    prefix="/users",
)

@UsersRouter.post("/registration", status_code=status.HTTP_201_CREATED, tags=["registration"])
async def registration(
        data: UserCreate,
        session: Session
):
    password_hash = hashlib.sha256(
        data.password.encode("utf-8")
    ).hexdigest()

    user = User(
        username=data.username,
        email=data.email,
        password=password_hash
    )
    session.add(user)
    await session.commit()

    create_jwt(user.id)
    return {"status": "200"}

@UsersRouter.post("/login", tags=["login"])
async def login(
        data: UserIn,
        session: Session
):
    password_hash = hashlib.sha256(
        data.password.encode("utf-8")
    ).hexdigest()

    user = get_user(data.username, password_hash, session)
    create_jwt(user.id)
    return {"status": "200"}

@UsersRouter.post("/logout")
async def login(user: CurrentUser):
    # create_jwt(user.id)
    return {"status": "200"}