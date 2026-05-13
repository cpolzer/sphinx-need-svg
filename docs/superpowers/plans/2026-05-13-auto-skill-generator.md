# Auto-Generated Agent Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python script that reads source code (AST) and RST docs (regex) to generate a SKILL.md file, with CI auto-committing changes on main.

**Architecture:** A standalone `scripts/generate_skill.py` extracts directive options, Jinja helpers, version, need types, and examples from the codebase, renders them through a Jinja2 template (`scripts/skill_template.md.j2`), and writes `SKILL.md`. A CI job regenerates and auto-commits if changed.

**Tech Stack:** Python (ast, re, pathlib), Jinja2, GitHub Actions

**Spec:** `docs/superpowers/specs/2026-05-13-auto-skill-generator-design.md`

---

## File Structure

| File | Responsibility |
|---|---|
| `scripts/generate_skill.py` | Generator script: extract data from code + docs, render template, write output |
| `scripts/skill_template.md.j2` | Jinja2 template defining the SKILL.md structure and static prose |
| `SKILL.md` | Generated output at repo root |
| `.github/workflows/ci.yml` | Add `update-skill` job for auto-commit on main |

---

### Task 1: Create the Jinja2 Skill Template

**Files:**
- Create: `scripts/skill_template.md.j2`

- [ ] **Step 1: Create the `scripts/` directory**

Run: `mkdir -p scripts`

- [ ] **Step 2: Write the template file**

The template defines the full SKILL.md structure with static and dynamic sections:

```jinja
# sphinx-need-svg v{{ version }}

A Sphinx-Needs extension for rendering SVG diagrams with clickable links to
needs entities.  Write SVG markup with Jinja2 templating in your RST docs.

## When to Use This Skill

Use when working with a Sphinx project that uses `sphinx-need-svg` and you need to:
- Create or edit `.. needsvg::` blocks
- Link SVG elements to sphinx-needs entities
- Build drill-down navigation between SVG layers
- Configure need types for SVG diagram wrappers

Trigger on: "needsvg", "SVG diagram", "drill down", "architecture view",
"sphinx-need-svg", or any reference to SVG + sphinx-needs integration.

## Installation

{{ installation }}

## Directive: `.. needsvg::`

Renders inline SVG with Jinja2 templating.  Content is processed through Jinja2
at build time with access to all sphinx-needs data.

### Options

| Option | Type | Default | Description |
|---|---|---|---|
{% for opt in directive_options -%}
| `:{{ opt.name }}:` | {{ opt.type }} | {{ opt.default }} | {{ opt.description }} |
{% endfor %}

### Basic Example

```rst
.. needsvg::

   <svg width="400" height="60" xmlns="http://www.w3.org/2000/svg">
     {%- raw %}{%{% endraw %} for need in filter("type == 'req'") {%- raw %}%}{% endraw %}
       <a href="{%- raw %}{{ ref(need.id) }}{% endraw %}">
         <rect x="{%- raw %}{{ loop.index0 * 130 }}{% endraw %}" y="5" width="120" height="40"
               rx="4" fill="#ddeeff" stroke="#336699"/>
         <text x="{%- raw %}{{ loop.index0 * 130 + 60 }}{% endraw %}" y="30"
               text-anchor="middle">{%- raw %}{{ need.title }}{% endraw %}</text>
       </a>
     {%- raw %}{%{% endraw %} endfor {%- raw %}%}{% endraw %}
   </svg>
