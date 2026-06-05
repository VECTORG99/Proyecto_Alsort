from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    spotify_redirect_uri: str = "http://localhost:8000/auth/callback"
    session_secret: str = "alsort-secret-key-change-in-production"
    database_url: str = "sqlite+aiosqlite:///./alsort.db"
    frontend_url: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
