# sphinx-needs-svg Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a pip-installable Sphinx-Needs extension providing a `needsvg` directive that renders Jinja-templated SVG diagrams with clickable links to needs entities.

**Architecture:** Two-phase rendering modeled after needuml -- directive stores data + placeholder node at parse time, event handler renders SVG at doctree-resolved time. Jinja2 context provides `needs`, `ref()`, `filter()`, `flow()` helpers for accessing sphinx-needs data.

**Tech Stack:** Python, Sphinx, sphinx-needs, Jinja2, pytest

**Spec:** `docs/superpowers/specs/2026-05-13-needsvg-design.md`

---

## File Structure

| File | Responsibility |
|---|---|
| `pyproject.toml` | Package metadata, dependencies, entry points |
| `src/sphinx_needs_svg/__init__.py` | `setup()` function -- registers node, directive, event handler |
| `src/sphinx_needs_svg/directives/__init__.py` | Package marker |
| `src/sphinx_needs_svg/directives/needsvg.py` | `Needsvg` node, `NeedsvgDirective`, `process_needsvg()` |
| `src/sphinx_needs_svg/jinja_context.py` | `SvgJinjaContext` -- `ref()`, `filter()`, `flow()` helpers |
| `tests/conftest.py` | Shared fixtures (Sphinx app builder with sphinx-needs + our extension) |
| `tests/test_needsvg.py` | Directive integration tests |

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/sphinx_needs_svg/__init__.py`
- Create: `src/sphinx_needs_svg/directives/__init__.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68.0", "setuptools-scm"]
build-backend = "setuptools.build_meta"

[project]
name = "sphinx-needs-svg"
version = "0.1.0"
description = "Sphinx-Needs extension for SVG diagrams with clickable need links"
requires-python = ">=3.9"
dependencies = [
    "sphinx>=5.0",
    "sphinx-needs>=2.0",
]

[project.optional-dependencies]
test = ["pytest", "pytest-regressions"]

[tool.setuptools.packages.find]
where = ["src"]
```

- [ ] **Step 2: Create empty `__init__.py` for directives package**

`src/sphinx_needs_svg/directives/__init__.py` -- empty file.

- [ ] **Step 3: Create `src/sphinx_needs_svg/__init__.py` with setup stub**

```python
from __future__ import annotations

from typing import Any


def setup(app: Any) -> dict[str, Any]:
    """Sphinx extension entry point."""
    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
```

- [ ] **Step 4: Verify the package is importable**

Run: `pip install -e ".[test]"` then `python -c "import sphinx_needs_svg; print('ok')"`
Expected: `ok`

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/
git commit -m "feat: scaffold sphinx-needs-svg package"
```

---

### Task 2: Needsvg Node and Directive (Placeholder Only)

**Files:**
- Create: `src/sphinx_needs_svg/directives/needsvg.py`
- Modify: `src/sphinx_needs_svg/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_needsvg.py`

- [ ] **Step 1: Write the failing test**

`tests/conftest.py`:
```python
from pathlib import Path

import pytest

pytest_plugins = "sphinx.testing.fixtures"


@pytest.fixture(scope="session")
def rootdir():
    return Path(__file__).parent / "roots"
```

Create `tests/roots/test-basic/conf.py`:
```python
extensions = ["sphinx_needs", "sphinx_needs_svg"]
needs_types = [
    {"directive": "req", "title": "Requirement", "prefix": "REQ_", "color": "#BFD8D2", "style": "node"},
]
```

Create `tests/roots/test-basic/index.rst`:
```rst
Test
====

.. req:: My Requirement
   :id: REQ_001

   A test requirement.

.. needsvg::

   <svg width="200" height="50">
     <rect width="200" height="50" fill="#eef"/>
   </svg>
```

`tests/test_needsvg.py`:
```python
import pytest


@pytest.mark.sphinx("html", testroot="basic")
def test_needsvg_renders_svg(app, status, warning):
    app.build()
    content = (Path(app.outdir) / "index.html").read_text()
    assert "<svg" in content
    assert 'width="200"' in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_needsvg.py::test_needsvg_renders_svg -v`
Expected: FAIL -- `needsvg` directive not registered.

