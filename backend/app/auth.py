import uuid
import hashlib
import base64
import json
import httpx
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .config import settings
from .database import get_session, User
from .logger import logger

router = APIRouter(prefix="/auth", tags=["auth"])


def generate_code_verifier() -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(64)).decode().rstrip("=")


def generate_code_challenge(verifier: str) -> str:
    return base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).decode().rstrip("=")


@router.get("/login")
async def login():
    verifier = generate_code_verifier()
    challenge = generate_code_challenge(verifier)

    state = secrets.token_urlsafe(32)

    spotify_state = base64.urlsafe_b64encode(
        json.dumps({"v": verifier, "s": state}).encode()
    ).decode()

    params = (
        f"response_type=code"
        f"&client_id={settings.spotify_client_id}"
        f"&scope=user-library-read playlist-modify-public playlist-modify-private"
        f"&redirect_uri={settings.spotify_redirect_uri}"
        f"&state={spotify_state}"
        f"&code_challenge_method=S256"
        f"&code_challenge={challenge}"
    )

    logger.info("Redirecting to Spotify OAuth")
    response = RedirectResponse(url=f"https://accounts.spotify.com/authorize?{params}")
    return response


@router.get("/callback")
async def callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_session),
):

    if error:
        logger.warning("OAuth callback error=%s", error)
        return RedirectResponse(url=f"{settings.frontend_url}/?error={error}")

    if not code or not state:
        logger.warning("OAuth callback missing params")
        return RedirectResponse(url=f"{settings.frontend_url}/?error=missing_params")

    try:
        state_data = json.loads(base64.urlsafe_b64decode(state + "==").decode())
        verifier = state_data["v"]
    except Exception:
        logger.error("Invalid OAuth state")
        raise HTTPException(status_code=400, detail="Invalid state")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.spotify_redirect_uri,
                "client_id": settings.spotify_client_id,
                "code_verifier": verifier,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if resp.status_code != 200:
        logger.error("Failed to exchange code for token status=%d", resp.status_code)
        raise HTTPException(status_code=400, detail="Failed to get token")

    token_data = resp.json()
    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token", "")
    expires_in = token_data["expires_in"]
    expires_at = datetime.now(timezone.utc).timestamp() + expires_in

    async with httpx.AsyncClient() as client:
        me_resp = await client.get(
            "https://api.spotify.com/v1/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    if me_resp.status_code != 200:
        logger.error("Failed to fetch user info status=%d", me_resp.status_code)
        raise HTTPException(status_code=400, detail="Failed to get user info")

    me_data = me_resp.json()
    spotify_id = me_data["id"]

    result = await db.execute(select(User).where(User.spotify_id == spotify_id))
    user = result.scalar_one_or_none()

    if user:
        user.access_token = access_token
        user.refresh_token = refresh_token or user.refresh_token
        user.token_expires_at = expires_at
        logger.info("Existing user logged in spotify_id=%s", spotify_id)
    else:
        user = User(
            spotify_id=spotify_id,
            display_name=me_data.get("display_name"),
            email=me_data.get("email"),
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=expires_at,
        )
        db.add(user)
        logger.info("New user registered spotify_id=%s", spotify_id)

    await db.commit()
    await db.refresh(user)

    session_token = user.id
    redirect_url = f"{settings.frontend_url}/?session={session_token}"
    logger.info("OAuth complete spotify_id=%s redirecting", spotify_id)
    return RedirectResponse(url=redirect_url)


@router.get("/me")
async def get_me(request: Request, db: AsyncSession = Depends(get_session)):
    session_id = request.headers.get("X-Session-Id") or request.cookies.get("session_id")
    if not session_id:
        logger.warning("get_me called without session")
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await db.execute(select(User).where(User.id == session_id))
    user = result.scalar_one_or_none()
    if not user:
        logger.warning("Invalid session id=%s", session_id)
        raise HTTPException(status_code=401, detail="Invalid session")

    if datetime.now(timezone.utc).timestamp() > user.token_expires_at:
        try:
            await refresh_spotify_token(user, db)
        except HTTPException as e:
            if e.status_code == 401:
                logger.warning("Session expired spotify_id=%s", user.spotify_id)
                raise HTTPException(
                    status_code=401,
                    detail="Session expired. Please login again.",
                )
            raise

    return {"id": user.id, "spotify_id": user.spotify_id, "display_name": user.display_name}


async def refresh_spotify_token(user: User, db: AsyncSession):

    if not user.refresh_token:
        logger.warning("No refresh token for user spotify_id=%s", user.spotify_id)
        raise HTTPException(
            status_code=401,
            detail="No refresh token available. Spotify no proporcionó un refresh_token con PKCE. Debes iniciar sesión de nuevo.",
        )

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": user.refresh_token,
                "client_id": settings.spotify_client_id,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if resp.status_code != 200:
        logger.warning("Token refresh failed spotify_id=%s status=%d", user.spotify_id, resp.status_code)
        raise HTTPException(status_code=401, detail="Failed to refresh token. Please login again.")

    token_data = resp.json()
    user.access_token = token_data["access_token"]
    if "refresh_token" in token_data:
        user.refresh_token = token_data["refresh_token"]
    user.token_expires_at = datetime.now(timezone.utc).timestamp() + token_data["expires_in"]
    logger.info("Token refreshed spotify_id=%s", user.spotify_id)
    await db.commit()
