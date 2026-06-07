from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .database import User, CachedTrack
from .spotify_client import SpotifyClient
from .models import FilterRequest, FilterCriterion, TrackOut
from .filters import apply_filters, _get_track_value, _apply_operator
from .logger import logger
import json


async def get_filtered_tracks(
    user: User,
    db: AsyncSession,
    filter_req: FilterRequest,
) -> tuple[list[TrackOut], int]:
    logger.debug("Loading cached tracks user=%s", user.spotify_id)
    result = await db.execute(
        select(CachedTrack).where(CachedTrack.spotify_user_id == user.spotify_id)
        .order_by(CachedTrack.cached_at.desc())
    )
    cached_tracks = result.scalars().all()

    if not cached_tracks:
        logger.info("No cached tracks found for user=%s, fetching from Spotify", user.spotify_id)
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

        features_dict = features or {}

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
            instrumentalness=features_dict.get("instrumentalness"),
            acousticness=features_dict.get("acousticness"),
            tempo=features_dict.get("tempo"),
            energy=features_dict.get("energy"),
            danceability=features_dict.get("danceability"),
        )
        track_outs.append(to)

    filtered = apply_filters(track_outs, filter_req.and_filters, filter_req.or_filters)

    total = len(filtered)
    offset = filter_req.offset
    limit = filter_req.limit
    paginated = filtered[offset : offset + limit]
    logger.debug("Filter result user=%s total=%d returned=%d", user.spotify_id, total, len(paginated))

    return paginated, total


SPOTIFY_PLAYLIST_MAX = 10000


async def create_playlist_from_filters(
    user: User,
    db: AsyncSession,
    name: str,
    description: str,
    public: bool,
    filter_req: FilterRequest,
) -> dict:
    logger.info("Creating playlist from filters user=%s name=%s", user.spotify_id, name)
    full_req = FilterRequest(
        and_filters=filter_req.and_filters,
        or_filters=filter_req.or_filters,
        limit=SPOTIFY_PLAYLIST_MAX,
        offset=0,
    )
    filtered_tracks, total_matched = await get_filtered_tracks(user, db, full_req)

    if not filtered_tracks:
        logger.warning("No tracks match filter criteria user=%s", user.spotify_id)
        raise ValueError("No tracks match the filter criteria")

    tracks_to_add = filtered_tracks[:SPOTIFY_PLAYLIST_MAX]
    total_added = len(tracks_to_add)

    if total_matched > SPOTIFY_PLAYLIST_MAX:
        logger.warning("Truncating playlist from %d to %d tracks", total_matched, SPOTIFY_PLAYLIST_MAX)

    client = SpotifyClient(user, db)
    track_uris = [f"spotify:track:{t.track_id}" for t in tracks_to_add]
    playlist = await client.create_playlist(name, description, public, track_uris)

    return {
        "playlist": playlist,
        "name": playlist.get("name", name),
        "total_matched": total_matched,
        "total_added": total_added,
        "truncated": total_matched > SPOTIFY_PLAYLIST_MAX,
    }
