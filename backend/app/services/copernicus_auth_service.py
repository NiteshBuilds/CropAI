"""
copernicus_auth_service.py
──────────────────────────
Service handling authentication for the Copernicus Data Space Ecosystem (CDSE).

Responsibilities:
- Authenticate with CDSE OpenID Connect using username/password
- Retrieve access token
- Handle token expiry and refresh
- Raise meaningful exceptions on failure
"""

import httpx
import logging
import time
from typing import Optional

from app.core.api_config import CopernicusConfig, copernicus_config
from app.schemas.copernicus import AccessTokenResponse

logger = logging.getLogger(__name__)


class CopernicusAuthError(Exception):
    """Raised when Copernicus authentication fails."""
    pass


class CopernicusAuthService:
    """Service to handle authentication with Copernicus Data Space Ecosystem."""

    def __init__(self, config: CopernicusConfig = copernicus_config):
        self._config = config
        self._access_token: Optional[str] = None
        self._token_expiry_time: float = 0
        self._refresh_token: Optional[str] = None
        # Safety buffer before actual expiration (in seconds) to trigger refresh
        self._expiry_buffer: int = 60

    @property
    def is_configured(self) -> bool:
        """Check if username and password are provided in settings."""
        return self._config.is_configured

    @property
    def is_authenticated(self) -> bool:
        """Check if a valid access token is currently held."""
        if not self._access_token:
            return False
        return time.time() < (self._token_expiry_time - self._expiry_buffer)

    @property
    def expires_in(self) -> Optional[int]:
        """Returns the number of seconds until the token expires, or None if not authenticated."""
        if not self.is_authenticated:
            return None
        return int(self._token_expiry_time - time.time())

    async def authenticate(self) -> bool:
        """
        Authenticate with Copernicus using username and password.
        
        Raises:
            CopernicusAuthError: If authentication fails.
        """
        if not self.is_configured:
            raise CopernicusAuthError("Copernicus credentials are not configured.")

        logger.info("Authentication started")

        data = {
            "client_id": "cdse-public",
            "grant_type": "password",
            "username": self._config.username,
            "password": self._config.password,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self._config.auth_url,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
            if response.status_code != 200:
                logger.error("Authentication failed")
                raise CopernicusAuthError(
                    f"Failed to authenticate with Copernicus. Status: {response.status_code}, Detail: {response.text}"
                )

            token_data = AccessTokenResponse(**response.json())
            self._access_token = token_data.access_token
            self._refresh_token = token_data.refresh_token
            self._token_expiry_time = time.time() + token_data.expires_in
            
            logger.info("Authentication successful")
            return True
            
        except httpx.RequestError as exc:
            logger.error("Authentication failed")
            raise CopernicusAuthError(f"Network error during authentication: {exc}")

    async def get_valid_token(self) -> str:
        """
        Get a valid access token, authenticating or refreshing if necessary.
        
        Raises:
            CopernicusAuthError: If authentication fails.
        """
        if not self.is_authenticated:
            await self.authenticate()
            
        if not self._access_token:
             raise CopernicusAuthError("Failed to obtain a valid access token.")
             
        return self._access_token

# Singleton instance to be used across the application
copernicus_auth_service = CopernicusAuthService()
