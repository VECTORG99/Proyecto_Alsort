import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.main import app
from app.models import TrackOut
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_track():
    return TrackOut(
        id="1",
        track_id="abc",
        track_name="Test Song",
        artists="Test Artist",
        album="Test Album",
        album_image_url=None,
        duration_ms=240000,
        explicit=False,
        popularity=60,
        genres="rock, alternative",
        year=2020,
        instrumentalness=0.1,
        acousticness=0.2,
        tempo=120.0,
        energy=0.8,
        danceability=0.7,
    )


@pytest.fixture
def tracks(sample_track):
    variants = [
        sample_track,
        TrackOut(
            id="2",
            track_id="def",
            track_name="Acoustic Ballad",
            artists="Folk Singer",
            album="Folk Album",
            album_image_url=None,
            duration_ms=300000,
            explicit=False,
            popularity=40,
            genres="folk, acoustic",
            year=2015,
            instrumentalness=0.05,
            acousticness=0.9,
            tempo=80.0,
            energy=0.2,
            danceability=0.3,
        ),
        TrackOut(
            id="3",
            track_id="ghi",
            track_name="Workout Banger",
            artists="Gym Bro",
            album="Fitness",
            album_image_url=None,
            duration_ms=180000,
            explicit=True,
            popularity=80,
            genres="pop, dance",
            year=2023,
            instrumentalness=0.01,
            acousticness=0.05,
            tempo=140.0,
            energy=0.9,
            danceability=0.85,
        ),
        TrackOut(
            id="4",
            track_id="jkl",
            track_name="Old Jazz",
            artists="Miles Tone",
            album="Blue",
            album_image_url=None,
            duration_ms=360000,
            explicit=False,
            popularity=30,
            genres="jazz",
            year=1960,
            instrumentalness=0.8,
            acousticness=0.95,
            tempo=60.0,
            energy=0.1,
            danceability=0.2,
        ),
        TrackOut(
            id="5",
            track_id="mno",
            track_name="Pop Hit",
            artists="Pop Star",
            album="Pop Album",
            album_image_url=None,
            duration_ms=200000,
            explicit=False,
            popularity=90,
            genres="pop",
            year=2024,
            instrumentalness=0.0,
            acousticness=0.1,
            tempo=110.0,
            energy=0.6,
            danceability=0.8,
        ),
    ]
    return variants
