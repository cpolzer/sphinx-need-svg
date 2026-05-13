from pathlib import Path

import pytest


@pytest.mark.sphinx("html", testroot="basic")
def test_needsvg_renders_svg(app, status, warning):
    app.build()
    content = (Path(app.outdir) / "index.html").read_text()
    assert "<svg" in content
    assert 'width="200"' in content
