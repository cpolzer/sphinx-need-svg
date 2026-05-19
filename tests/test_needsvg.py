from pathlib import Path

import pytest


@pytest.mark.sphinx("html", testroot="basic")
def test_needsvg_renders_svg(app, status, warning):
    app.build()
    content = (Path(app.outdir) / "index.html").read_text()
    assert "<svg" in content
    assert 'width="200"' in content


@pytest.mark.sphinx("html", testroot="basic")
def test_needsvg_jinja_ref(app, status, warning):
    app.build()
    content = (Path(app.outdir) / "index.html").read_text()
    assert "My Requirement" in content
    assert 'href="' in content  # ref() generated a link


@pytest.mark.sphinx("html", testroot="basic")
def test_needsvg_filter(app, status, warning):
    app.build()
    content = (Path(app.outdir) / "index.html").read_text()
    assert "My Requirement" in content
    assert "Second Requirement" in content


@pytest.mark.sphinx("html", testroot="basic")
def test_needsvg_debug_shows_source(app, status, warning):
    app.build()
    content = (Path(app.outdir) / "index.html").read_text()
    assert "<rect" in content
    assert "literal-block" in content or "<pre" in content


@pytest.mark.sphinx("html", testroot="basic")
def test_needsvg_flow_helper(app, status, warning):
    app.build()
    content = (Path(app.outdir) / "index.html").read_text()
    assert "REQ_001" in content
    assert "My Requirement" in content
    assert "ddeeff" in content


@pytest.mark.sphinx("html", testroot="errors")
def test_needsvg_bad_need_ref_warns(app, status, warning):
    app.build()
    content = (Path(app.outdir) / "index.html").read_text()
    # Should not crash the build. Should produce some output.
    assert (
        "<svg" in content
        or "error" in content.lower()
        or "needsvg" in warning.getvalue().lower()
    )


@pytest.mark.sphinx("html", testroot="file")
def test_needsvg_file_option(app, status, warning):
    app.build()
    content = (Path(app.outdir) / "index.html").read_text()
    assert "File-loaded Requirement" in content
    assert 'href="' in content
    assert "ddeeff" in content


@pytest.mark.sphinx("html", testroot="file")
def test_needsvg_file_not_found(app, status, warning):
    app.build()
    content = (Path(app.outdir) / "index.html").read_text()
    assert "file not found" in content.lower() or "nonexistent" in content


@pytest.mark.sphinx("html", testroot="drawio")
def test_needsvg_drawio_renders_visible_svg(app, status, warning):
    app.build()
    content = (Path(app.outdir) / "index.html").read_text()
    assert "Drawio Requirement" in content
    assert 'href="' in content


@pytest.mark.sphinx("html", testroot="drawio")
def test_needsvg_drawio_syncs_content_attr(app, status, warning):
    app.build()
    content = (Path(app.outdir) / "index.html").read_text()
    # The content attribute should contain the rendered title, not Jinja
    # We need to decode it to verify
    import re
    from xml.etree import ElementTree as ET

    from sphinx_need_svg.drawio import _DIAGRAM_BODY_RE, _decode_diagram

    # Extract the content attribute containing mxfile from the output HTML
    m = re.search(r'content="([^"]*mxfile[^"]*)"', content)
    assert m is not None, "content attribute with mxfile not found in output"
    raw = m.group(1)
    # XML-unescape
    dummy = ET.fromstring(f'<x v="{raw}"/>')
    mxfile_xml = dummy.get("v", "")
    dm = _DIAGRAM_BODY_RE.search(mxfile_xml)
    assert dm is not None, "diagram body not found in content attribute"
    mxgraph_xml = _decode_diagram(dm.group(2).strip())
    assert mxgraph_xml is not None, "could not decode diagram"
    # The rendered mxGraphModel should contain the resolved title
    assert "Drawio Requirement" in mxgraph_xml
    # And should NOT contain raw Jinja expressions
    assert "{{" not in mxgraph_xml
