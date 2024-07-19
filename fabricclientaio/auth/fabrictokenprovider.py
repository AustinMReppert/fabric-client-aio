"""Fabric Token Provider Interface."""

from abc import ABC, abstractmethod

from azure.core.credentials import AccessToken


class FabricTokenProvider(ABC):
    """Fabric Token Provider Interface."""

    @abstractmethod
    async def get_token(self) -> AccessToken:
        """Get Fabric Token."""
