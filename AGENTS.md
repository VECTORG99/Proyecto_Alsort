# Alsort — Contexto para IA

## Stack
- **Backend**: Python 3.12, FastAPI, SQLAlchemy async + SQLite, Alembic, httpx, pydantic-settings
- **Frontend**: React 18, TypeScript 5.6, Vite 6
- **Auth**: OAuth PKCE con Spotify (sin client_secret en el flujo)
- **Infra**: Docker Compose (nginx → backend), GitHub Actions CI
- **Testing**: pytest (asyncio_mode=auto), 45+ tests

## Convenciones de Código
- `async def` en toda la app (httpx + SQLAlchemy async)
- Pydantic v2: `field_validator` (no `validators`), `model_config`
- Sin comentarios en código salvo excepciones justificadas
- Logging estructurado: `[timestamp] LEVEL module:line mensaje`
- Errores de usuario: toast notification, no inline messages
- Sesión en localStorage (`alsort_session_id`), enviada como header `X-Session-Id`

## Límites
- Rate limiter Spotify: 280 req / 60s (con `asyncio.Lock`)
- Playlist máx: 10.000 tracks (límite Spotify)
- Paginación UI: 50/100/200 por página
- Audio features batch: 100 IDs/req, Artists batch: 50 IDs/req

## Archivos Clave

| Archivo | Rol |
|---------|-----|
| `backend/app/main.py` | FastAPI app, CORS, rutas, health, `get_current_user` |
| `backend/app/config.py` | Settings via pydantic-settings, valida env vars al startup |
| `backend/app/auth.py` | OAuth PKCE: login, callback, get_me, refresh |
| `backend/app/spotify_client.py` | httpx wrapper: rate limiter, retry, batch fetch, cache |
| `backend/app/filters.py` | `apply_filters()` + `sort_tracks()`, mapeo tipo→atributo |
| `backend/app/models.py` | Pydantic: `FilterCriterion` (validación rangos), `FilterRequest`, `TrackOut` |
| `backend/app/playlist_manager.py` | `get_filtered_tracks()`, `create_playlist_from_filters()` |
| `backend/app/database.py` | SQLAlchemy `User`, `CachedTrack`, `Playlist`, `init_db()` |
| `frontend/src/services/api.ts` | fetch wrapper, `VITE_API_URL` env, `AbortSignal` |
| `frontend/src/components/Dashboard.tsx` | Estado: página, sort, filtros; coordina componentes |
| `frontend/src/components/FilterPanel.tsx` | Filtros AND/OR dinámicos con `_key` único |
| `frontend/src/components/SongList.tsx` | Skeleton, búsqueda local, sort, paginación |
| `frontend/src/components/PlaylistCreator.tsx` | Formulario + toast en creación |
| `frontend/src/context/ToastContext.tsx` | useRef para IDs y timers, cleanup en unmount |
| `frontend/src/context/LoadingContext.tsx` | Overlay global con spinner |

## Flujo OAuth
```
/login → PKCE challenge → Spotify auth → /callback → code exchange →
  fetch /me → upsert User → redirect ?session={user.id} → localStorage →
  X-Session-Id header en cada request
```

## Flujo de Datos
```
Sync: Spotify /me/tracks → /audio-features → /artists → SQLite cache
Filter: SQLite cache → apply_filters() → sort_tracks() → paginate → response
Create: filter → Spotify /me/playlists → /playlists/{id}/tracks → response
```

## Variables de Entorno (backend/.env)
- `SPOTIFY_CLIENT_ID` — obligatorio, validado al startup
- `SPOTIFY_REDIRECT_URI` — default `http://localhost:8000/auth/callback`
- `SESSION_SECRET` — obligatorio, validado al startup
- `DATABASE_URL` — default `sqlite+aiosqlite:///./data/alsort.db`
- `FRONTEND_URL` — default `http://localhost:5173`
- `VITE_API_URL` (frontend) — default `""` (mismo origen vía Vite proxy)

## Comandos
```bash
make dev-backend        # uvicorn :8000
make dev-frontend       # vite :5173
make test-backend       # pytest -v (45+ tests)
make test-frontend      # tsc --noEmit + vite build
make docker-up          # docker compose up --build
make lint-backend       # ruff check .
make clean              # rm -rf dist/ __pycache__/ .pytest_cache
```

## Tests
- `test_filters.py`: 22 tests — cada tipo de filtro, combinaciones AND/OR, bordes
- `test_models.py`: 15 tests — validación rangos (year, popularity, instrumentalness, acousticness, tempo)
- `test_api.py`: 8 tests — auth, endpoints protegidos, validación requests
- Fixtures: 5 tracks mock (rock, folk, workout, jazz, pop) con `track_id` bare (sin `spotify:track:` prefijo)

## Bugs Conocidos (fixeados)
- ~~DB path default no coincidía con volumen Docker~~ (/data/alsort.db ahora)
- ~~API_BASE hardcodeado a localhost~~ (usa VITE_API_URL + Vite proxy)
- ~~sort_by ignorado al crear playlist~~ (se pasa en FilterRequest)
- ~~Rate limiter: race condition TOCTOU + reset completo de timestamps~~ (asyncio.Lock + filtrado)
- ~~N+1 queries en cache_tracks~~ (batch fetch con `in_()`)
- ~~PKCE verifier de solo 43 chars~~ (64 bytes, 88 chars)
- ~~State OAuth contenía verifier~~ (state aleatorio adicional)
- ~~React key índice en filtros~~ (\_key único numérico)
- ~~Toast setTimeout sin cleanup~~ (timersRef + cleanup en unmount)
- ~~test track_ids con prefijo spotify:track:~~ (bare IDs)
- ~~year crash en release_date corta~~ (try/except + len check)
- ~~CORS necesario en dev~~ (Vite proxy elimina necesidad)
