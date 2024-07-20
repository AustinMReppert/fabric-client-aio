"""Fabric Client Error module."""

from fabricclientaio.models.responses import ErrorResponse


class FabricClientError(Exception):
    """Base class for exceptions in this module."""

    error_response: ErrorResponse

    def __init__(self, error_response: ErrorResponse) -> None:
        """Initialize the Fabric Client Error."""
        self.error_response = error_response
        super().__init__(error_response.message)