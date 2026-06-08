import asyncio
import httpx
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .database import User, CachedTrack
from .auth import refresh_spotify_token
from .logger import logger


RETRYABLE_STATUSES = {429, 502, 503, 504}
MAX_RETRIES = 3
RATE_LIMIT_MAX = 280
RATE_LIMIT_WINDOW = 60


class SpotifyClient:
    def __init__(self, user: User, db: AsyncSession):
        self.user = user
        self.db = db
        self._base_url = "https://api.spotify.com/v1"
        self._request_timestamps: list[float] = []
        self._rate_lock = asyncio.Lock()
        self._client = httpx.AsyncClient()

    async def _ensure_token(self):
        if datetime.now(timezone.utc).timestamp() > self.user.token_expires_at:
            await refresh_spotify_token(self.user, self.db)

    async def _get_headers(self) -> dict:
        await self._ensure_token()
        return {"Authorization": f"Bearer {self.user.access_token}"}

    async def _rate_limit_wait(self):
        async with self._rate_lock:
            now = asyncio.get_event_loop().time()
            cutoff = now - RATE_LIMIT_WINDOW
            self._request_timestamps = [t for t in self._request_timestamps if t > cutoff]

            if len(self._request_timestamps) >= RATE_LIMIT_MAX:
                wait = self._request_timestamps[0] - cutoff
                if wait > 0:
                    await asyncio.sleep(wait)
                self._request_timestamps = [t for t in self._request_timestamps if t > asyncio.get_event_loop().time() - RATE_LIMIT_WINDOW]

    async def _request(
        self,
        method: str,
        path: str,
        max_retries: int = MAX_RETRIES,
        **kwargs,
    ) -> httpx.Response:
        url = f"{self._base_url}{path}" if path.startswith("/") else f"{self._base_url}/{path}"
        headers = await self._get_headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        for attempt in range(max_retries + 1):
            await self._rate_limit_wait()

            try:
                resp = await self._client.request(method, url, headers=headers, **kwargs)
            except (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError) as e:
                if attempt < max_retries:
                    wait = 2 ** attempt
                    logger.warning("Request failed (attempt %d/%d) %s %s: %s. Retrying in %ds",
                                   attempt + 1, max_retries, method, path, e, wait)
                    await asyncio.sleep(wait)
                    continue
                logger.error("Request failed after %d retries %s %s: %s", max_retries, method, path, e)
                raise Exception(f"Spotify API request failed after {max_retries} retries: {e}")

            self._request_timestamps.append(asyncio.get_event_loop().time())

            if resp.status_code == 429 and attempt < max_retries:
                retry_after = int(resp.headers.get("Retry-After", 2 ** attempt))
                logger.warning("Rate limited (429) %s %s. Waiting %ds (attempt %d/%d)",
                               method, path, retry_after, attempt + 1, max_retries)
                await asyncio.sleep(retry_after)
                continue

            if resp.status_code in RETRYABLE_STATUSES and attempt < max_retries:
                wait = 2 ** attempt
                logger.warning("Retryable status %d %s %s (attempt %d/%d). Waiting %ds",
                               resp.status_code, method, path, attempt + 1, max_retries, wait)
                await asyncio.sleep(wait)
                continue

            return resp

        raise Exception(f"Spotify API error: {resp.status_code} {resp.text}")

    async def fetch_all_liked_tracks(self) -> list[dict]:
        tracks = []
        offset = 0
        limit = 50
        total = None

        logger.info("Fetching liked tracks from Spotify")

        while True:
            resp = await self._request("GET", "/me/tracks", params={"limit": limit, "offset": offset})
            if resp.status_code != 200:
                raise Exception(f"Spotify API error: {resp.status_code} {resp.text}")

            data = resp.json()
            if total is None:
                total = data.get("total", 0)
                logger.info("Total liked tracks: %d", total)

            items = data.get("items", [])
            if not items:
                break

            for item in items:
                track = item.get("track", {})
                if track:
                    tracks.append(track)

            logger.debug("Fetched %d/%d tracks", len(tracks), total)
            if len(tracks) >= total:
                break
            offset += limit

        logger.info("Fetched %d liked tracks total=%d", len(tracks), total or 0)
        return tracks

    async def fetch_audio_features(self, track_ids: list[str]) -> dict[str, dict]:
        features_map: dict[str, dict] = {}
        logger.info("Fetching audio features for %d tracks", len(track_ids))

        for i in range(0, len(track_ids), 100):
            batch = track_ids[i : i + 100]
            resp = await self._request("GET", "/audio-features", params={"ids": ",".join(batch)})
            if resp.status_code == 200:
                af_data = resp.json()
                for af in af_data.get("audio_features", []):
                    if af and af.get("id"):
                        features_map[af["id"]] = af

        logger.info("Fetched audio features for %d tracks", len(features_map))
        return features_map

    async def fetch_artist_genres(self, artist_ids: list[str]) -> dict[str, list[str]]:
        genres_map: dict[str, list[str]] = {}
        logger.info("Fetching genres for %d artists", len(artist_ids))

        for i in range(0, len(artist_ids), 50):
            batch = artist_ids[i : i + 50]
            resp = await self._request("GET", "/artists", params={"ids": ",".join(batch)})
            if resp.status_code == 200:
                artists_data = resp.json()
                for artist in artists_data.get("artists", []):
                    if artist and artist.get("id"):
                        genres_map[artist["id"]] = artist.get("genres", [])

        logger.info("Fetched genres for %d artists", len(genres_map))
        return genres_map

    async def create_playlist(self, name: str, description: str, public: bool, track_uris: list[str]) -> dict:
        logger.info("Creating Spotify playlist name=%s tracks=%d", name, len(track_uris))

        playlist_resp = await self._request(
            "POST",
            "/me/playlists",
            json={"name": name, "description": description, "public": public},
        )
        if playlist_resp.status_code not in (200, 201):
            raise Exception(f"Failed to create playlist: {playlist_resp.text}")

        playlist = playlist_resp.json()
        playlist_id = playlist["id"]
        logger.info("Playlist created id=%s name=%s", playlist_id, name)

        for i in range(0, len(track_uris), 100):
            batch = track_uris[i : i + 100]
            await self._request(
                "POST",
                f"/playlists/{playlist_id}/tracks",
                json={"uris": batch},
            )
            logger.debug("Added %d/%d tracks to playlist", i + len(batch), len(track_uris))

        logger.info("Playlist %s populated with %d tracks", playlist_id, len(track_uris))
        return playlist

    async def cache_tracks(self, tracks: list[dict], user_spotify_id: str):
        logger.info("Caching %d tracks for user=%s", len(tracks), user_spotify_id)
        all_artist_ids = []
        for track in tracks:
            for artist in track.get("artists", []):
                if artist.get("id"):
                    all_artist_ids.append(artist["id"])
        all_artist_ids = list(set(all_artist_ids))
        genres_map = await self.fetch_artist_genres(all_artist_ids)

        track_ids = [t["id"] for t in tracks if t.get("id")]
        features_map = await self.fetch_audio_features(track_ids)

        existing_result = await self.db.execute(
            select(CachedTrack).where(
                CachedTrack.track_id.in_(track_ids),
                CachedTrack.spotify_user_id == user_spotify_id,
            )
        )
        existing_tracks = {ct.track_id: ct for ct in existing_result.scalars().all()}

        for track in tracks:
            tid = track.get("id")
            if not tid:
                continue

            artist_names = ", ".join(a["name"] for a in track.get("artists", []))
            artist_ids = [a["id"] for a in track.get("artists", []) if a.get("id")]

            track_genres = set()
            for aid in artist_ids:
                track_genres.update(genres_map.get(aid, []))
            genres_str = ", ".join(sorted(track_genres))

            year = None
            release_date = (track.get("album") or {}).get("release_date", "")
            if release_date and len(release_date) >= 4:
                try:
                    year = int(release_date[:4])
                except ValueError:
                    year = None

            images = (track.get("album") or {}).get("images", [])
            album_image_url = images[0]["url"] if images else None
            album_name = (track.get("album") or {}).get("name", "")
            album_id = (track.get("album") or {}).get("id", "")

            features = features_map.get(tid)

            existing_track = existing_tracks.get(tid)

            if existing_track:
                existing_track.track_name = track["name"]
                existing_track.artists = artist_names
                existing_track.album = album_name
                existing_track.album_id = album_id
                existing_track.album_image_url = album_image_url
                existing_track.duration_ms = track.get("duration_ms", 0)
                existing_track.explicit = track.get("explicit", False)
                existing_track.popularity = track.get("popularity", 0)
                existing_track.track_url = track.get("external_urls", {}).get("spotify", "")
                existing_track.genres = genres_str
                existing_track.year = year
                existing_track.audio_features = features
            else:
                cached = CachedTrack(
                    spotify_user_id=user_spotify_id,
                    track_id=tid,
                    track_name=track["name"],
                    artists=artist_names,
                    album=album_name,
                    album_id=album_id,
                    album_image_url=album_image_url,
                    duration_ms=track.get("duration_ms", 0),
                    explicit=track.get("explicit", False),
                    popularity=track.get("popularity", 0),
                    track_url=track.get("external_urls", {}).get("spotify", ""),
                    genres=genres_str,
                    year=year,
                    audio_features=features,
                )
                self.db.add(cached)

        await self.db.commit()
