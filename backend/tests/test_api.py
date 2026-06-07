import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import FilterCriterion


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestAuth:
    def test_login_redirects(self, client):
        resp = client.get("/auth/login", follow_redirects=False)
        assert resp.status_code in (200, 307, 302)
        location = resp.headers.get("location", "")
        assert "spotify.com/authorize" in location or "accounts.spotify.com" in location

    def test_get_me_unauthenticated(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 401
        assert "Not authenticated" in resp.text


class TestFilterEndpoint:
    def test_filter_unauthenticated(self, client):
        resp = client.post("/api/tracks/filter", json={})
        assert resp.status_code == 401

    def test_sync_unauthenticated(self, client):
        resp = client.post("/api/tracks/sync")
        assert resp.status_code == 401

    def test_create_playlist_unauthenticated(self, client):
        resp = client.post("/api/playlists", json={
            "name": "Test",
            "filter_criteria": {},
        })
        assert resp.status_code == 401


class TestPlaylistEndpoint:
    def test_create_empty_name(self, client):
        resp = client.post("/api/playlists", json={
            "name": "",
            "filter_criteria": {"and_filters": [], "or_filters": []},
        })
        assert resp.status_code in (401, 422)

    def test_create_without_criteria(self, client):
        resp = client.post("/api/playlists", json={"name": "Test"})
        assert resp.status_code in (401, 422)
