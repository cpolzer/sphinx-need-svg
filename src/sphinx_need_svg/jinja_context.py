from __future__ import annotations

from typing import Any

from jinja2 import Environment


class SvgJinjaContext:
    """Provides Jinja2 context for needsvg templates."""

    def __init__(self, app: Any, fromdocname: str | None = None) -> None:
        self._app = app
        self._fromdocname = fromdocname
        self._needs = self._load_needs()

    def _load_needs(self) -> dict[str, Any]:
        try:
            from sphinx_needs.data import SphinxNeedsData

            view = SphinxNeedsData(self._app.env).get_needs_view()
            return dict(view.items())
        except Exception:
            return {}

    @property
    def needs(self) -> dict[str, Any]:
        """Dict of all needs keyed by ID. Access fields like needs['REQ_001'].title."""
        return self._needs

    def ref(self, need_id: str) -> str:
        """Return the URL anchor for a need, relative to the rendering page.

        When ``fromdocname`` is known (the docname of the page into which
        the needsvg is being rendered), the URL is computed via
        ``builder.get_relative_uri`` so it is correct regardless of where
        the source page and the target need's page live in the doctree:

        * Same page: returns ``#NEED-ID`` (pure fragment anchor).
        * Sibling page: returns ``sibling.html#NEED-ID``.
        * Cross-directory: returns ``../path/to/page.html#NEED-ID``.

        Without ``fromdocname`` (e.g. when called outside of the directive
        pipeline), falls back to the unscoped ``{docname}.html#{id}`` form.
        """
        need = self._needs.get(need_id)
        if need is None:
            return f"#UNKNOWN-{need_id}"
        target_docname = need.get("docname", "")
        if not target_docname:
            return f"#{need_id}"
        if self._fromdocname is None:
            return f"{target_docname}.html#{need_id}"
        try:
            base = self._app.builder.get_relative_uri(self._fromdocname, target_docname)
        except Exception:
            base = f"{target_docname}.html"
        return f"{base}#{need_id}"

    def filter(self, filter_string: str) -> list[Any]:
        """Return needs matching a filter expression."""
        try:
            from sphinx_needs.config import NeedsSphinxConfig
            from sphinx_needs.data import SphinxNeedsData
            from sphinx_needs.filter_common import filter_needs_view

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
            f"<g>"
            f'<rect width="120" height="40" rx="4"'
            f' fill="#ddeeff" stroke="#336699"/>'
            f'<text x="60" y="16" text-anchor="middle"'
            f' font-size="10" fill="#666">{need_id}</text>'
            f'<text x="60" y="30" text-anchor="middle"'
            f' font-size="11">{title}</text>'
            f"</g>"
            f"</a>"
        )

    def get_context(self) -> dict[str, Any]:
        return {
            "needs": self._needs,
            "ref": self.ref,
            "filter": self.filter,
            "flow": self.flow,
        }


def render_jinja_svg(
    content: str, app: Any, fromdocname: str | None = None
) -> tuple[str, dict[str, Any]]:
    """Render a Jinja2 template string with needs-aware context.

    Pass ``fromdocname`` (the rendering page's docname) so that
    :py:meth:`SvgJinjaContext.ref` and :py:meth:`SvgJinjaContext.flow`
    emit URLs relative to that page. Without it, links fall back to the
    legacy ``{docname}.html#{id}`` form which doubles the path for
    same-page references.

    Returns the rendered SVG string and the Jinja context dict (for reuse
    by downstream processors such as the drawio content-attribute sync).
    """
    ctx = SvgJinjaContext(app, fromdocname=fromdocname)
    env = Environment()
    template = env.from_string(content)
    context = ctx.get_context()
    return template.render(**context), context
