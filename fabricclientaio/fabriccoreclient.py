"""Fabric Core Client module."""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncGenerator

import aiohttp

from fabricclientaio.models.responses import Workspace, Workspaces

if TYPE_CHECKING:
    from fabricclientaio.fabricclient import FabricClient


class FabricCoreClient:
    """Fabric Core Client class."""

    _fabric_client: FabricClient

    def __init__(self, fabric_client: FabricClient) -> None:
        """Initialize Fabric Core Client."""
        self._fabric_client = fabric_client


    async def get_workspaces(self, roles: list[str] | None = None) -> AsyncGenerator[Workspace, None]:
        """Get Workspaces.

        Retrieves the list of workspaces from the Fabric API.

        https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/list-workspaces?tabs=HTTP

        Parameters
        ----------
        roles : list[str], optional
            A list of roles to filter the workspaces by, by default None.

        Yields
        ------
        Workspace
            A workspace object.

        """
        url = f"{self._fabric_client.base_url}/workspaces"
        params: dict[str, str] = {}
        if roles:
            params["roles"] = ",".join(roles)
        headers = await self._fabric_client.get_auth_headers()

        has_next_page = True

        while has_next_page:
            async with aiohttp.ClientSession() as session, session.get(url, params=params, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                workspaces = Workspaces(**data)
                for workspace in workspaces.value:
                    yield workspace
                if workspaces.continuation_uri and workspaces.continuation_token:
                    url = workspaces.continuation_uri
                    params = {"continuationToken": workspaces.continuation_token}
                else:
                    has_next_page = False
