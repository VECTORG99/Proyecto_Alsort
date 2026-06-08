# Alsort

**Gestor inteligente de playlists de Spotify.** Extrae tus canciones likeadas, enriquécelas con audio features y géneros, aplícales filtros avanzados con lógica AND/OR, ordénalas por múltiples criterios y crea playlists directamente en tu cuenta de Spotify.

<p align="center">
  <a href="https://github.com/VECTORG99/Proyecto_Alsort/actions/workflows/ci.yml">
    <img src="https://github.com/VECTORG99/Proyecto_Alsort/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <img src="https://img.shields.io/badge/tests-57-brightgreen" alt="Tests">
  <img src="https://img.shields.io/badge/python-3.12-blue" alt="Python">
  <img src="https://img.shields.io/badge/node-20-blue" alt="Node">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/status-activo-success" alt="Status">
</p>

---

## Stack

| Capa | Tecnología |
|------|-----------|
| Frontend | React 18 + TypeScript + Vite |
| Backend | Python 3.12 + FastAPI |
| Base de datos | SQLite + SQLAlchemy 2.0 (async) + Alembic |
| HTTP Client | httpx (async) |
| Auth | OAuth PKCE |
| Infra | Docker Compose (nginx + backend) |

---

## Requisitos

- Python 3.12+
- Node.js 18+
- Cuenta de Spotify (gratuita o premium)
- App registrada en [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

---

## Instalación

### 1. Crear App en Spotify

1. Ve a [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) → **Create App**
2. Nombre: `Alsort`, Redirect URI: `http://localhost:8000/auth/callback`
3. Marca **Web API**, guarda
4. Copia **Client ID** y **Client Secret**

### 2. Desarrollo local

```bash
git clone https://github.com/VECTORG99/Proyecto_Alsort.git
cd Proyecto_Alsort

# Backend
cp backend/.env.example backend/.env
# Edita backend/.env con tu Client ID y Client Secret
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (nueva terminal)
cd frontend && npm install && npm run dev
```

Backend: `http://localhost:8000` — Docs API: `http://localhost:8000/docs`
Frontend: `http://localhost:5173`

### 3. Docker

```bash
make docker-up    # docker compose up --build
make docker-down  # docker compose down
```

---

## Estructura del Proyecto

```
Proyecto_Alsort/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, rutas, CORS, lifespan, health
│   │   ├── config.py                # pydantic-settings (valida env vars al startup)
│   │   ├── auth.py                  # OAuth PKCE: login, callback, refresh, get_me
│   │   ├── database.py              # SQLAlchemy async engine, modelos, Alembic runner
│   │   ├── models.py                # Pydantic: FilterCriterion, FilterRequest, TrackOut, etc.
│   │   ├── spotify_client.py        # Cliente httpx con rate limiter, retry, batch requests
│   │   ├── filters.py               # Motor de filtros (AND/OR, sort, tipo a atributo)
│   │   ├── playlist_manager.py      # Orquestación: filtrar + cachear + crear playlist
│   │   └── logger.py                # Logging estructurado [timestamp] LEVEL module:line msg
│   ├── alembic/                     # Migraciones (1 initial)
│   ├── tests/                       # 45+ tests (pytest)
│   ├── requirements.txt             # Producción
│   ├── requirements-dev.txt         # + pytest
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.tsx                 # Entry point
│   │   ├── App.tsx                  # Sesión, Login ↔ Dashboard, Loading + Toast wrappers
│   │   ├── index.css                # Tema oscuro Spotify, skeleton, toast, paginación
│   │   ├── vite-env.d.ts            # Tipos VITE_API_URL
│   │   ├── types/index.ts           # Track, FilterCriterion, FilterRequest, constantes
│   │   ├── services/api.ts          # fetch wrapper con X-Session-Id + AbortSignal
│   │   ├── context/
│   │   │   ├── LoadingContext.tsx    # Overlay global con spinner + mensaje
│   │   │   └── ToastContext.tsx      # Notificaciones success/error/info, auto-dismiss
│   │   └── components/
│   │       ├── Login.tsx             # Botón de inicio con logo Spotify
│   │       ├── Dashboard.tsx         # Header + sidebar (filtros/crear) + main (lista)
│   │       ├── FilterPanel.tsx       # Filtros AND/OR con 11 tipos, 7 operadores
│   │       ├── SongList.tsx          # Resultados: skeleton, búsqueda, sort, paginación
│   │       └── PlaylistCreator.tsx   # Formulario: nombre, descripción, público/privado
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts               # Proxy dev /api → :8000, /auth → :8000
├── Dockerfile.backend                # Multi-stage, python:3.12-slim, no dev, no-root
├── Dockerfile.frontend               # Multi-stage, node → nginx, SPA fallback
├── docker-compose.yml                # backend + frontend, red interna, healthcheck
├── nginx.conf                        # SPA fallback, proxy reverso, security headers
├── Makefile                          # dev, build, test, lint, docker, clean
├── pyproject.toml                    # pytest + ruff config
├── .pre-commit-config.yaml           # ruff, prettier, hooks generales
├── .dockerignore
├── .github/workflows/ci.yml          # test-backend, test-frontend, docker build
├── AGENTS.md                         # Contexto para IA
└── README.md
```

---

## Variables de Entorno

| Variable | Default | Obligatoria | Descripción |
|----------|---------|-------------|-------------|
| `SPOTIFY_CLIENT_ID` | — | ✅ | Client ID de tu app en Spotify |
| `SPOTIFY_CLIENT_SECRET` | — | ❌ (PKCE) | Solo para referencia; PKCE no lo usa |
| `SPOTIFY_REDIRECT_URI` | `http://localhost:8000/auth/callback` | ❌ | Debe coincidir con el Redirect URI en Spotify Dashboard |
| `SESSION_SECRET` | — | ✅ | Clave para firma de sesiones |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/alsort.db` | ❌ | Ruta a la base de datos SQLite |
| `FRONTEND_URL` | `http://localhost:5173` | ❌ | Origen CORS y destino de redirect OAuth |
| `VITE_API_URL` | `""` (mismo origen) | ❌ | URL base de la API (para producción) |

El backend valida al startup que `SPOTIFY_CLIENT_ID` y `SESSION_SECRET` estén configuradas y no usen valores placeholder. Si falta alguna, el proceso termina con un mensaje claro.

---

## API Endpoints

### Auth (`/auth`)

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `GET` | `/auth/login` | No | Redirige a Spotify con PKCE challenge |
| `GET` | `/auth/callback` | No | Intercambia code por token, crea/actualiza usuario, redirect a frontend con `?session=` |
| `GET` | `/auth/me` | X-Session-Id | Info del usuario + refresh automático de token si expiró |

### Tracks (`/api/tracks`)

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `POST` | `/api/tracks/sync` | X-Session-Id | Trae liked songs, audio features, géneros, cachea en SQLite |
| `POST` | `/api/tracks/filter` | X-Session-Id | Filtra + ordena + paginación sobre cache |

### Playlists

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `POST` | `/api/playlists` | X-Session-Id | Crea playlist desde filtros (máx 10.000 tracks) |

### Health

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `GET` | `/health` | No | `{"status": "ok", "service": "alsort-api"}` |

### Autenticación

Todas las rutas protegidas leen el header `X-Session-Id` (o cookie `session_id`). El valor es el UUID del usuario en la base de datos, almacenado en `localStorage` como `alsort_session_id` tras el flujo OAuth.

---

## Filtros

### Tipos disponibles

| Tipo | Rango | Operadores | Fuente |
|------|-------|------------|--------|
| `year` | 1900–2030 | `=` `>` `<` `>=` `<=` `between` | Metadata del álbum |
| `popularity` | 0–100 | `=` `>` `<` `>=` `<=` | Spotify |
| `duration_ms` | cualquier entero | `>` `<` `between` | Metadata |
| `explicit` | booleano | `=` | Metadata |
| `artist` | texto | `=` `contains` | Metadata |
| `album` | texto | `=` `contains` | Metadata |
| `genre` | texto | `=` `contains` | Artista (vía Spotify) |
| `instrumentalness` | 0.0–1.0 | `>` `<` `>=` `<=` | Audio features |
| `acousticness` | 0.0–1.0 | `>` `<` `>=` `<=` | Audio features |
| `tempo` | 0–300 | `>` `<` `>=` `<=` `between` | Audio features |
| `workout` | booleano | `=` | Derivado: `energy>0.7 AND tempo>120 AND danceability>0.6` |

### Lógica

1. **AND**: la canción debe pasar TODOS los criterios AND
2. **OR**: la canción debe pasar AL MENOS UNO de los criterios OR (si no hay OR, se omite)
3. Resultado = intersección de ambos grupos

### Ordenamiento

Campos ordenables: `year`, `popularity`, `duration_ms`, `tempo`, `energy`, `danceability`, `track_name`, `artists` — en sentido ascendente o descendente.

---

## Base de Datos

### Modelos SQLAlchemy (`database.py`)

**User** (`users`)
- `id` (UUID PK), `spotify_id` (unique), `display_name`, `email`, `access_token`, `refresh_token`, `token_expires_at`, `created_at`

**CachedTrack** (`cached_tracks`)
- `id` (UUID PK), `spotify_user_id` (indexed), `track_id`, `track_name`, `artists`, `album`, `album_id`, `album_image_url`, `duration_ms`, `explicit`, `popularity`, `track_url`, `genres`, `year`, `audio_features` (JSON), `cached_at`

**Playlist** (`playlists`)
- `id` (UUID PK), `spotify_user_id` (indexed), `spotify_playlist_id`, `name`, `description`, `filter_criteria` (JSON), `created_at`

### Migraciones

Alembic con `async_engine_from_config`. La migración inicial (`4dc010d98fab`) crea las 3 tablas. `init_db()` en `database.py` ejecuta `alembic upgrade head` automáticamente al iniciar.

---

## Spotify Client

### Rate Limiting

- Máx 280 requests por ventana de 60 segundos
- `asyncio.Lock` para exclusión mutua
- Si se excede el límite, espera hasta que expire la ventana
- Los timestamps expirados se limpian, no se reinicia la ventana por completo

### Retry

- 3 reintentos máximos
- Reintenta en: 429 (con `Retry-After`), 502, 503, 504
- Reintenta en: `TimeoutException`, `ConnectError`, `RemoteProtocolError`
- Backoff exponencial: 1s, 2s, 4s

### Endpoints usados de Spotify

| Endpoint | Propósito | Batch |
|----------|-----------|-------|
| `GET /me/tracks` | Liked songs (offset/limit 50) | Paginación automática |
| `GET /audio-features` | BPM, energía, etc. | 100 IDs por request |
| `GET /artists` | Géneros de artistas | 50 IDs por request |
| `POST /me/playlists` | Crear playlist | — |
| `POST /playlists/{id}/tracks` | Agregar tracks | 100 URIs por request |

---

## Tests

<p align="center">
  <img src="https://img.shields.io/badge/estado-aprobado-success" alt="Tests">
  <img src="https://img.shields.io/badge/coverage-≥85%25-success" alt="Coverage">
  <img src="https://img.shields.io/badge/unitarios-26-blue" alt="Unit">
  <img src="https://img.shields.io/badge/modelo-24-blue" alt="Model">
  <img src="https://img.shields.io/badge/integración-7-blue" alt="Integration">
  <img src="https://img.shields.io/badge/frontend-tsc%2Bbuild-blue" alt="Frontend">
</p>

### Backend (57 tests)

Los tests **no requieren conexión a Spotify**. Usan `TestClient` de FastAPI con datos mock.

```bash
make test-backend              # pytest sin cobertura
make test-backend-coverage     # pytest con cobertura + reporte HTML
make test-coverage             # backend coverage + frontend typecheck
make test-all                  # coverage + lint (backend + frontend)
make coverage-report           # abre backend/coverage_html/index.html
```

| Archivo | Tests | Cobertura | Lo que cubre |
|---------|-------|-----------|-------------|
| `test_filters.py` | 26 | ~100% | Cada tipo de filtro individual, operadores `=` `>` `<` `>=` `<=` `between` `contains`, combinaciones AND/OR, bordes (None, vacío), workout, sort |
| `test_models.py` | 24 | ~100% | Validación de rangos: `year` (1900-2030), `popularity` (0-100), `instrumentalness`/`acousticness` (0.0-1.0), `tempo` (0-300), valores válidos e inválidos |
| `test_api.py` | 7 | ~90% | Auth sin sesión retorna 401, login redirige a Spotify, get_me sin auth 401, endpoints protegidos, validación de requests (nombre vacío, criteria faltante) |

**Fixtures:** 5 tracks de ejemplo (rock, folk, workout, jazz, pop) con valores realistas que cubren todo el espectro de cada campo.

### Frontend (type-check + build)

```bash
make test-frontend    # tsc --noEmit + vite build
npm run typecheck     # solo type-check
npm run lint          # type-check (como lint)
```

El frontend no tiene tests unitarios de componentes actualmente. El type-check de TypeScript y el build de Vite validan la corrección del código.

### CI/CD automatizado

GitHub Actions ejecuta todos los tests en cada push/PR a `master`:

```yaml
jobs:
  test-backend:   # pytest con cobertura, sube reporte HTML como artifact
  test-frontend:  # tsc --noEmit + vite build
  docker:         # build de ambas imágenes Docker
```

El reporte de cobertura se genera automáticamente y está disponible como artifact de GitHub Actions.

---

## Docker

```bash
make docker-up       # Construye y levanta backend + frontend
make docker-down     # Detiene servicios
make build-backend   # Solo construir imagen backend
make build-frontend  # Solo construir imagen frontend
```

- Backend: python:3.12-slim, multi-stage, usuario no-root, healthcheck
- Frontend: nginx:alpine con SPA fallback y proxy reverso
- Red interna `alsort-net`, backend solo escucha en `127.0.0.1:8000`
- Volumen `alsort-data` persistente montado en `/app/data`
- CI también construye ambas imágenes para validar

---

## CI/CD

GitHub Actions ejecuta 3 jobs en cada push/PR a `master` (ver [workflow](.github/workflows/ci.yml)):

| Job | Qué hace | Artefacto |
|-----|----------|-----------|
| `test-backend` | pytest con cobertura | Reporte HTML (`coverage-report`) |
| `test-frontend` | `tsc --noEmit` + `vite build` | — |
| `docker` | Build de ambas imágenes Docker | — |

Los badges de estado se actualizan automáticamente con cada ejecución.

---

## Guía de Uso

1. Abre `http://localhost:5173` (o el puerto Docker)
2. Inicia sesión con Spotify — serás redirigido a la autorización de Spotify
3. Haz clic en **Sincronizar likes** para cargar tus canciones (se cachean en SQLite)
4. En el panel lateral, añade filtros AND y/u OR
5. Haz clic en **Aplicar Filtros** — los resultados aparecen con ordenación y paginación
6. Usa la **búsqueda local** para filtrar dentro de los resultados actuales
7. Una vez satisfecho, completa el formulario **Crear Playlist** y haz clic en el botón
8. La playlist aparece automáticamente en tu cuenta de Spotify

---

## Seguridad y Estabilidad (QA)

- **Seguridad contra CSRF**: Validación estricta del parámetro `state` mediante cookies HTTP-only temporales (`max_age=300`) y verificación segura usando `hmac.compare_digest` para evitar ataques de falsificación de peticiones en sitios cruzados durante el login.
- **Prevención de Fugas de Memoria y Conexiones**: Gestión limpia de clientes HTTP mediante el uso garantizado de bloques `try/finally` asegurando el cierre asíncrono (`aclose()`) de las instancias `httpx.AsyncClient` creadas para interactuar con la API de Spotify.
- **Control de Concurrencia**: Uso de bloqueos de tipo `asyncio.Lock` en el refresco de tokens por usuario de Spotify para prevenir múltiples renovaciones de credenciales simultáneas y race conditions.
- **Robustez en SQLite**: Capping de consultas en lote a un máximo de 900 variables en la cláusula `IN` de SQLite para evitar el límite máximo de variables permitido por el motor base.
- **Consistencia en la UI**:
  - Implementación de `AbortController` en peticiones Fetch del frontend para cancelar peticiones previas en curso si se realizan filtros o paginación rápidamente.
  - Límite de notificaciones push concurrentes (*toasts*) a un máximo de 5 para mejorar la visualización y evitar consumo excesivo de timers.
- **Interfaz Responsiva**: Inclusión de reglas responsivas y *media queries* nativas en CSS para adaptar la interfaz web perfectamente a tablets y teléfonos móviles.

---

## Limitaciones Conocidas

- Spotify no siempre devuelve `refresh_token` en flujo PKCE — si el token expira, hay que re-autenticar
- Máximo 10.000 tracks por playlist (límite de Spotify)
- La búsqueda local (client-side) solo filtra la página actual, no el conjunto completo
- Las canciones cacheadas no se actualizan automáticamente — hay que hacer sync manual
