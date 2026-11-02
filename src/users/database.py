from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User


async def get_user(
    username: str,
    password: str,
    session: AsyncSession
) -> User | None:

    result = await session.execute(
        select(User).where(User.username == username, User.password == password)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return None
    return user