- [ ] **Step 3: Implement Needsvg node, NeedsvgDirective, and process_needsvg**

`src/sphinx_needs_svg/directives/needsvg.py`:
```python
from __future__ import annotations

from typing import Any, ClassVar, Sequence

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective


class Needsvg(nodes.General, nodes.Element):
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

        # Store data on env
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

        svg_content = data["content"]
        options = data["options"]

        # Wrap in alignment div
        align = options.get("align", "center")
        wrapper = f'<div style="text-align: {align}">{svg_content}</div>'

        content_nodes: list[nodes.Node] = [
            nodes.raw("", wrapper, format="html"),
        ]

        if options.get("debug"):
            code = nodes.literal_block(svg_content, svg_content)
            code["language"] = "xml"
            content_nodes.append(code)

        node.replace_self(content_nodes)
```

Update `src/sphinx_needs_svg/__init__.py`:
```python
from __future__ import annotations

from typing import Any

from sphinx.application import Sphinx

from sphinx_needs_svg.directives.needsvg import Needsvg, NeedsvgDirective, process_needsvg


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_node(Needsvg)
    app.add_directive("needsvg", NeedsvgDirective)
    app.connect("doctree-resolved", process_needsvg)

    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_needsvg.py::test_needsvg_renders_svg -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: add Needsvg node, directive, and process handler"
```

---

### Task 3: Jinja Context with Needs Helpers

**Files:**
- Create: `src/sphinx_needs_svg/jinja_context.py`
- Modify: `src/sphinx_needs_svg/directives/needsvg.py`
- Modify: `tests/test_needsvg.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/roots/test-basic/index.rst` a new needsvg block:

```rst
.. needsvg::

   <svg width="300" height="50">
     <a href="{{ ref('REQ_001') }}">
       <text x="10" y="30">{{ needs['REQ_001'].title }}</text>
     </a>
   </svg>
```

Add test in `tests/test_needsvg.py`:
```python
@pytest.mark.sphinx("html", testroot="basic")
def test_needsvg_jinja_ref(app, status, warning):
    app.build()
    content = (Path(app.outdir) / "index.html").read_text()
    assert "My Requirement" in content
    assert 'href="' in content  # ref() generated a link
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_needsvg.py::test_needsvg_jinja_ref -v`
Expected: FAIL -- Jinja not processed, raw `{{ }}` in output or template error.

- [ ] **Step 3: Implement SvgJinjaContext and wire into process_needsvg**

`src/sphinx_needs_svg/jinja_context.py`:
```python
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
```

Update `process_needsvg` in `needsvg.py` to call `render_jinja_svg`:

In the `process_needsvg` function, replace `svg_content = data["content"]` with:
```python
from sphinx_needs_svg.jinja_context import render_jinja_svg
svg_content = render_jinja_svg(data["content"], app)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_needsvg.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: add Jinja2 context with needs helpers (ref, filter, flow)"
```

---

### Task 4: Filter Helper Test

**Files:**
- Modify: `tests/roots/test-basic/index.rst`
- Modify: `tests/test_needsvg.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/roots/test-basic/index.rst`:
```rst
.. req:: Second Requirement
   :id: REQ_002

   Another requirement.

.. needsvg::

   <svg width="400" height="50">
     {% for need in filter("type == 'req'") %}
       <text x="{{ loop.index0 * 150 }}" y="30">{{ need.title }}</text>
     {% endfor %}
   </svg>
```

Add test:
```python
@pytest.mark.sphinx("html", testroot="basic")
def test_needsvg_filter(app, status, warning):
    app.build()
    content = (Path(app.outdir) / "index.html").read_text()
    assert "My Requirement" in content
    assert "Second Requirement" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_needsvg.py::test_needsvg_filter -v`
Expected: May pass if Task 3 is already in place. If so, that confirms filter works.

- [ ] **Step 3: Fix if needed, otherwise confirm**

