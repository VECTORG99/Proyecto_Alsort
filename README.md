# Alsort

Gestor inteligente de playlists de Spotify. Extrae tus canciones likeadas, filtra por múltiples criterios (año, BPM, género, energía, etc.) y crea playlists automáticamente.

## Stack

- **Frontend:** React + Vite + TypeScript
- **Backend:** Python + FastAPI + SQLite
- **API:** Spotify Web API

## Requisitos

- Python 3.11+
- Node.js 18+
- Una app registrada en [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

## Configuración

1. Clona el repo y entra al directorio:
```bash
git clone <repo-url>
cd Proyecto_Alsort
```

2. Configura el backend:
```bash
cd backend
cp .env.example .env
# Edita .env con tu SPOTIFY_CLIENT_ID y SPOTIFY_CLIENT_SECRET
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

3. Configura el frontend:
```bash
cd frontend
npm install
npm run dev
```

4. Abre `http://localhost:5173`

## Uso

1. Inicia sesión con Spotify
2. Haz clic en "Sincronizar likes" para cargar tus canciones
3. Añade filtros (AND y/u OR)
4. Previsualiza los resultados
5. Dale nombre a tu playlist y créala

## Filtros disponibles

- Año / Década
- Popularidad
- Duración
- Explícito
- Artista, Álbum, Género
- Instrumentalidad, Acousticidad
- Tempo (BPM)
- Workout (alto rendimiento)
