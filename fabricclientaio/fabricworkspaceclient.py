"""Fabric Workspace Client module."""
from __future__ import annotations

from typing import TYPE_CHECKING, AsyncGenerator

from fabricclientaio.models.responses import Item, Items, WorkspaceInfo

if TYPE_CHECKING:
    from fabricclientaio.fabricclient import FabricClient


class FabricWorkspaceClient:
    """Fabric Workspace Client class."""

    _fabric_client: FabricClient
    _workspace_id: str

    def __init__(self, fabric_client: FabricClient, workspace_id: str) -> None:
        """Initialize Fabric Workspace Client."""
        self._fabric_client = fabric_client
        self._workspace_id = workspace_id

    async def get_workspace(self) -> WorkspaceInfo:
        """Get Workspace.

        Retrieves the workspace from the Fabric API.

        https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces/get-workspace?tabs=HTTP

        Returns
        -------
        WorkspaceInfo
            A workspace object.

        """
        url = f"{self._fabric_client.base_url}/workspaces/{self._workspace_id}"

        workspace_json = await self._fabric_client.get(url)
        return WorkspaceInfo(**workspace_json)


    async def get_items(self, item_type: str | None = None) -> AsyncGenerator[Item, None]:
        """Get Items From a Workspace.

        Retrieves the list of items from the workspace.

        https://learn.microsoft.com/en-us/rest/api/fabric/core/items/list-items

        Parameters
        ----------
        item_type : str, optional
            The type of item to filter the items by, by default None.

        Yields
        ------
        Item
            An item object.

        """
        url = f"{self._fabric_client.base_url}/workspaces/{self._workspace_id}/items"
        params: dict[str, str] = {}
        if item_type:
            params["type"] = item_type

        async for items_json in self._fabric_client.get_paged(url, params):
            items = Items(**items_json)
            for item in items.value:
                yield item


