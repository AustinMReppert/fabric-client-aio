# fabric-client-aio

An async Python client for the Microsoft Fabric REST API.

## Usage

```python
from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential
from fabricclientaio.auth.fabrictokenprovider import FabricTokenProvider
from fabricclientaio.fabricclient import FabricClient
from fabricclientaio.fabriccoreclient import FabricCoreClient
from fabricclientaio.fabricworkspaceclient import FabricWorkspaceClient


class DefaultAzureCredentialProvider(FabricTokenProvider):
    def __init__(self):
        pass

    async def get_token(self) -> AccessToken:
        default_credentials = DefaultAzureCredential()
        return default_credentials.get_token("https://api.fabric.microsoft.com/.default")


async def main() -> None:
    fabric_client = FabricClient(DefaultAzureCredentialProvider())
    fabric_core_client = FabricCoreClient(fabric_client)

    async for workspace in fabric_core_client.get_workspaces():
        print(f"Workspace: {workspace.display_name}")
        workspace_client = FabricWorkspaceClient(fabric_client, workspace.id)
        async for item in workspace_client.get_items():
            print(f"\tItem: {item.display_name} - {item.type}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```


## Contributing

Contributions are welcome!
