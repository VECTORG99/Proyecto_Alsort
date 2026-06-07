from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .config import settings
from .database import init_db, get_session, User
from .auth import router as auth_router
from .models import FilterRequest, CreatePlaylistRequest, TrackOut
from .playlist_manager import get_filtered_tracks, create_playlist_from_filters
from .logger import setup_logging, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting up Alsort API")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down Alsort API")


app = FastAPI(title="Alsort API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("Request %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("Response %s %s -> %s", request.method, request.url.path, response.status_code)
    return response


async def get_current_user(request: Request, db: AsyncSession = Depends(get_session)) -> User:
    session_id = request.headers.get("X-Session-Id") or request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await db.execute(select(User).where(User.id == session_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    return user


@app.post("/api/tracks/filter")
async def filter_tracks(
    filter_req: FilterRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    logger.info("Filtering tracks user=%s and_filters=%d or_filters=%d",
                user.spotify_id, len(filter_req.and_filters), len(filter_req.or_filters))
    tracks, total = await get_filtered_tracks(user, db, filter_req)
    logger.info("Filter result user=%s total=%d returned=%d",
                user.spotify_id, total, len(tracks))
    return {
        "tracks": [t.model_dump() for t in tracks],
        "total": total,
        "limit": filter_req.limit,
        "offset": filter_req.offset,
    }


@app.post("/api/tracks/sync")
async def sync_tracks(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    from .spotify_client import SpotifyClient

    logger.info("Starting sync user=%s", user.spotify_id)
    client = SpotifyClient(user, db)
    tracks_data = await client.fetch_all_liked_tracks()
    await client.cache_tracks(tracks_data, user.spotify_id)
    logger.info("Sync complete user=%s total=%d", user.spotify_id, len(tracks_data))
    return {"synced": len(tracks_data)}


@app.post("/api/playlists")
async def create_playlist(
    req: CreatePlaylistRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    logger.info("Creating playlist user=%s name=%s", user.spotify_id, req.name)
    try:
        result = await create_playlist_from_filters(
            user, db, req.name, req.description, req.public, req.filter_criteria
        )
        logger.info("Playlist created user=%s name=%s added=%d",
                    user.spotify_id, result["name"], result["total_added"])
        return result
    except ValueError as e:
        logger.warning("Playlist creation failed user=%s error=%s", user.spotify_id, str(e))
        raise HTTPException(status_code=400, detail=str(e))