```

## Jinja Helpers

Available inside `.. needsvg::` content:

{% for helper in jinja_helpers -%}
### `{{ helper.signature }}`

{{ helper.docstring }}

{% endfor %}

## Configuration

### Need Types

The project defines these need types in `conf.py`:

| Directive | Title | Prefix | Purpose |
|---|---|---|---|
{% for nt in needs_types -%}
| `{{ nt.directive }}` | {{ nt.title }} | `{{ nt.prefix }}` | {{ nt.purpose }} |
{% endfor %}

The `arch` type is used to wrap SVG layers for drill-down navigation.

### Need Links

| Link type | Outgoing | Incoming |
|---|---|---|
{% for link_name, link in needs_links.items() -%}
| `{{ link_name }}` | {{ link.outgoing }} | {{ link.incoming }} |
{% endfor %}

## Patterns

### Drill-Down with `arch` Wrappers

Wrap each SVG layer in an `.. arch::` need element with an ID.  Boxes in a
parent SVG link to the child `arch` element via `ref('ARCH_CHILD')`.

**Key elements:**
- **Drill-down link:** `<a href="{%- raw %}{{ ref('ARCH_BUILD') }}{% endraw %}">`
- **Back-link:** `<a href="{%- raw %}{{ ref('ARCH_PIPELINE') }}{% endraw %}">◀ CI Pipeline</a>`
- **Breadcrumb:** Static SVG text showing hierarchy path
- **Sibling nav:** Links to peer `arch` elements at the same level

Each `arch` element uses `:implements:` to link to its parent, creating a
traceable hierarchy that works with needflow and needtable.

### Traceability Chain

Link needs across types (req → spec → impl → test) and render as a horizontal
flow using `ref()` for clickable boxes.

### Dynamic Dashboard

Use `filter()` to render all needs of a given type automatically:

```jinja
{%- raw %}{%{% endraw %} for need in filter("type == 'req'") {%- raw %}%}{% endraw %}
```

## Common Mistakes

- **Missing `xmlns`:** Always include `xmlns="http://www.w3.org/2000/svg"` on the `<svg>` element
- **Using `ref()` for non-existent needs:** Returns `#UNKNOWN-ID` -- check IDs exist
- **Forgetting `:implements:`** on `arch` elements: breaks the traceability chain
- **SVG `id` collisions:** When multiple `needsvg` blocks use `<defs>` with markers, use unique IDs per block (e.g. `arr1`, `arr2`)
- **Inline content + `:file:` together:** If both are given, `:file:` wins and a warning is emitted
```

- [ ] **Step 3: Commit**

```bash
git add scripts/skill_template.md.j2
git commit -m "feat: add Jinja2 template for SKILL.md generation"
```

---

### Task 2: Create the Generator Script -- Code Extraction

**Files:**
- Create: `scripts/generate_skill.py`

- [ ] **Step 1: Write the script skeleton with AST extraction functions**

```python
#!/usr/bin/env python3
"""Generate SKILL.md from source code and documentation."""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "sphinx_need_svg"
DOCS = ROOT / "docs"


def extract_version() -> str:
    """Extract version from __init__.py."""
    source = (SRC / "__init__.py").read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "version":
                    if isinstance(node.value, ast.Constant):
                        return str(node.value.value)
    # Fallback: parse from return dict
    match = re.search(r'"version":\s*"([^"]+)"', source)
    return match.group(1) if match else "unknown"


def extract_directive_options() -> list[dict[str, str]]:
    """Extract option_spec from NeedsvgDirective via AST."""
    source = (SRC / "directives" / "needsvg.py").read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "NeedsvgDirective":
            for item in node.body:
                if (isinstance(item, ast.AnnAssign)
                        and isinstance(item.target, ast.Name)
                        and item.target.id == "option_spec"):
                    return _parse_option_spec(item.value)
                if (isinstance(item, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == "option_spec"
                                for t in item.targets)):
                    return _parse_option_spec(item.value)
    return []


def _parse_option_spec(node: ast.expr) -> list[dict[str, str]]:
    """Parse an option_spec dict AST node into a list of option dicts."""
    options = []
    if not isinstance(node, ast.Dict):
        return options

    # Map known directive type functions to human-readable types
    type_map = {
        "unchanged": "string",
        "flag": "flag",
        "unchanged_required": "string (required)",
        "nonnegative_int": "int",
        "positive_int": "int",
    }

    # Default values (hardcoded knowledge from directive)
    defaults = {
        "width": '"100%"',
        "height": '"auto"',
        "align": '"center"',
        "debug": "off",
        "file": "none",
    }

    # Descriptions (from reference.rst, but fallback here)
    descriptions = {
        "width": "SVG container width",
        "height": "SVG container height",
        "align": "Horizontal alignment (left/center/right)",
        "debug": "Show raw Jinja/SVG source above rendered output",
        "file": "Load SVG content from external file instead of inline",
    }

    for key_node, val_node in zip(node.keys, node.values):
        if not isinstance(key_node, ast.Constant):
            continue
        name = str(key_node.value)

        # Determine type from the value (function reference)
        opt_type = "string"
        if isinstance(val_node, ast.Attribute):
            opt_type = type_map.get(val_node.attr, val_node.attr)
        elif isinstance(val_node, ast.Name):
            opt_type = type_map.get(val_node.id, val_node.id)
        elif isinstance(val_node, ast.Lambda):
            opt_type = "choice"

        options.append({
            "name": name,
            "type": opt_type,
            "default": defaults.get(name, "none"),
            "description": descriptions.get(name, ""),
        })
    return options


