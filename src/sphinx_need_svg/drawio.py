"""Decode and encode draw.io mxfile content embedded in SVG."""

from __future__ import annotations

import base64
import logging
import re
import zlib
from xml.etree import ElementTree as ET

from jinja2 import Environment

logger = logging.getLogger(__name__)

# Matches the content="..." attribute on the root <svg> element
_CONTENT_ATTR_RE = re.compile(
    r'(<svg\b[^>]*?\bcontent=")([^"]*?)(")',
    re.DOTALL,
)

# Matches the diagram body inside <mxfile><diagram ...>BODY</diagram></mxfile>
_DIAGRAM_BODY_RE = re.compile(
    r"(<diagram\b[^>]*?>)(.*?)(</diagram>)",
    re.DOTALL,
)


def _decode_diagram(encoded: str) -> str | None:
    """Decode a drawio diagram body (base64 + raw-deflate) to XML."""
    try:
        raw = base64.b64decode(encoded)
        # Wrap raw deflate stream with zlib header/trailer for decompression
        xml_bytes = zlib.decompress(raw, -zlib.MAX_WBITS)
        return xml_bytes.decode("utf-8")
    except Exception:
        logger.debug("needsvg: could not decode drawio diagram body")
        return None


def _encode_diagram(xml: str) -> str:
    """Encode an mxGraphModel XML string back to drawio format."""
    compress_obj = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
    compressed = compress_obj.compress(xml.encode("utf-8"))
    compressed += compress_obj.flush()
    return base64.b64encode(compressed).decode("ascii")


def _render_mxgraph_labels(mxgraph_xml: str, jinja_ctx: dict[str, object]) -> str:
    """Render Jinja2 expressions in mxCell value attributes."""
    env = Environment()
    try:
        root = ET.fromstring(mxgraph_xml)
    except ET.ParseError:
        logger.debug("needsvg: could not parse mxGraphModel XML")
        return mxgraph_xml

    changed = False
    for cell in root.iter("mxCell"):
        value = cell.get("value")
        if value and ("{{" in value or "{%" in value):
            template = env.from_string(value)
            cell.set("value", template.render(**jinja_ctx))
            changed = True

    if not changed:
        return mxgraph_xml

    return ET.tostring(root, encoding="unicode", xml_declaration=False)


def sync_drawio_content(
    rendered_svg: str,
    jinja_ctx: dict[str, object],
) -> str:
    """If *rendered_svg* contains a drawio ``content`` attribute, render
    Jinja expressions inside the mxfile cell labels and update the attribute.

    Returns the (possibly modified) SVG string.
    """
    content_match = _CONTENT_ATTR_RE.search(rendered_svg)
    if content_match is None:
        return rendered_svg

    # The content attribute value is XML-escaped; unescape it
    raw_content = content_match.group(2)
    try:
        # Use a dummy element to XML-unescape the attribute value
        dummy = ET.fromstring(f'<x v="{raw_content}"/>')
        mxfile_xml = dummy.get("v", "")
    except ET.ParseError:
        return rendered_svg

    if "<diagram" not in mxfile_xml:
        return rendered_svg

    diagram_match = _DIAGRAM_BODY_RE.search(mxfile_xml)
    if diagram_match is None:
        return rendered_svg

    diagram_body = diagram_match.group(2).strip()
    mxgraph_xml = _decode_diagram(diagram_body)
    if mxgraph_xml is None:
        return rendered_svg

    # Render Jinja expressions in cell labels
    rendered_mxgraph = _render_mxgraph_labels(mxgraph_xml, jinja_ctx)

    # Re-encode and reassemble
    new_body = _encode_diagram(rendered_mxgraph)
    new_mxfile = diagram_match.group(1) + new_body + diagram_match.group(3)
    # Reconstruct the full mxfile string (replace only the diagram body)
    new_mxfile_full = (
        mxfile_xml[: diagram_match.start()]
        + new_mxfile
        + mxfile_xml[diagram_match.end() :]
    )

    # XML-escape for the attribute value
    escaped = (
        new_mxfile_full.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    new_svg = (
        rendered_svg[: content_match.start(2)]
        + escaped
        + rendered_svg[content_match.end(2) :]
    )
    return new_svg
