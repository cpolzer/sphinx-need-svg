from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

from sphinx_needs_svg.jinja_context import render_jinja_svg

logger = logging.getLogger(__name__)


class Needsvg(nodes.General, nodes.Element):  # type: ignore[misc]
    """Placeholder node replaced during doctree-resolved."""

    pass


class NeedsvgDirective(SphinxDirective):
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    option_spec: ClassVar[dict[str, Any]] = {
        "width": directives.unchanged,
        "height": directives.unchanged,
        "align": lambda x: directives.choice(x, ("left", "center", "right")),
        "debug": directives.flag,
    }

    def run(self) -> Sequence[nodes.Node]:
        env = self.state.document.settings.env
        serial = env.new_serialno("needsvg")
        targetid = f"needsvg-{env.docname}-{serial}"

        if not hasattr(env, "needsvg_all_data"):
            env.needsvg_all_data = {}

        env.needsvg_all_data[targetid] = {
            "docname": env.docname,
            "lineno": self.lineno,
            "content": "\n".join(self.content),
            "options": {
                "width": self.options.get("width", "100%"),
                "height": self.options.get("height", "auto"),
                "align": self.options.get("align", "center"),
                "debug": "debug" in self.options,
            },
        }

        targetnode = nodes.target("", "", ids=[targetid])
        node = Needsvg("")
        node["targetid"] = targetid

        return [targetnode, node]


def process_needsvg(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    """Replace Needsvg placeholder nodes with rendered SVG."""
    env = app.builder.env
    data_store: dict[str, Any] = getattr(env, "needsvg_all_data", {})

    for node in doctree.findall(Needsvg):
        targetid = node["targetid"]
        data = data_store.get(targetid)
        if data is None:
            node.replace_self([])
            continue

        try:
            svg_content = render_jinja_svg(data["content"], app)
        except Exception as e:
            logger.warning(f"needsvg error at {data['docname']}:{data['lineno']}: {e}")
            svg_content = f'<svg><text fill="red">needsvg error: {e}</text></svg>'
        options = data["options"]

        align = options.get("align", "center")
        wrapper = f'<div style="text-align: {align}">{svg_content}</div>'

        content_nodes: list[nodes.Node] = [
            nodes.raw("", wrapper, format="html"),
        ]

        if options.get("debug"):
            raw_source = data["content"]
            rst_block = ".. needsvg::\n\n"
            for line in raw_source.splitlines():
                rst_block += f"   {line}\n"
            code = nodes.literal_block(rst_block, rst_block)
            code["language"] = "rst"
            content_nodes.insert(0, code)

        node.replace_self(content_nodes)