def extract_jinja_helpers() -> list[dict[str, str]]:
    """Extract public methods from SvgJinjaContext."""
    source = (SRC / "jinja_context.py").read_text()
    tree = ast.parse(source)
    helpers = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "SvgJinjaContext":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                    # Skip get_context -- it's internal plumbing
                    if item.name == "get_context":
                        continue
                    sig = _format_signature(item)
                    docstring = ast.get_docstring(item) or ""
                    helpers.append({"signature": sig, "docstring": docstring})
            # Also add the 'needs' property
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "needs":
                    for decorator in item.decorator_list:
                        if isinstance(decorator, ast.Name) and decorator.id == "property":
                            helpers.insert(0, {
                                "signature": "needs",
                                "docstring": "Dict of all needs keyed by ID. Access with `needs['REQ_001'].title`.",
                            })
    return helpers


def _format_signature(func: ast.FunctionDef) -> str:
    """Format a function signature from AST, excluding self."""
    args = []
    for arg in func.args.args:
        if arg.arg == "self":
            continue
        annotation = ""
        if arg.annotation and isinstance(arg.annotation, ast.Name):
            annotation = f": {arg.annotation.id}"
        elif arg.annotation and isinstance(arg.annotation, ast.Constant):
            annotation = f": {arg.annotation.value}"
        args.append(f"{arg.arg}{annotation}")
    return f"{func.name}({', '.join(args)})"
```

- [ ] **Step 2: Verify extraction works**

Run: `uv run python -c "import sys; sys.path.insert(0, 'scripts'); from generate_skill import extract_version, extract_directive_options, extract_jinja_helpers; print(extract_version()); print(extract_directive_options()); print(extract_jinja_helpers())"`

Expected: Version string, list of option dicts, list of helper dicts.

- [ ] **Step 3: Commit**

```bash
git add scripts/generate_skill.py
git commit -m "feat: add code extraction functions for skill generator"
```

---

### Task 3: Add Docs Extraction to Generator Script

**Files:**
- Modify: `scripts/generate_skill.py`

- [ ] **Step 1: Add docs extraction functions**

Append to `scripts/generate_skill.py`:

```python
def extract_needs_types() -> list[dict[str, str]]:
    """Extract needs_types from docs/conf.py."""
    source = (DOCS / "conf.py").read_text()
    # Find the needs_types list
    match = re.search(r"needs_types\s*=\s*\[(.+?)\]", source, re.DOTALL)
    if not match:
        return []

    types = []
    purpose_map = {
        "req": "Requirements definition",
        "spec": "Specification details",
        "impl": "Implementation tracking",
        "test": "Test case definition",
        "arch": "Architecture View -- wraps SVG layers for drill-down navigation",
    }
    for m in re.finditer(
        r'\{\s*"directive":\s*"(\w+)".*?"title":\s*"([^"]+)".*?"prefix":\s*"([^"]+)"',
        match.group(1),
        re.DOTALL,
    ):
        directive, title, prefix = m.group(1), m.group(2), m.group(3)
        types.append({
            "directive": directive,
            "title": title,
            "prefix": prefix,
            "purpose": purpose_map.get(directive, title),
        })
    return types


def extract_needs_links() -> dict[str, dict[str, str]]:
    """Extract needs_links from docs/conf.py."""
    source = (DOCS / "conf.py").read_text()
    match = re.search(r"needs_links\s*=\s*\{(.+?)\}", source, re.DOTALL)
    if not match:
        return {}

    links = {}
    for m in re.finditer(
        r'"(\w+)":\s*\{\s*"incoming":\s*"([^"]+)".*?"outgoing":\s*"([^"]+)"\s*\}',
        match.group(1),
        re.DOTALL,
    ):
        links[m.group(1)] = {"incoming": m.group(2), "outgoing": m.group(3)}
    return links


