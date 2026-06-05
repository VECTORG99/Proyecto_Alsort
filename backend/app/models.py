from pydantic import BaseModel
from typing import Literal, Any


class FilterCriterion(BaseModel):
    type: Literal[
        "year", "popularity", "duration_ms", "explicit",
        "artist", "album", "genre",
        "instrumentalness", "acousticness", "tempo", "workout"
    ]
    operator: Literal["=", ">", "<", ">=", "<=", "between", "contains"]
    value: Any


class FilterRequest(BaseModel):
    and_filters: list[FilterCriterion] = []
    or_filters: list[FilterCriterion] = []
    limit: int = 50
    offset: int = 0


class TrackOut(BaseModel):
    id: str
    track_id: str
    track_name: str
    artists: str
    album: str
    album_image_url: str | None
    duration_ms: int
    explicit: bool
    popularity: int
    genres: str | None
    year: int | None
    instrumentalness: float | None
    acousticness: float | None
    tempo: float | None

    model_config = {"from_attributes": True}


class FilterResponse(BaseModel):
    tracks: list[TrackOut]
    total: int
    limit: int
    offset: int


class CreatePlaylistRequest(BaseModel):
    name: str
    description: str = ""
    public: bool = True
    filter_criteria: FilterRequest


class UserOut(BaseModel):
    id: str
    spotify_id: str
    display_name: str | None
    email: str | None
