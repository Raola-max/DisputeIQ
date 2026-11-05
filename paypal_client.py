import os
import httpx
import traceback
from dotenv import load_dotenv

load_dotenv()

PAYPAY_BASE_URL = os.getenv("PAYPAL_BASE_URL", "https://api-m.sandbox.paypal.com")
CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
SECRET = os.getenv("PAYPAL_SECRET")

_token_cache = {"access_token": None, "expires_at": 0}

async def get_access_token() -> str:
    """Fetch (and cache) a PayPal OAuth2 access token."""
    import time
    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"] - 60:
        return _token_cache["access_token"]

    if not CLIENT_ID or not SECRET:
        raise ValueError("PayPal CLIENT_ID or SECRET is missing from environment variables.")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{PAYPAY_BASE_URL}/v1/oauth2/token",
                auth=(CLIENT_ID, SECRET),
                data={"grant_type": "client_credentials"},
                headers={
                    "Accept": "application/json",
                    "Accept-Language": "en_US",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
            )
            resp.raise_for_status()
            data = resp.json()
            _token_cache["access_token"] = data["access_token"]
            _token_cache["expires_at"] = time.time() + data.get("expires_in", 32400)
            return data["access_token"]
        except httpx.HTTPStatusError as e:
            print(f"PayPal Auth HTTP Error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            print(f"PayPal Auth Exception: {str(e)}")
            raise

async def paypal_get(path: str) -> dict:
    """Authenticated GET request to PayPal."""
    token = await get_access_token()
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{PAYPAY_BASE_URL}{path}",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            print(f"PayPal GET Error [{path}]: {e.response.status_code} - {e.response.text}")
            raise

async def paypal_post(path: str, body: dict) -> dict:
    """Authenticated POST request to PayPal."""
    token = await get_access_token()
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{PAYPAY_BASE_URL}{path}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=body,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            print(f"PayPal POST Error [{path}]: {e.response.status_code} - {e.response.text}")
            raise