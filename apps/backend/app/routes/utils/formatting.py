"""Helpers for parsing/formatting request and response data in routes."""


def parse_version_header(value: str | None) -> int | None:
    """Parse If-Match or If-None-Match to integer version, or None if missing/invalid."""
    if value is None or not value.strip():
        return None
    s = value.strip().strip('"')
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None
