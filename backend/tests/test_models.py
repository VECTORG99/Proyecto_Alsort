import pytest
from pydantic import ValidationError
from app.models import FilterCriterion, FilterRequest, CreatePlaylistRequest


class TestFilterCriterion:
    def test_valid_year(self):
        c = FilterCriterion(type="year", operator=">", value=2000)
        assert c.value == 2000

    def test_valid_year_between(self):
        c = FilterCriterion(type="year", operator="between", value=[2000, 2024])
        assert c.value == [2000, 2024]

    def test_invalid_year_too_low(self):
        with pytest.raises(ValidationError, match="out of range"):
            FilterCriterion(type="year", operator=">", value=1800)

    def test_invalid_year_too_high(self):
        with pytest.raises(ValidationError, match="out of range"):
            FilterCriterion(type="year", operator=">", value=3000)

    def test_invalid_year_between_high(self):
        with pytest.raises(ValidationError, match="out of range"):
            FilterCriterion(type="year", operator="between", value=[2000, 3000])

    def test_invalid_popularity_negative(self):
        with pytest.raises(ValidationError, match="out of range"):
            FilterCriterion(type="popularity", operator=">", value=-1)

    def test_invalid_popularity_too_high(self):
        with pytest.raises(ValidationError, match="out of range"):
            FilterCriterion(type="popularity", operator=">", value=101)

    def test_valid_popularity(self):
        c = FilterCriterion(type="popularity", operator="=", value=50)
        assert c.value == 50

    def test_invalid_instrumentalness(self):
        with pytest.raises(ValidationError):
            FilterCriterion(type="instrumentalness", operator=">", value=1.5)

    def test_invalid_acousticness(self):
        with pytest.raises(ValidationError):
            FilterCriterion(type="acousticness", operator="<", value=-0.1)

    def test_invalid_tempo(self):
        with pytest.raises(ValidationError):
            FilterCriterion(type="tempo", operator=">", value=500)

    def test_valid_tempo(self):
        c = FilterCriterion(type="tempo", operator=">", value=120)
        assert c.value == 120

    def test_valid_explicit(self):
        c = FilterCriterion(type="explicit", operator="=", value=True)
        assert c.value is True

    def test_valid_artist_text(self):
        c = FilterCriterion(type="artist", operator="contains", value="queen")
        assert c.value == "queen"

    def test_valid_workout(self):
        c = FilterCriterion(type="workout", operator="=", value=True)
        assert c.value is True


class TestFilterRequest:
    def test_empty(self):
        req = FilterRequest()
        assert req.and_filters == []
        assert req.or_filters == []
        assert req.limit == 50
        assert req.offset == 0

    def test_with_filters(self):
        req = FilterRequest(
            and_filters=[FilterCriterion(type="year", operator=">", value=2000)],
            or_filters=[FilterCriterion(type="genre", operator="contains", value="rock")],
            limit=100,
        )
        assert len(req.and_filters) == 1
        assert len(req.or_filters) == 1
        assert req.limit == 100


class TestCreatePlaylistRequest:
    def test_minimal(self):
        req = CreatePlaylistRequest(
            name="My Playlist",
            filter_criteria=FilterRequest(),
        )
        assert req.name == "My Playlist"
        assert req.public is True

    def test_full(self):
        req = CreatePlaylistRequest(
            name="Test",
            description="desc",
            public=False,
            filter_criteria=FilterRequest(
                and_filters=[FilterCriterion(type="year", operator=">", value=2020)]
            ),
        )
        assert req.public is False
        assert len(req.filter_criteria.and_filters) == 1
