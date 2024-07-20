"""FabricClient class."""
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, AsyncGenerator

import aiohttp

from fabricclientaio.models.responses import LongRunningOperationStatus, OperationState
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


    async def get(self, url: str, params: dict[str, str] | None = None, headers: dict[str, str] | None = None) -> dict:
        """Make a GET request to the Fabric API.

        Parameters
        ----------
        url : str
            The URL to make the request to.
        params : dict[str, str], optional
            The parameters to include in the request.
        headers : dict[str, str], optional
            The headers to include in the request.

        Returns
        -------
        dict
            The response from the request.

        """
        headers = headers.copy() if headers is not None else {}

        if "Authorization" not in headers:
            headers = await self.get_auth_headers()

        async with aiohttp.ClientSession() as session, session.get(url, params=params, headers=headers) as response:
            response.raise_for_status()
            return await response.json()


    async def get_paged(
        self,
        url: str,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> AsyncGenerator[dict, None]:
        """Make a GET request to the Fabric API that returns paged results.

        Parameters
        ----------
        url : str
            The URL to make the request to.
        params : dict[str, str], optional
            The parameters to include in the request.
        headers : dict[str, str], optional
            The headers to include in the request.

        Yields
        ------
        dict
            The response from the request.

        """
        has_next_page = True

        while has_next_page:
            data = await self.get(url, params, headers)
            yield data

            if "continuationUri" in data and "continuationToken" in data:
                url = data["continuationUri"]
                params = {"continuationToken": data["continuationToken"]}
            else:
                has_next_page = False

    async def get_long_running_job(
        self,
        url: str,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict:
        """Make a GET request to the Fabric API for a long running job.

        Parameters
        ----------
        url : str
            The URL to make the request to.
        params : dict[str, str], optional
            The parameters to include in the request.
        headers : dict[str, str], optional
            The headers to include in the request.

        Returns
        -------
        dict
            The response from the request.

        """
        headers = headers.copy() if headers is not None else {}

        if "Authorization" not in headers:
            headers = await self.get_auth_headers()

        async with aiohttp.ClientSession() as session, session.post(url, params=params, headers=headers) as response:
            response.raise_for_status()
            if response.status == 200:
                return await response.json()

        if response.status != 202:
            raise Exception(f"Failed to get long running job: {response.status}")

        operation_id = response.headers["x-ms-operation-id"]
        retry_after: int = int(response.headers["Retry-After"])
        location = response.headers["Location"]

        is_waiting = True
        while is_waiting:
            await asyncio.sleep(retry_after)
            async with aiohttp.ClientSession() as session, session.get(url=location, headers=headers) as response:
                response.raise_for_status()

                retry_after = int(response.headers.get("Retry-After", "5"))
                location = response.headers["Location"]

                operation_json = await response.json()
                operation_result = OperationState(**operation_json)
                if operation_result.is_completed():
                    is_waiting = False

        return await self.get(location)

