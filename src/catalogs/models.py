from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database.database import Base


class File(Base):
    __tablename__ = 'files'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(30), unique=True
    )
    original_filename: Mapped[str] = mapped_column(String(255))
    server_filename: Mapped[str] = mapped_column(String(255))
    catalog: Mapped[str] = mapped_column(String(255))
    owner: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )



