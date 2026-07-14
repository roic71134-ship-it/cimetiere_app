"""Configuration et client API pour le frontend."""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# Token stocké en mémoire (session)
_token: str = ""
_user_info: dict = {}


def set_token(token: str, user_info: dict):
    global _token, _user_info
    _token = token
    _user_info = user_info


def get_headers() -> dict:
    return {"Authorization": f"Bearer {_token}", "Content-Type": "application/json"}


def get_user_info() -> dict:
    return _user_info


def api_post(endpoint: str, data: dict, auth: bool = True) -> tuple[bool, dict]:
    """POST vers l'API."""
    headers = get_headers() if auth else {"Content-Type": "application/json"}
    try:
        r = requests.post(f"{API_BASE_URL}{endpoint}", json=data, headers=headers, timeout=10)
        return r.ok, r.json()
    except Exception as e:
        return False, {"message": str(e)}


def api_get(endpoint: str, params: dict = None) -> tuple[bool, any]:
    """GET vers l'API."""
    try:
        r = requests.get(f"{API_BASE_URL}{endpoint}", headers=get_headers(),
                         params=params or {}, timeout=10)
        return r.ok, r.json()
    except Exception as e:
        return False, {"message": str(e)}
