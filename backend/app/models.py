from pydantic import BaseModel, field_validator
from typing import Literal, Any


RANGE_RULES: dict[str, dict] = {
    "year": {"min": 1900, "max": 2030},
    "popularity": {"min": 0, "max": 100},
    "instrumentalness": {"min": 0.0, "max": 1.0},
    "acousticness": {"min": 0.0, "max": 1.0},
    "tempo": {"min": 0, "max": 300},
}


class FilterCriterion(BaseModel):
    type: Literal[
        "year", "popularity", "duration_ms", "explicit",
        "artist", "album", "genre",
        "instrumentalness", "acousticness", "tempo", "workout"
    ]
    operator: Literal["=", ">", "<", ">=", "<=", "between", "contains"]
    value: Any

    @field_validator("value")
    @classmethod
    def validate_value_range(cls, v, info):
        values = info.data
        ft = values.get("type")
        if not ft or ft not in RANGE_RULES:
            return v
        rules = RANGE_RULES[ft]
        if isinstance(v, list):
            for item in v:
                if isinstance(item, (int, float)):
                    if item < rules["min"] or item > rules["max"]:
                        raise ValueError(
                            f"Value {item} out of range for {ft} ({rules['min']}-{rules['max']})"
                        )
        elif isinstance(v, (int, float)):
            if v < rules["min"] or v > rules["max"]:
                raise ValueError(
                    f"Value {v} out of range for {ft} ({rules['min']}-{rules['max']})"
                )
        return v


class FilterRequest(BaseModel):
    and_filters: list[FilterCriterion] = []
    or_filters: list[FilterCriterion] = []
    limit: int = 50
    offset: int = 0
    sort_by: Literal["year", "popularity", "duration_ms", "tempo", "energy", "danceability", "track_name", "artists"] | None = None
    sort_order: Literal["asc", "desc"] = "desc"


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
    energy: float | None
    danceability: float | None

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
