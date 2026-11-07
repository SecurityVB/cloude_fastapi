from sqlalchemy import select, update
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


async def update_user_storage_usage(user_id: int, delta_bytes: int, session: AsyncSession) -> None:
    if delta_bytes:
        await session.execute(
            update(User).where(User.id == user_id)
            .values(used_bytes=User.used_bytes + delta_bytes)
        )
