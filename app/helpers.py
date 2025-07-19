import os

from dotenv import load_dotenv

def getenv(key: str, default: str | None = None) -> str:
    load_dotenv()
    value = os.getenv(key)  # noqa: F821

    if value is not None:
        return value

    if default is not None:
        return default

    raise ValueError(f"key {key} not defined")