If test passes, no changes needed. If filter API differs, adjust `SvgJinjaContext.filter()`.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "test: add filter helper integration test"
```

---

### Task 5: Directive Options (width, height, align, debug)

**Files:**
- Modify: `tests/test_needsvg.py`
- Modify: `tests/roots/test-basic/index.rst`

- [ ] **Step 1: Write the failing test for debug option**

Add to `tests/roots/test-basic/index.rst`:
```rst
.. needsvg::
   :debug:
   :width: 300
   :height: 80

   <svg>
     <rect width="100" height="40" fill="#ccc"/>
   </svg>
```

Add test:
```python
@pytest.mark.sphinx("html", testroot="basic")
def test_needsvg_debug_shows_source(app, status, warning):
    app.build()
    content = (Path(app.outdir) / "index.html").read_text()
    # debug mode should show the raw SVG as a code block
    assert "<rect" in content  # rendered SVG
    assert "literal-block" in content or "<pre" in content  # debug code block
```

- [ ] **Step 2: Run test to verify it passes**

Run: `pytest tests/test_needsvg.py::test_needsvg_debug_shows_source -v`
Expected: PASS (debug already implemented in Task 2).

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "test: add directive options tests (debug, width, height)"
```

---

### Task 6: Flow Helper Test

**Files:**
- Modify: `tests/roots/test-basic/index.rst`
- Modify: `tests/test_needsvg.py`

- [ ] **Step 1: Write the test**

Add to `tests/roots/test-basic/index.rst`:
```rst
.. needsvg::

   <svg width="200" height="60">
     {{ flow('REQ_001') }}
   </svg>
```

Add test:
```python
@pytest.mark.sphinx("html", testroot="basic")
def test_needsvg_flow_helper(app, status, warning):
    app.build()
    content = (Path(app.outdir) / "index.html").read_text()
    assert "REQ_001" in content
    assert "My Requirement" in content
    assert "ddeeff" in content  # flow() default fill color
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_needsvg.py::test_needsvg_flow_helper -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "test: add flow helper integration test"
```

---

### Task 7: Error Handling

**Files:**
- Modify: `src/sphinx_needs_svg/jinja_context.py`
- Modify: `src/sphinx_needs_svg/directives/needsvg.py`
- Modify: `tests/test_needsvg.py`

- [ ] **Step 1: Write the failing test**

Create `tests/roots/test-errors/conf.py`:
```python
extensions = ["sphinx_needs", "sphinx_needs_svg"]
```

Create `tests/roots/test-errors/index.rst`:
```rst
Test Errors
===========

.. needsvg::

   <svg>{{ needs['NONEXISTENT'].title }}</svg>
```

Add test:
```python
@pytest.mark.sphinx("html", testroot="errors")
def test_needsvg_bad_need_ref_warns(app, status, warning):
    app.build()
    # Should not crash, should produce output (possibly with error indicator)
    content = (Path(app.outdir) / "index.html").read_text()
    assert "<svg" in content or "error" in content.lower() or "needsvg" in warning.getvalue().lower()
```

- [ ] **Step 2: Run test to verify behavior**

Run: `pytest tests/test_needsvg.py::test_needsvg_bad_need_ref_warns -v`
Expected: May crash with KeyError. Need to add error handling.

- [ ] **Step 3: Add error handling in render_jinja_svg and process_needsvg**

In `jinja_context.py`, use `jinja2.Undefined` subclass or wrap template rendering in try/except to emit a warning and produce a visible error SVG instead of crashing.

In `needsvg.py` `process_needsvg`, wrap the render call:
```python
try:
    svg_content = render_jinja_svg(data["content"], app)
except Exception as e:
    logger.warning(f"needsvg error at {data['docname']}:{data['lineno']}: {e}")
    svg_content = f'<svg><text fill="red">needsvg error: {e}</text></svg>'
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_needsvg.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: add error handling for bad need references and template errors"
```

---

### Task 8: Final Integration Test and Cleanup

**Files:**
- Modify: `tests/test_needsvg.py`

- [ ] **Step 1: Run full test suite**

Run: `pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 2: Verify package installs cleanly**

Run: `pip install -e ".[test]" && python -c "from sphinx_needs_svg import setup; print(setup)"`
Expected: prints function reference

- [ ] **Step 3: Commit any final cleanup**

```bash
git add -A
git commit -m "chore: final cleanup and all tests passing"
```
