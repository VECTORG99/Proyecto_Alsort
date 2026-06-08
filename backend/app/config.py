import sys
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    spotify_redirect_uri: str = "http://localhost:8000/auth/callback"
    session_secret: str = ""
    database_url: str = "sqlite+aiosqlite:///./data/alsort.db"
    frontend_url: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

if not settings.spotify_client_id or "tu_client_id" in settings.spotify_client_id:
    print("ERROR: SPOTIFY_CLIENT_ID no está configurada. Revisa backend/.env", file=sys.stderr)
    sys.exit(1)

if not settings.session_secret or "change" in settings.session_secret.lower():
    print("ERROR: SESSION_SECRET no está configurada o usa valor por defecto. Revisa backend/.env", file=sys.stderr)
    sys.exit(1)
