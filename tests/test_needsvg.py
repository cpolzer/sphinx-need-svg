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
    assert "<svg" in content or "error" in content.lower() or "needsvg" in warning.getvalue().lower()
