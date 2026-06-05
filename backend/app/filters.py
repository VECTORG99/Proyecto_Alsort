import json
from typing import Any

from .models import FilterCriterion, TrackOut


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
        energy = track.instrumentalness
        tempo = track.tempo
        danceability = 0.0
        if hasattr(track, "audio_features") and track.audio_features:
            af = json.loads(track.audio_features) if isinstance(track.audio_features, str) else track.audio_features
            energy = af.get("energy", 0)
            danceability = af.get("danceability", 0)
            tempo = af.get("tempo", 0)
        else:
            pass
        return (energy is not None and tempo is not None and
                energy is not None and
                energy > 0.7 and tempo > 120 and danceability > 0.6)
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


def apply_filters(tracks: list[TrackOut], and_filters: list[FilterCriterion], or_filters: list[FilterCriterion]) -> list[TrackOut]:
    if not and_filters and not or_filters:
        return tracks

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

    return result
