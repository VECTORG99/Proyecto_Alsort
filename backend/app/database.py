from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, Integer, Text, JSON, DateTime, Boolean
from datetime import datetime, timezone
from alembic.config import Config
from alembic import command
import uuid
import os

from .config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    spotify_id: Mapped[str] = mapped_column(String(64), unique=True)
    display_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    email: Mapped[str | None] = mapped_column(String(128), nullable=True)
    access_token: Mapped[str] = mapped_column(Text)
    refresh_token: Mapped[str] = mapped_column(Text)
    token_expires_at: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class CachedTrack(Base):
    __tablename__ = "cached_tracks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    spotify_user_id: Mapped[str] = mapped_column(String(64), index=True)
    track_id: Mapped[str] = mapped_column(String(64))
    track_name: Mapped[str] = mapped_column(String(256))
    artists: Mapped[str] = mapped_column(Text)
    album: Mapped[str] = mapped_column(String(256))
    album_id: Mapped[str] = mapped_column(String(64))
    album_image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer)
    explicit: Mapped[bool] = mapped_column(Boolean)
    popularity: Mapped[int] = mapped_column(Integer)
    track_url: Mapped[str] = mapped_column(String(512))
    genres: Mapped[str | None] = mapped_column(Text, nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    audio_features: Mapped[str | None] = mapped_column(JSON, nullable=True)
    cached_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    spotify_user_id: Mapped[str] = mapped_column(String(64), index=True)
    spotify_playlist_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    filter_criteria: Mapped[str] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


async def init_db():
    try:
        alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
        command.upgrade(alembic_cfg, "head")
    except RuntimeError:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def get_session():
    async with async_session() as session:
        yield session
