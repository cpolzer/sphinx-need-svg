from __future__ import annotations

from typing import Any

from jinja2 import Environment


class SvgJinjaContext:
    """Provides Jinja2 context for needsvg templates."""

    def __init__(self, app: Any) -> None:
        self._app = app
        self._needs = self._load_needs()

    def _load_needs(self) -> dict[str, Any]:
        try:
            from sphinx_needs.data import SphinxNeedsData
            return {k: v for k, v in SphinxNeedsData(self._app.env).get_needs_view().items()}
        except Exception:
            return {}

    @property
    def needs(self) -> dict[str, Any]:
        return self._needs

    def ref(self, need_id: str) -> str:
        """Return the URL anchor for a need."""
        need = self._needs.get(need_id)
        if need is None:
            return f"#UNKNOWN-{need_id}"
        docname = need.get("docname", "")
        return f"{docname}.html#{need_id}"

    def filter(self, filter_string: str) -> list[Any]:
        """Return needs matching a filter expression."""
        try:
            from sphinx_needs.config import NeedsSphinxConfig
            from sphinx_needs.filter_common import filter_needs_view
            from sphinx_needs.data import SphinxNeedsData

            needs_view = SphinxNeedsData(self._app.env).get_needs_view()
            needs_config = NeedsSphinxConfig(self._app.config)
            return list(filter_needs_view(needs_view, needs_config, filter_string))
        except Exception:
            return []

    def flow(self, need_id: str) -> str:
        """Return a pre-styled SVG <g> element for a need."""
        need = self._needs.get(need_id)
        if need is None:
            return f'<g><text fill="red">Unknown: {need_id}</text></g>'
        title = need.get("title", need_id)
        link = self.ref(need_id)
        return (
            f'<a href="{link}">'
            f'<g>'
            f'<rect width="120" height="40" rx="4" fill="#ddeeff" stroke="#336699"/>'
            f'<text x="60" y="16" text-anchor="middle" font-size="10" fill="#666">{need_id}</text>'
            f'<text x="60" y="30" text-anchor="middle" font-size="11">{title}</text>'
            f'</g>'
            f'</a>'
        )

    def get_context(self) -> dict[str, Any]:
        return {
            "needs": self._needs,
            "ref": self.ref,
            "filter": self.filter,
            "flow": self.flow,
        }


def render_jinja_svg(content: str, app: Any) -> str:
    """Render a Jinja2 template string with needs-aware context."""
    ctx = SvgJinjaContext(app)
    env = Environment()
    template = env.from_string(content)
    return template.render(**ctx.get_context())
