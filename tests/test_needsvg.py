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
