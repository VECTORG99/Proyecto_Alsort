from app.models import FilterCriterion


def test_year_filter(tracks):
    criterion = FilterCriterion(type="year", operator=">", value=2020)
    from app.filters import apply_filters

    result = apply_filters(tracks, [criterion], [])
    assert len(result) == 2
    assert all(t.year is not None and t.year > 2020 for t in result)


def test_year_between(tracks):
    criterion = FilterCriterion(type="year", operator="between", value=[2016, 2023])
    from app.filters import apply_filters

    result = apply_filters(tracks, [criterion], [])
    assert len(result) == 2
    assert all(t.year is not None and 2016 <= t.year <= 2023 for t in result)


def test_popularity_filter(tracks):
    criterion = FilterCriterion(type="popularity", operator=">=", value=80)
    from app.filters import apply_filters

    result = apply_filters(tracks, [criterion], [])
    assert len(result) == 2
    assert all(t.popularity >= 80 for t in result)


def test_duration_filter(tracks):
    criterion = FilterCriterion(type="duration_ms", operator=">", value=300000)
    from app.filters import apply_filters

    result = apply_filters(tracks, [criterion], [])
    assert len(result) == 1
    assert result[0].track_id == "jkl"


def test_explicit_filter(tracks):
    criterion = FilterCriterion(type="explicit", operator="=", value=True)
    from app.filters import apply_filters

    result = apply_filters(tracks, [criterion], [])
    assert len(result) == 1
    assert result[0].track_id == "ghi"


def test_artist_contains(tracks):
    criterion = FilterCriterion(type="artist", operator="contains", value="folk")
    from app.filters import apply_filters

    result = apply_filters(tracks, [criterion], [])
    assert len(result) == 1
    assert "folk" in result[0].artists.lower()


def test_genre_contains(tracks):
    criterion = FilterCriterion(type="genre", operator="contains", value="rock")
    from app.filters import apply_filters

    result = apply_filters(tracks, [criterion], [])
    assert len(result) == 1
    assert result[0].track_id == "abc"


def test_genre_or_contains(tracks):
    criterion = FilterCriterion(type="genre", operator="contains", value="jazz")
    from app.filters import apply_filters

    result = apply_filters(tracks, [criterion], [])
    assert len(result) == 1
    assert "jazz" in result[0].genres.lower()


def test_tempo_filter(tracks):
    criterion = FilterCriterion(type="tempo", operator=">", value=130)
    from app.filters import apply_filters

    result = apply_filters(tracks, [criterion], [])
    assert len(result) == 1
    assert result[0].tempo is not None and result[0].tempo > 130


def test_instrumentalness_filter(tracks):
    criterion = FilterCriterion(type="instrumentalness", operator=">", value=0.5)
    from app.filters import apply_filters

    result = apply_filters(tracks, [criterion], [])
    assert len(result) == 1
    assert result[0].track_id == "jkl"


def test_acousticness_filter(tracks):
    criterion = FilterCriterion(type="acousticness", operator=">", value=0.8)
    from app.filters import apply_filters

    result = apply_filters(tracks, [criterion], [])
    assert len(result) == 2
    assert all(t.acousticness is not None and t.acousticness > 0.8 for t in result)


def test_workout_filter(tracks):
    criterion = FilterCriterion(type="workout", operator="=", value=True)
    from app.filters import apply_filters

    result = apply_filters(tracks, [criterion], [])
    assert len(result) == 1
    assert result[0].track_id == "ghi"


def test_and_combination(tracks):
    and_filters = [
        FilterCriterion(type="year", operator=">=", value=2020),
        FilterCriterion(type="popularity", operator=">=", value=50),
    ]
    from app.filters import apply_filters

    result = apply_filters(tracks, and_filters, [])
    assert len(result) == 3
    for t in result:
        assert t.year is not None and t.year >= 2020
        assert t.popularity >= 50


def test_or_combination(tracks):
    or_filters = [
        FilterCriterion(type="genre", operator="contains", value="jazz"),
        FilterCriterion(type="genre", operator="contains", value="rock"),
    ]
    from app.filters import apply_filters

    result = apply_filters(tracks, [], or_filters)
    assert len(result) == 2
    for t in result:
        assert t.genres is not None and ("jazz" in t.genres or "rock" in t.genres)


def test_mixed_and_or(tracks):
    and_filters = [FilterCriterion(type="year", operator=">=", value=2020)]
    or_filters = [
        FilterCriterion(type="genre", operator="contains", value="pop"),
        FilterCriterion(type="genre", operator="contains", value="dance"),
    ]
    from app.filters import apply_filters

    result = apply_filters(tracks, and_filters, or_filters)
    assert len(result) == 2
    for t in result:
        assert t.year is not None and t.year >= 2020


def test_no_filters(tracks):
    from app.filters import apply_filters

    result = apply_filters(tracks, [], [])
    assert len(result) == len(tracks)


def test_no_match(tracks):
    criterion = FilterCriterion(type="year", operator="<", value=1900)
    from app.filters import apply_filters

    result = apply_filters(tracks, [criterion], [])
    assert len(result) == 0


def test_none_values():
    from app.models import TrackOut
    from app.filters import apply_filters

    track = TrackOut(
        id="99",
        track_id="none:track",
        track_name="Null Track",
        artists="Nobody",
        album="Void",
        album_image_url=None,
        duration_ms=0,
        explicit=False,
        popularity=0,
        genres=None,
        year=None,
        instrumentalness=None,
        acousticness=None,
        tempo=None,
        energy=None,
        danceability=None,
    )

    result = apply_filters([track], [FilterCriterion(type="year", operator=">", value=2000)], [])
    assert len(result) == 0

    result = apply_filters([track], [FilterCriterion(type="workout", operator="=", value=True)], [])
    assert len(result) == 0


def test_or_filters_empty_and_present(tracks):
    criterion = FilterCriterion(type="year", operator=">", value=2023)
    from app.filters import apply_filters

    result = apply_filters(tracks, [criterion], [])
    assert len(result) == 1
    assert result[0].year == 2024
