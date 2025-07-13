import json
from typing import Optional

from fastapi import Header, HTTPException, status


def _load_authorized_keys() -> dict:
    """Helper function to load and parse the authorized keys JSON file."""
    try:
        with open("data/authorized_keys.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # In a production environment, you should log this error.
        return {}


def get_key_info(api_key: str) -> Optional[dict]:
    """
    Validates an API key and returns the associated key information if valid.

    Args:
        api_key: The API key to validate.

    Returns:
        A dictionary with key information if the key is valid, otherwise None.
    """
    if not api_key:
        return None

    authorized_keys = _load_authorized_keys()
    return authorized_keys.get(api_key)


async def get_api_key(x_api_key: str = Header(..., description="The API Key for authentication.")):
    """
    FastAPI dependency to protect HTTP endpoints.

    It validates the API key from the 'X-API-Key' header.
    If the key is invalid or missing, it raises an HTTPException.
    """
    key_info = get_key_info(x_api_key)
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key",
        )
    return key_info
