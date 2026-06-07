# Alsort - Spotify Playlist Manager

## Stack
- Backend: Python 3.12, FastAPI, SQLAlchemy async, SQLite, Alembic, httpx
- Frontend: React 19, TypeScript, Vite
- Auth: OAuth PKCE with Spotify
- Infra: Docker Compose (backend + frontend + nginx)

## Repo Structure
```
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, routes, health check
│   │   ├── auth.py           # OAuth PKCE flow, session validation
│   │   ├── spotify_client.py # Spotify API wrapper (rate limit + retry)
│   │   ├── filters.py        # Filter engine + sort
│   │   ├── models.py         # Pydantic models (FilterRequest, TrackOut, etc.)
│   │   ├── playlist_manager.py # Orchestrates filter/sort/playlist creation (10k limit)
│   │   ├── database.py       # SQLAlchemy models + Alembic runner
│   │   └── logger.py         # Structured logging
│   ├── alembic/              # DB migrations
│   ├── tests/                # Pytest tests (45+)
│   └── .env.example          # Required env vars
├── frontend/
│   ├── src/
│   │   ├── components/       # Login, Dashboard, FilterPanel, SongList, PlaylistCreator
│   │   ├── context/          # LoadingContext, ToastContext
│   │   ├── services/         # API client
│   │   └── types/            # TypeScript types + constants
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── Makefile
└── .pre-commit-config.yaml
```

## Key Commands
```bash
# Development (local)
make dev-backend    # uvicorn on :8000
make dev-frontend   # vite on :5173

# Docker
make docker-up      # docker compose up --build
make docker-down

# Tests
make test-backend   # pytest
make test-frontend  # tsc typecheck

# Lint
make lint-backend   # ruff check
make lint-frontend  # eslint if configured

# Install deps
make install
```

## Conventions
- Use async/await everywhere (httpx + SQLAlchemy async)
- Pydantic v2 for validation (field_validator, not validators)
- No comments in code unless absolutely necessary
- Rate limiter: 280 req/60s (Spotify ~300/min)
- Playlist max: 10,000 tracks (Spotify-imposed)
- Toast for success/error feedback, not inline messages
- Session stored in localStorage (alsort_session_id)

## Env Vars (backend/.env)
- SPOTIFY_CLIENT_ID
- SPOTIFY_CLIENT_SECRET
- SPOTIFY_REDIRECT_URI (default: http://localhost:8000/auth/callback)
- SESSION_SECRET
- FRONTEND_URL (default: http://localhost:5173)
