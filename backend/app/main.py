import time
from collections import defaultdict
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import router as auth_router
from .config import settings
from .database import User, get_session, init_db
from .logger import logger, setup_logging
from .models import CreatePlaylistRequest, FilterRequest
from .playlist_manager import create_playlist_from_filters, get_filtered_tracks


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


RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX_REQUESTS = 10
_auth_rate_limits: dict[str, list[float]] = defaultdict(list)


@app.middleware("http")
async def auth_rate_limit(request: Request, call_next):
    if request.url.path.startswith("/auth/"):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        timestamps = _auth_rate_limits[client_ip]
        _auth_rate_limits[client_ip] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
        if len(_auth_rate_limits[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
            )
        _auth_rate_limits[client_ip].append(now)
    return await call_next(request)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "alsort-api"}


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
    try:
        tracks_data = await client.fetch_all_liked_tracks()
        await client.cache_tracks(tracks_data, user.spotify_id)
    finally:
        await client.close()
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
