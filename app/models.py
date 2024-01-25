import os
import datetime
import json

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncAttrs,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, String, func


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5431")
POSTGRES_USER = os.getenv("POSTGRES_USER", "app")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")
POSTGRES_DB = os.getenv("POSTGRES_DB", "app")
POSTGRES_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_async_engine(POSTGRES_URL, echo=True)
Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Advert(Base):
    __tablename__ = "app_adverts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    description: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    owner_id: Mapped[int] = mapped_column(nullable=False)

    @property
    def dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "owner_id": self.owner_id,
        }

    @property
    def to_json(self):
        return json.dumps(self.dict, cls=CustomJSONEncoder)


class User(Base):
    __tablename__ = "app_users"
    id: Mapped[int] = mapped_column(primary_key=True)
    mail: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(100), nullable=False)

    @property
    def dict(self) -> dict:
        return {"id": self.id, "mail": self.mail, "password": self.password}


async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
