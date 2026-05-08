from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)

    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    offer_accepted: Mapped[bool] = mapped_column(Boolean, default=False)

    phone_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    tg_first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tg_last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tg_username: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
