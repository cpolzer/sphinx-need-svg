# Design: sphinx-needs-svg (needsvg directive)

**Date:** 2026-05-13
**Status:** Approved

## Goal

A Sphinx-Needs extension that provides a `needsvg` directive for rendering SVG diagrams with clickable links to sphinx-needs entities. Modeled after needuml's architecture.

## Content Model

Users write SVG markup in the directive body with Jinja2 templating for dynamic access to sphinx-needs data. Jinja helpers (`ref`, `needs`, `filter`, `flow`) resolve need references at build time.

### Example

```rst
.. needsvg::
   :width: 400
   :height: 100

   <svg>
     {% for need in filter("type == 'req'") %}
       <a href="{{ ref(need.id) }}">
         <rect x="{{ loop.index0 * 120 }}" y="10" width="100" height="40" fill="#eef" stroke="#333"/>
         <text x="{{ loop.index0 * 120 + 50 }}" y="35" text-anchor="middle">{{ need.title }}</text>
       </a>
     {% endfor %}
   </svg>
```

## Architecture

### Two-Phase Rendering (same as needuml)

**Phase 1 -- Directive parsing** (`NeedsvgDirective.run()`):
- Parses options: `width`, `height`, `align`, `debug`, `config`, `extra`
- Stores content + options in `env` keyed by `needsvg-{docname}-{serial}`
- Returns `[target_node, Needsvg("")]` placeholder

**Phase 2 -- Rendering** (`process_needsvg()`, connected to `doctree-resolved`):
- For each `Needsvg` node, retrieves stored data
- Renders directive body through Jinja2 with needs-aware context
- Wraps result in proper `<svg>` container if not already present
- Emits `nodes.raw("", svg_html, format="html")` for inline SVG
- Optionally shows raw source in debug mode

### Package Structure

```
sphinx-needs-svg/
├── pyproject.toml
├── src/
│   └── sphinx_needs_svg/
│       ├── __init__.py          # setup() entry point
│       ├── directives/
│       │   └── needsvg.py       # Needsvg node, NeedsvgDirective, process_needsvg
│       └── jinja_context.py     # SVG-specific Jinja helpers
└── tests/
    ├── conftest.py
    └── test_needsvg.py
```

### Jinja Context

| Helper | Returns | Example |
|---|---|---|
| `needs` | Dict of all needs by ID | `{{ needs['REQ_001'].title }}` |
| `ref(id)` | URL anchor for a need | `<a href="{{ ref('REQ_001') }}">` |
| `filter(expr)` | List of matching needs | `{% for n in filter("type=='req'") %}` |
| `flow(id)` | Pre-styled SVG `<g>` for a need | `{{ flow('REQ_001') }}` |

### Directive Options

| Option | Type | Default | Purpose |
|---|---|---|---|
| `width` | str | `"100%"` | SVG width |
| `height` | str | `"auto"` | SVG height |
| `align` | choice | `"center"` | left/center/right |
| `debug` | flag | off | Show raw SVG source below |
| `config` | str | none | Named config from `conf.py` |
| `extra` | str | none | `key:value` pairs for Jinja context |

### Registration

```python
def setup(app):
    app.add_node(Needsvg)
    app.add_directive("needsvg", NeedsvgDirective)
    app.connect("doctree-resolved", process_needsvg)
    return {"version": "0.1.0", "parallel_read_safe": True}
```

### Dependencies

- `sphinx>=5.0`
- `sphinx-needs>=2.0` (uses `SphinxNeedsData`, filter APIs)
- No other runtime dependencies (SVG as strings, Jinja2 via Sphinx)

## Output Strategy

Inline SVG via `nodes.raw("", svg_string, format="html")`. This is preferred over file-based `nodes.image` because inline SVG supports clickable `<a>` links natively, which is the primary feature.

## What This Is Not

- Not a diagramming DSL -- users write SVG directly
- Not a PlantUML replacement -- no external rendering tools
- No dependency on `sphinxcontrib.plantuml`
