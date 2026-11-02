from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(30), unique=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True
    )
    password: Mapped[str] = mapped_column(
        String(255)
    )
    role_id: Mapped[str] = mapped_column(
        ForeignKey("roles.id"), default=1
    )


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    limit: Mapped[str] = mapped_column(String(7))