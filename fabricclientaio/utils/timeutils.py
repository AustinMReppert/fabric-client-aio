"""Time-related utility functions."""

import time


def get_current_unix_timestamp() -> int:
    """Get the current Unix timestamp."""
    return int(time.time())
