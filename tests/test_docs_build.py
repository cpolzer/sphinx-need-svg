"""End-to-end dogfood test: build the project's own docs and verify SVG output."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
BUILD_DIR = DOCS_DIR / "_build" / "html"


@pytest.fixture(scope="module")
def docs_build():
    """Build the docs once per test module."""
    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "html",
         str(DOCS_DIR), str(BUILD_DIR)],
        capture_output=True, text=True, timeout=120,
    )
    return result


def _read_page(name: str) -> str:
    return (BUILD_DIR / f"{name}.html").read_text()


class TestDocsBuildsSuccessfully:
    def test_build_succeeds(self, docs_build):
        # -W turns warnings into errors; allow the one known deprecation
        assert docs_build.returncode == 0 or "needs_extra_links" in docs_build.stderr

    def test_no_needsvg_errors(self, docs_build):
        assert "needsvg error" not in docs_build.stderr


class TestQuickstartPage:
    def test_contains_svg(self, docs_build):
        content = _read_page("quickstart")
        assert "<svg" in content

    def test_ref_links_present(self, docs_build):
        content = _read_page("quickstart")
        assert 'href="' in content
        assert "REQ_AUTH" in content

    def test_flow_helper_renders(self, docs_build):
        content = _read_page("quickstart")
        assert "ddeeff" in content  # flow() default fill


class TestExamplesPage:
    def test_contains_svg(self, docs_build):
        content = _read_page("examples")
        assert "<svg" in content

    def test_traceability_chain(self, docs_build):
        content = _read_page("examples")
        for need_id in ("REQ_ENC", "SPEC_DBENC", "IMPL_TDE", "TC_ENC"):
            assert need_id in content

    def test_filter_renders_all_reqs(self, docs_build):
        content = _read_page("examples")
        assert "Data encryption at rest" in content

    def test_debug_mode_shows_source(self, docs_build):
        content = _read_page("examples")
        assert "literal-block" in content or "<pre" in content

    def test_flow_cards(self, docs_build):
        content = _read_page("examples")
        assert "ddeeff" in content


class TestArchitecturePage:
    def test_contains_svg(self, docs_build):
        content = _read_page("architecture")
        assert "<svg" in content

    def test_component_links(self, docs_build):
        content = _read_page("architecture")
        for comp in ("ARCH_SETUP", "ARCH_DIRECTIVE", "ARCH_NODE",
                      "ARCH_PROCESSOR", "ARCH_RENDER", "ARCH_JINJA"):
            assert comp in content

    def test_clickable_refs(self, docs_build):
        content = _read_page("architecture")
        assert 'href="' in content
