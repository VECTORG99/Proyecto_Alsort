from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .database import User, CachedTrack
from .spotify_client import SpotifyClient
from .models import FilterRequest, FilterCriterion, TrackOut
from .filters import apply_filters, _get_track_value, _apply_operator
import json


async def get_filtered_tracks(
    user: User,
    db: AsyncSession,
    filter_req: FilterRequest,
) -> tuple[list[TrackOut], int]:
    result = await db.execute(
        select(CachedTrack).where(CachedTrack.spotify_user_id == user.spotify_id)
        .order_by(CachedTrack.cached_at.desc())
    )
    cached_tracks = result.scalars().all()

    if not cached_tracks:
        client = SpotifyClient(user, db)
        tracks_data = await client.fetch_all_liked_tracks()
        await client.cache_tracks(tracks_data, user.spotify_id)

        result = await db.execute(
            select(CachedTrack).where(CachedTrack.spotify_user_id == user.spotify_id)
        )
        cached_tracks = result.scalars().all()

    track_outs = []
    for ct in cached_tracks:
        af = ct.audio_features
        features = json.loads(af) if isinstance(af, str) else af

        to = TrackOut(
            id=ct.id,
            track_id=ct.track_id,
            track_name=ct.track_name,
            artists=ct.artists,
            album=ct.album,
            album_image_url=ct.album_image_url,
            duration_ms=ct.duration_ms,
            explicit=bool(ct.explicit),
            popularity=ct.popularity,
            genres=ct.genres,
            year=ct.year,
            instrumentalness=features.get("instrumentalness") if features else None,
            acousticness=features.get("acousticness") if features else None,
            tempo=features.get("tempo") if features else None,
        )
        track_outs.append(to)

    filtered = apply_filters(track_outs, filter_req.and_filters, filter_req.or_filters)

    total = len(filtered)
    offset = filter_req.offset
    limit = filter_req.limit
    paginated = filtered[offset : offset + limit]

    return paginated, total


async def create_playlist_from_filters(
    user: User,
    db: AsyncSession,
    name: str,
    description: str,
    public: bool,
    filter_req: FilterRequest,
) -> dict:
    filtered_tracks, _ = await get_filtered_tracks(user, db, filter_req)

    if not filtered_tracks:
        raise ValueError("No tracks match the filter criteria")

    client = SpotifyClient(user, db)
    track_uris = [f"spotify:track:{t.track_id}" for t in filtered_tracks]

    playlist = await client.create_playlist(name, description, public, track_uris)
    return playlist
