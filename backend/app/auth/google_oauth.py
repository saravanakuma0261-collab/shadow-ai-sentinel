import logging
from typing import Optional, Dict, Any
import httpx
try:
    from authlib.integrations.starlette_client import OAuth
except ImportError:
    from authlib.integrations.starlette_integration import OAuth
from app.config import settings

logger = logging.getLogger(__name__)

oauth = OAuth()

if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid email profile"
        }
    )
else:
    logger.info("Google OAuth Client ID/Secret not configured; Google Sign-in will operate in demo/placeholder mode.")


async def verify_google_token_or_code(code: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
    """
    Exchanges authorization code for Google tokens and fetches user profile.
    Returns dict with email, name, sub (google_id), or None on failure.
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        # Dev / Demo mock fallback when keys aren't set
        logger.warning("Mocking Google OAuth callback because Google credentials are not set in .env")
        return {
            "sub": "google_demo_123456789",
            "email": "demo.google.user@example.com",
            "name": "Google Demo User",
            "picture": "https://lh3.googleusercontent.com/a/default-user"
        }

    token_url = "https://oauth2.googleapis.com/token"
    userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            token_url,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            logger.error(f"Google token exchange failed: {token_resp.text}")
            return None

        token_data = token_resp.json()
        access_token = token_data.get("access_token")

        userinfo_resp = await client.get(
            userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if userinfo_resp.status_code != 200:
            logger.error(f"Google userinfo request failed: {userinfo_resp.text}")
            return None

        return userinfo_resp.json()
