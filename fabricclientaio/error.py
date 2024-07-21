"""Fabric Client Error module."""

from fabricclientaio.models.responses import ErrorResponse


class FabricClientError(Exception):
    """Base class for exceptions in this module."""

    status_code: int
    error_response: ErrorResponse

    def __init__(self, status_code:int, error_response: ErrorResponse) -> None:
        """Initialize the Fabric Client Error."""
        self.status_code = status_code
        self.error_response = error_response
        super().__init__(f"Error {status_code}: {error_response.model_dump_json}")