def extract_installation() -> str:
    """Extract installation section from quickstart.rst."""
    source = (DOCS / "quickstart.rst").read_text()
    # Find the Installation section content
    match = re.search(
        r"Installation\n[-=]+\n\n(.+?)(?=\n[A-Z][\w ]+\n[-=]+|\Z)",
        source,
        re.DOTALL,
    )
    if match:
        return match.group(1).strip()
    return "```bash\npip install sphinx-need-svg\n```"
```

- [ ] **Step 2: Verify docs extraction**

Run: `uv run python -c "import sys; sys.path.insert(0, 'scripts'); from generate_skill import extract_needs_types, extract_needs_links, extract_installation; print(extract_needs_types()); print(extract_needs_links()); print(extract_installation()[:100])"`

Expected: List of need type dicts, dict of links, installation text.

- [ ] **Step 3: Commit**

```bash
git add scripts/generate_skill.py
git commit -m "feat: add docs extraction for needs_types, links, installation"
```

---

### Task 4: Add Main Function and Template Rendering

**Files:**
- Modify: `scripts/generate_skill.py`

- [ ] **Step 1: Add the main function**

Append to `scripts/generate_skill.py`:

```python
import argparse

from jinja2 import Environment, FileSystemLoader


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate SKILL.md from source code and documentation."
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=ROOT / "SKILL.md",
        help="Output file (default: SKILL.md at repo root)",
    )
    args = parser.parse_args()

    # Extract all data
    data = {
        "version": extract_version(),
        "directive_options": extract_directive_options(),
        "jinja_helpers": extract_jinja_helpers(),
        "needs_types": extract_needs_types(),
        "needs_links": extract_needs_links(),
        "installation": extract_installation(),
    }

    # Render template
    template_dir = Path(__file__).parent
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        keep_trailing_newline=True,
    )
    template = env.get_template("skill_template.md.j2")
    output = template.render(**data)

    # Write output
    args.output.write_text(output)
    print(f"Generated {args.output}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the generator end to end**

Run: `uv run python scripts/generate_skill.py`
Expected: Prints `Generated /path/to/SKILL.md`, file exists with rendered content.

- [ ] **Step 3: Review the generated SKILL.md**

Run: `head -60 SKILL.md`
Expected: Populated header, version, directive options table, helpers section.

- [ ] **Step 4: Commit**

```bash
git add scripts/generate_skill.py SKILL.md
git commit -m "feat: complete skill generator with template rendering"
```

---

### Task 5: Add CI Job for Auto-Commit

**Files:**
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Add `update-skill` job after `docs-build`**

Add the following job to `.github/workflows/ci.yml`, after the `docs-build` job:

```yaml
  update-skill:
    name: Update SKILL.md
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    needs: [lint, test, docs-build]
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Regenerate SKILL.md
        run: uv run python scripts/generate_skill.py

      - name: Commit if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add SKILL.md
          git diff --cached --quiet || git commit -m "chore: regenerate SKILL.md [skip ci]"
          git push
```

- [ ] **Step 2: Ensure `update-skill` runs in parallel with `bump` (both depend on docs-build, not on each other)**

Verify that `update-skill` has `needs: [lint, test, docs-build]` and `bump` also has `needs: [lint, test, docs-build]`. They should run independently.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add update-skill job to auto-commit SKILL.md on main"
```

---

### Task 6: Test End-to-End Locally

- [ ] **Step 1: Clean regenerate**

Run: `rm SKILL.md && uv run python scripts/generate_skill.py`
Expected: SKILL.md is recreated with current content.

- [ ] **Step 2: Verify content has dynamic data**

Check that SKILL.md contains:
- Current version from `__init__.py`
- All directive options (`width`, `height`, `align`, `debug`, `file`)
- All Jinja helpers (`needs`, `ref`, `filter`, `flow`)
- All need types including `arch`
- All need links (`implements`, `tests`, `traces`)

Run: `grep -c "arch" SKILL.md` -- should be > 0
Run: `grep -c "ref(" SKILL.md` -- should be > 0
Run: `grep -c "filter(" SKILL.md` -- should be > 0

- [ ] **Step 3: Verify idempotency**

Run: `uv run python scripts/generate_skill.py && uv run python scripts/generate_skill.py && git diff SKILL.md`
Expected: No diff -- running twice produces identical output.

- [ ] **Step 4: Final commit with generated SKILL.md**

```bash
git add SKILL.md scripts/
git commit -m "feat: auto-generated SKILL.md for agentic AI consumption"
```
