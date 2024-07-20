"""Fabric Core Client module."""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncGenerator

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

        async for workspaces_json in self._fabric_client.get_paged(url, params=params):
            workspaces = Workspaces(**workspaces_json)
            for workspace in workspaces.value:
                yield workspace
