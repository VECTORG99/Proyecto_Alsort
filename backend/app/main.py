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


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Alsort API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


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
    tracks, total = await get_filtered_tracks(user, db, filter_req)
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

    client = SpotifyClient(user, db)
    tracks_data = await client.fetch_all_liked_tracks()
    await client.cache_tracks(tracks_data, user.spotify_id)
    return {"synced": len(tracks_data)}


@app.post("/api/playlists")
async def create_playlist(
    req: CreatePlaylistRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    try:
        result = await create_playlist_from_filters(
            user, db, req.name, req.description, req.public, req.filter_criteria
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
