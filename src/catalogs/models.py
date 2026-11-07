from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database.database import Base


class File(Base):
    __tablename__ = 'files'

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    server_filename: Mapped[str] = mapped_column(
        String(255), unique=True
    )
    path: Mapped[str] = mapped_column(String(550))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    owner: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )



