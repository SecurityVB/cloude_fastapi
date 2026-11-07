from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import Role, User


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

async def reserve_upload_bytes(user_id: int, size: int, session: AsyncSession) -> bool:
    result = await session.scalar(
        update(User)
        .where(User.id == user_id, User.role == Role.name,
               size <= Role.limit_bytes - User.used_bytes)
        .values(used_bytes=User.used_bytes + size)
        .returning(User.id)
        .execution_options(synchronize_session=False)
    )
    return result is not None


async def available_bytes(user_id: int, session: AsyncSession) -> int:
    result = await session.execute(
        select(Role.limit_bytes - User.used_bytes)
        .join_from(User, Role, User.role == Role.name)
        .where(User.id == user_id)
    )
    return max(0, result.scalar_one())
