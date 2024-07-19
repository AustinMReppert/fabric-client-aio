"""FabricClient class."""
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from fabricclientaio.utils.timeutils import get_current_unix_timestamp

if TYPE_CHECKING:
    from azure.core.credentials import AccessToken

    from fabricclientaio.auth.fabrictokenprovider import FabricTokenProvider


class FabricClient:
    """FabricClient class."""

    _fabric_token_provider: FabricTokenProvider
    _base_url: str = "https://api.fabric.microsoft.com/v1"
    _token: AccessToken | None = None
    _lock = asyncio.Lock()

    def __init__(self, fabric_token_provider: FabricTokenProvider, base_url: str | None = None) -> None:
        """Initialize Fabric Client.

        Parameters
        ----------
        fabric_token_provider : FabricTokenProvider
            The token provider used to retrieve authentication tokens.
        base_url : str, optional
            The base URL of the Fabric API, use the default if None.

        """
        self.fabric_token_provider = fabric_token_provider
        if base_url:
            self._base_url = base_url

    @property
    def base_url(self) -> str:
        """Get the base URL of the Fabric API.

        Returns
        -------
        str
            The base URL of the Fabric API.

        """
        return self._base_url

    async def _get_token(self) -> str:
        """Retrieve the authentication token for the fabric client.

        If the token is not available or has expired, it requests a new token from the fabric token provider.

        Returns
        -------
        str
            The authentication token.

        """
        # Lock to ensure only one request for a token is made at a time.
        # This is to prevent multiple requests for a token when the token has expired.
        async with self._lock:
            if not self._token or self._token.expires_on < get_current_unix_timestamp():
                self._token = await self.fabric_token_provider.get_token()
            return self._token.token


    async def get_auth_headers(self) -> dict[str, str]:
        """Get the authentication headers for the fabric client.

        Returns
        -------
        dict[str, str]
            The authentication headers.

        """
        token = await self._get_token()
        return {"Authorization": f"Bearer {token}"}
