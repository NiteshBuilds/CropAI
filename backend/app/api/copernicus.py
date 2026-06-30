"""
copernicus.py  (api router)
───────────────────────────
Endpoints for interacting with the Copernicus Data Space Ecosystem.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import logging

from app.services.copernicus_auth_service import copernicus_auth_service, CopernicusAuthError
from app.schemas.copernicus import AuthenticationStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/copernicus", tags=["Copernicus"])


class AuthenticationResponse(BaseModel):
    """Response schema for a successful authentication attempt."""
    authenticated: bool
    expires_in: int


@router.get(
    "/status",
    response_model=AuthenticationStatus,
    summary="Check Copernicus authentication status",
    description="Returns the current configuration and authentication status for the Copernicus service.",
)
async def get_copernicus_status() -> AuthenticationStatus:
    """Return the configuration and authentication status."""
    return AuthenticationStatus(
        configured=copernicus_auth_service.is_configured,
        authenticated=copernicus_auth_service.is_authenticated,
        expires_in=copernicus_auth_service.expires_in,
    )


@router.post(
    "/authenticate",
    response_model=AuthenticationResponse,
    summary="Authenticate with Copernicus",
    description="Attempts to login and retrieve an access token from Copernicus.",
)
async def authenticate_copernicus() -> AuthenticationResponse:
    """Attempt authentication and return the result."""
    try:
        await copernicus_auth_service.authenticate()
        
        expires_in = copernicus_auth_service.expires_in
        if expires_in is None:
            # Fallback if somehow expires_in is None but authenticate succeeded without raising error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication succeeded but token expiry is unavailable."
            )
            
        return AuthenticationResponse(
            authenticated=True,
            expires_in=expires_in
        )
    except CopernicusAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc)
        )
