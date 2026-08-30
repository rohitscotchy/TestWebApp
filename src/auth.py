import os

from dotenv import load_dotenv
from fastapi import Header, HTTPException, status

load_dotenv()


def get_expected_bearer_token() -> str:
    return os.getenv("API_BEARER_TOKEN", "test-token")


def get_expected_client_id() -> str:
    return os.getenv("CLIENT_ID", "test-client")


def require_api_auth(
    authorization: str | None = Header(default=None),
    x_client_id: str | None = Header(default=None, alias="X-Client-Id"),
    client_id: str | None = Header(default=None, alias="client-id"),
):
    expected_token = get_expected_bearer_token()
    expected_client_id = get_expected_client_id()

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header. Use 'Authorization: Bearer <token>'.",
        )

    token = authorization.split(" ", 1)[1].strip()
    if token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token.",
        )

    provided_client_id = x_client_id or client_id
    if not provided_client_id or provided_client_id != expected_client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid client ID.",
        )

    return {
        "token_valid": True,
        "client_id": provided_client_id,
    }
