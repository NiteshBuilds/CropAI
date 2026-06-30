from pydantic import BaseModel
from typing import Optional


class AccessTokenResponse(BaseModel):
    """Response schema from the Copernicus OAuth token endpoint."""

    access_token: str
    expires_in: int
    refresh_expires_in: int
    refresh_token: str
    token_type: str
    not_before_policy: int = 0
    session_state: str
    scope: str


class AuthenticationStatus(BaseModel):
    """Response schema for the Copernicus authentication status endpoint."""

    configured: bool
    authenticated: bool
    expires_in: Optional[int] = None
