from typing import Any, Literal

from .models import FilterCriterion, TrackOut

SORT_FIELDS = {"year", "popularity", "duration_ms", "tempo", "energy", "danceability", "track_name", "artists"}


def sort_tracks(
    tracks: list[TrackOut],
    sort_by: str | None,
    sort_order: Literal["asc", "desc"],
) -> list[TrackOut]:
    if sort_by not in SORT_FIELDS:
        return tracks

    reverse = sort_order == "desc"

    def key_fn(t: TrackOut) -> Any:
        v = getattr(t, sort_by, None)
        if v is None:
            return "" if isinstance(getattr(t, sort_by, None), str) else -1
        return v

    return sorted(tracks, key=key_fn, reverse=reverse)


def _get_track_value(track: TrackOut, filter_type: str) -> Any:
    if filter_type == "year":
        return track.year
    elif filter_type == "popularity":
        return track.popularity
    elif filter_type == "duration_ms":
        return track.duration_ms
    elif filter_type == "explicit":
        return track.explicit
    elif filter_type == "artist":
        return track.artists.lower() if track.artists else ""
    elif filter_type == "album":
        return track.album.lower() if track.album else ""
    elif filter_type == "genre":
        return track.genres.lower() if track.genres else ""
    elif filter_type == "instrumentalness":
        return track.instrumentalness
    elif filter_type == "acousticness":
        return track.acousticness
    elif filter_type == "tempo":
        return track.tempo
    elif filter_type == "workout":
        return bool(
            track.energy is not None
            and track.tempo is not None
            and track.danceability is not None
            and track.energy > 0.7
            and track.tempo > 120
            and track.danceability > 0.6
        )
    return None


def _apply_operator(value: Any, operator: str, target: Any) -> bool:
    if value is None:
        return False

    if operator == "=":
        if isinstance(value, str):
            return value == str(target).lower()
        return value == target
    elif operator == ">":
        return isinstance(value, (int, float)) and value > float(target)
    elif operator == "<":
        return isinstance(value, (int, float)) and value < float(target)
    elif operator == ">=":
        return isinstance(value, (int, float)) and value >= float(target)
    elif operator == "<=":
        return isinstance(value, (int, float)) and value <= float(target)
    elif operator == "between":
        if isinstance(target, list) and len(target) == 2:
            return isinstance(value, (int, float)) and float(target[0]) <= value <= float(target[1])
        return False
    elif operator == "contains":
        return isinstance(value, str) and str(target).lower() in value
    return False


def apply_filters(
    tracks: list[TrackOut],
    and_filters: list[FilterCriterion],
    or_filters: list[FilterCriterion],
    sort_by: str | None = None,
    sort_order: Literal["asc", "desc"] = "desc",
) -> list[TrackOut]:
    if not and_filters and not or_filters and not sort_by:
        return tracks

    result = tracks
    if and_filters or or_filters:
        result = []
        for track in tracks:
            and_pass = True
            or_pass = False

            if and_filters:
                for criterion in and_filters:
                    value = _get_track_value(track, criterion.type)
                    if not _apply_operator(value, criterion.operator, criterion.value):
                        and_pass = False
                        break

            if or_filters:
                for criterion in or_filters:
                    value = _get_track_value(track, criterion.type)
                    if _apply_operator(value, criterion.operator, criterion.value):
                        or_pass = True
                        break
            else:
                or_pass = True

            if and_pass and or_pass:
                result.append(track)

    if sort_by:
        result = sort_tracks(result, sort_by, sort_order)

    return result
