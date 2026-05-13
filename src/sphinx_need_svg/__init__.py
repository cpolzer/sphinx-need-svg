from __future__ import annotations

from typing import Any

from sphinx.application import Sphinx

from sphinx_need_svg.directives.needsvg import (
    Needsvg,
    NeedsvgDirective,
    process_needsvg,
)


def setup(app: Sphinx) -> dict[str, Any]:
    """Sphinx extension entry point."""
    app.add_node(Needsvg)
    app.add_directive("needsvg", NeedsvgDirective)
    app.connect("doctree-resolved", process_needsvg)

    return {
        "version": "0.2.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
