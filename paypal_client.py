import os
import httpx
from dotenv import load_dotenv

load_dotenv()

PAYPAL_BASE_URL = os.getenv("PAYPAL_BASE_URL")
CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
SECRET = os.getenv("PAYPAL_SECRET")

_token_cache = {"access_token": None, "expires_at": 0}


async def get_access_token() -> str:
    """Fetch (and cache) a PayPal OAuth2 access token."""
    import time
    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"] - 60:
        return _token_cache["access_token"]

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{PAYPAL_BASE_URL}/v1/oauth2/token",
            auth=(CLIENT_ID, SECRET),
            data={"grant_type": "client_credentials"},
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()
        _token_cache["access_token"] = data["access_token"]
        _token_cache["expires_at"] = time.time() + data["expires_in"]
        return data["access_token"]


async def paypal_get(path: str) -> dict:
    """Authenticated GET request to PayPal."""
    token = await get_access_token()
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{PAYPAL_BASE_URL}{path}",
            headers={"Authorization": f"Bearer {token}"},
        )
        resp.raise_for_status()
        return resp.json()


async def paypal_post(path: str, body: dict) -> dict:
    """Authenticated POST request to PayPal."""
    token = await get_access_token()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{PAYPAL_BASE_URL}{path}",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=body,
        )
        resp.raise_for_status()
        return resp.json()