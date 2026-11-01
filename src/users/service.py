from typing import Annotated

from fastapi import Depends, Cookie, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.jwt import verify_jwt
from src.database import get_session
from src.users.models import User


async def get_current_user(
    access_token: Annotated[str | None, Cookie()] = None,
    session: AsyncSession = Depends(get_session)
) -> User:

    if access_token is None:
        raise HTTPException(401, "Не авторизован")

    try:
        payload = verify_jwt(access_token)
        user_id = int(payload["sub"])
    except (ValueError, TypeError, KeyError, OverflowError):
        raise HTTPException(401, "Недействительный токен")

    user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(401, "Пользователь не найден")

    return user