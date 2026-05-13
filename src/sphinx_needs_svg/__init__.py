from __future__ import annotations

from typing import Any


def setup(app: Any) -> dict[str, Any]:
    """Sphinx extension entry point."""
    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
