<div align="center">
  <h1>🎵 Alsort</h1>
  <p><strong>Gestor inteligente de playlists de Spotify</strong></p>
  <p>Extrae tus canciones likeadas, aplícales filtros avanzados y crea playlists automáticamente.</p>
  <p>
    <a href="https://github.com/VECTORG99/Proyecto_Alsort/actions/workflows/ci.yml">
      <img src="https://github.com/VECTORG99/Proyecto_Alsort/actions/workflows/ci.yml/badge.svg" alt="CI">
    </a>
  </p>
</div>

---

## Tabla de Contenidos

- [Descripción](#descripción)
- [Capturas](#capturas)
- [Stack Tecnológico](#stack-tecnológico)
- [Requisitos](#requisitos)
- [Instalación y Configuración](#instalación-y-configuración)
  - [1. Crear App en Spotify](#1-crear-app-en-spotify)
  - [2. Configurar Backend](#2-configurar-backend)
  - [3. Configurar Frontend](#3-configurar-frontend)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Guía de Uso](#guía-de-uso)
- [Filtros Disponibles](#filtros-disponibles)
  - [Filtros de Metadata](#filtros-de-metadata)
  - [Filtros de Audio Features](#filtros-de-audio-features)
  - [Filtros Derivados](#filtros-derivados)
- [Crossplaylists: Lógica AND/OR](#crossplaylists-lógica-ando)
- [API Endpoints](#api-endpoints)
- [Flujo de Datos](#flujo-de-datos)
- [Posibles Mejoras Futuras](#posibles-mejoras-futuras)

---

## Descripción

**Alsort** es una aplicación web que se conecta con tu cuenta de Spotify para:

1. **Extraer todas tus canciones likeadas** (con paginación automática)
2. **Enriquecerlas** con audio features (BPM, energía, instrumentalidad, etc.) y géneros de los artistas
3. **Filtrarlas** combinando múltiples criterios con lógica AND/OR
4. **Crear playlists** directamente en tu cuenta de Spotify con los resultados

Está diseñada para resolver el problema de tener cientos o miles de canciones likeadas y no saber cómo organizarlas. Con Alsort puedes crear playlists temáticas al instante: "Rock intenso para gym", "Acústico para estudiar", "Fiesta 2020s", etc.

---

## Capturas

*(pendiente)*

---

## Stack Tecnológico

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| **Frontend** | React 18 + TypeScript + Vite | Interfaz de usuario moderna y reactiva |
| **Backend** | Python 3.11+ + FastAPI | API REST asíncrona |
| **Base de datos** | SQLite + SQLAlchemy 2.0 (async) | Caching de canciones y sesiones |
| **HTTP Client** | HTTPX (async) | Comunicación con Spotify Web API |
| **Auth** | PKCE OAuth 2.0 | Autenticación segura con Spotify |
| **Estilos** | CSS personalizado (modo oscuro) | Tema inspirado en Spotify |

---

## Requisitos

- **Python 3.11 o superior**
- **Node.js 18 o superior** (con npm)
- Una cuenta de **Spotify** (gratuita o premium)
- Una **app registrada** en el [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

---

## Instalación y Configuración

### 1. Crear App en Spotify

1. Ve a [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Haz clic en **"Create App"**
3. Ponle un nombre (ej: "Alsort") y una descripción
4. En **Redirect URIs**, agrega: `http://localhost:8000/auth/callback`
5. Marca **Web API** y acepta los términos
6. Guarda los cambios
7. Copia el **Client ID** y el **Client Secret** de la página de la app

### 2. Configurar Backend

```bash
# 1. Clona el repositorio
git clone https://github.com/VECTORG99/Proyecto_Alsort.git
cd Proyecto_Alsort

# 2. Ve al directorio del backend
cd backend

# 3. Crea el archivo .env desde el ejemplo
cp .env.example .env

# 4. Edita .env con tus credenciales de Spotify
nano .env
```

El archivo `.env` debe verse así:

```env
SPOTIFY_CLIENT_ID=tu_client_id_aqui
SPOTIFY_CLIENT_SECRET=tu_client_secret_aqui
SPOTIFY_REDIRECT_URI=http://localhost:8000/auth/callback
SESSION_SECRET=alsort-secret-key-change-in-production
FRONTEND_URL=http://localhost:5173
```

Luego instala dependencias y ejecuta:

```bash
# 5. Crea un entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# 6. Instala dependencias
pip install -r requirements.txt

# 7. Inicia el servidor
uvicorn app.main:app --reload
```

El backend se iniciará en `http://localhost:8000`. La documentación interactiva de la API está disponible en `http://localhost:8000/docs`.

### 3. Configurar Frontend

Abre una **nueva terminal** y ejecuta:

```bash
# 1. Ve al directorio del frontend
cd Proyecto_Alsort/frontend

# 2. Instala dependencias
npm install

# 3. Inicia el servidor de desarrollo
npm run dev
```

El frontend se iniciará en `http://localhost:5173`.

---

## Estructura del Proyecto

```
Proyecto_Alsort/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app, rutas, CORS, lifespan
│   │   ├── config.py              # Config con pydantic-settings
│   │   ├── auth.py                # OAuth PKCE, login, callback, refresh
│   │   ├── database.py            # SQLAlchemy async, modelos User/CachedTrack/Playlist
│   │   ├── spotify_client.py      # Cliente HTTPX para Spotify API
│   │   ├── models.py              # Pydantic request/response models
│   │   ├── filters.py             # Motor de filtros (aplica criterios AND/OR)
│   │   └── playlist_manager.py    # Orquestación: filtrar + crear playlist
│   ├── requirements.txt
│   ├── .env.example
│   └── .venv/                     # Entorno virtual (no incluido en git)
├── frontend/
│   ├── src/
│   │   ├── main.tsx               # Punto de entrada React
│   │   ├── App.tsx                # Router lógico: Login ↔ Dashboard
│   │   ├── index.css              # Estilos globales (tema oscuro)
│   │   ├── types/
│   │   │   └── index.ts           # Tipos TypeScript y constantes
│   │   ├── services/
│   │   │   └── api.ts             # Cliente HTTP para el backend
│   │   └── components/
│   │       ├── Login.tsx          # Pantalla de inicio con botón de Spotify
│   │       ├── Dashboard.tsx      # Panel principal con sidebar + contenido
│   │       ├── FilterPanel.tsx    # Panel de filtros (AND/OR dinámicos)
│   │       ├── SongList.tsx       # Lista de canciones con metadata y stats
│   │       └── PlaylistCreator.tsx # Formulario para crear playlist
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── .gitignore
└── README.md
```

---

## Guía de Uso

1. **Abre** `http://localhost:5173` en tu navegador
2. **Inicia sesión** con Spotify — serás redirigido a Spotify para autorizar la app
3. Una vez autenticado, verás el dashboard vacío
4. Haz clic en **"🔄 Sincronizar likes"** para cargar tus canciones likeadas
   - Esto puede tomar unos segundos dependiendo de cuántas tengas
   - Las canciones se cachean en SQLite para evitar llamadas repetidas
5. En el panel lateral, añade **filtros AND** y/o **filtros OR**:
   - Los filtros **AND** son obligatorios (todos deben cumplirse)
   - Los filtros **OR** son opcionales (al menos uno debe cumplirse)
6. Haz clic en **"Aplicar Filtros"** para ver los resultados
7. Una vez satisfecho con los resultados, desplázate abajo en el panel lateral
8. Ponle **nombre** a tu playlist, opcionalmente una descripción
9. Elige si quieres que sea **pública o privada**
10. Haz clic en **"Crear Playlist"** — la playlist se creará directamente en tu cuenta de Spotify

---

## Filtros Disponibles

### Filtros de Metadata

| Filtro | Tipo de Valor | Operadores | Descripción |
|--------|---------------|------------|-------------|
| **Año** | número | `=` `>` `<` `>=` `<=` `between` | Año de lanzamiento (ej: 2020, [2000, 2010]) |
| **Popularidad** | número (0-100) | `=` `>` `<` `>=` `<=` | Popularidad según Spotify |
| **Duración** | número (ms) | `>` `<` `between` | Duración en milisegundos |
| **Explícito** | booleano | `=` | Contenido explícito (Sí/No) |
| **Artista** | texto | `=` `contains` | Busca por nombre de artista |
| **Álbum** | texto | `=` `contains` | Busca por nombre de álbum |
| **Género** | texto | `=` `contains` | Géneros musicales del artista (rock, pop, jazz, etc.) |

### Filtros de Audio Features

Spotify analiza cada canción y devuelve estos valores numéricos (0.0 a 1.0, excepto tempo):

| Filtro | Rango | Operadores | Descripción |
|--------|-------|------------|-------------|
| **Tempo (BPM)** | 0-250+ | `>` `<` `>=` `<=` `between` | Pulsaciones por minuto |
| **Instrumentalidad** | 0.0 – 1.0 | `>` `<` `>=` `<=` | Predice si una canción no tiene voces. Cerca de 1.0 = instrumental |
| **Acousticidad** | 0.0 – 1.0 | `>` `<` `>=` `<=` | Confianza de que la pista es acústica |

### Filtros Derivados

| Filtro | Tipo | Descripción |
|--------|------|-------------|
| **Workout** | booleano (Sí/No) | Activa el preset: `energía > 0.7 AND tempo > 120 AND danceability > 0.6` |

Todos los filtros derivados se calculan a partir de los `audio_features` que Spotify ya proporciona, sin llamadas extra a la API.

---

## Crossplaylists: Lógica AND/OR

El verdadero poder de Alsort está en la combinación de filtros. Puedes mezclar criterios de metadata, audio features y derivados en una misma consulta.

**Ejemplos de combinaciones:**

| Propósito | Filtros AND | Filtros OR | Resultado |
|-----------|-------------|------------|-----------|
| Rock intenso | `año between [2000, 2024]` `tempo > 130` | `género contains "rock"` `género contains "metal"` | Rock y metal modernos de alto ritmo |
| Chill acústico | `acousticness > 0.6` `instrumentalness < 0.3` | `género contains "acoustic"` `género contains "folk"` | Acústico con voz, relajante |
| Fiesta 2020s | `año > 2020` `workout = Sí` | — | Canciones recientes y bailables |
| Madrugada | `acousticness > 0.4` `tempo < 100` | `género contains "jazz"` `género contains "ambient"` | Jazz suave o ambiental para la noche |
| Clásicos | `año between [1960, 1999]` `popularity > 50` | — | Canciones populares antiguas |

Las **canciones likeadas** se filtran en dos pasos:
1. **AND**: deben pasar **todos** los criterios AND
2. **OR**: deben pasar **al menos uno** de los criterios OR (si no hay OR, se saltan este paso)

---

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/auth/login` | Redirige a la pantalla de autorización de Spotify |
| `GET` | `/auth/callback` | Callback OAuth, intercambia código por token |
| `GET` | `/auth/me` | Obtiene información del usuario autenticado |
| `POST` | `/api/tracks/sync` | Sincroniza todas las canciones likeadas + audio features + géneros. Las guarda en SQLite |
| `POST` | `/api/tracks/filter` | Filtra canciones según criterios AND/OR. Body: `FilterRequest` |
| `POST` | `/api/playlists` | Crea una playlist en Spotify con las canciones filtradas. Body: `CreatePlaylistRequest` |

### Ejemplo de `FilterRequest`

```json
{
  "and_filters": [
    { "type": "year", "operator": "between", "value": [2010, 2024] },
    { "type": "tempo", "operator": ">", "value": 120 },
    { "type": "workout", "operator": "=", "value": true }
  ],
  "or_filters": [
    { "type": "genre", "operator": "contains", "value": "rock" },
    { "type": "genre", "operator": "contains", "value": "metal" }
  ],
  "limit": 100,
  "offset": 0
}
```

### Ejemplo de `CreatePlaylistRequest`

```json
{
  "name": "Rock Intenso - Alsort",
  "description": "Creada automáticamente con Alsort",
  "public": true,
  "filter_criteria": {
    "and_filters": [
      { "type": "year", "operator": ">", "value": 2010 },
      { "type": "workout", "operator": "=", "value": true }
    ],
    "or_filters": [],
    "limit": 200,
    "offset": 0
  }
}
```

---

## Flujo de Datos

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Navegador   │────▶│  Frontend React  │────▶│  Backend FastAPI │
│  (localhost  │     │  (localhost:5173) │     │  (localhost:8000)│
│    :5173)    │◀────│                  │◀────│                  │
└─────────────┘     └──────────────────┘     └────────┬─────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │   SQLite (cache) │
                                              │   - Usuarios     │
                                              │   - Tracks       │
                                              │   - Audio feats  │
                                              └──────────────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │  Spotify Web API │
                                              │  - Liked tracks  │
                                              │  - Audio feats   │
                                              │  - Create plylst │
                                              └──────────────────┘
```

**Proceso detallado:**

1. El usuario inicia sesión → OAuth PKCE → se almacena el token en SQLite
2. El usuario pide sincronizar → el backend trae todas las liked songs (paginado de 50 en 50)
3. Por cada canción, se obtienen los artistas (para géneros) y los audio features (BPM, energía, etc.)
4. Todo se cachea en SQLite para que las siguientes consultas sean instantáneas
5. Cuando el usuario aplica filtros, se leen de SQLite y se filtran en Python
6. Al crear una playlist, se toman las URIs de las canciones filtradas y se envían a Spotify

---

## Posibles Mejoras Futuras

- [ ] **Más filtros derivados:** Chill, Fiesta, Focus, Road Trip, Summer Vibes, etc.
- [ ] **Más audio features:** Energía, Danceability, Valence, Loudness, Speechiness, Liveness, Key
- [ ] **Exportar filtros como JSON** para compartir presets
- [ ] **Actualización incremental** de canciones (no volver a traer todas)
- [ ] **Filtros guardados** con nombres personalizados
- [ ] **Soporte para playlists existentes** (no solo liked songs)
- [ ] **Modo oscuro / modo claro** (actualmente solo oscuro)
- [ ] **Paginación en la UI** para más de 200 resultados
- [ ] **Despliegue** con Docker / docker-compose

---

<div align="center">
  <p>
    Hecho con ❤️ por <a href="https://github.com/VECTORG99">VECTORG99</a>
  </p>
  <p>
    <a href="https://github.com/VECTORG99/Proyecto_Alsort/issues">Reportar un bug</a>
    ·
    <a href="https://github.com/VECTORG99/Proyecto_Alsort/issues">Sugerir una mejora</a>
  </p>
</div>
