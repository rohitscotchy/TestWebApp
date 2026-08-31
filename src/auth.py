import os

from fastapi import Header, HTTPException, status


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

    # Validate Authorization header
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
        )

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header. Use 'Bearer <token>'.",
        )

    if token.strip() != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token.",
        )

    # Support both client-id headers
    provided_client_id = x_client_id or client_id

    if not provided_client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing client ID.",
        )

    if provided_client_id != expected_client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client ID.",
        )

    return {
        "token_valid": True,
        "client_id": provided_client_id,
    }