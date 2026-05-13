# Design: Drilldown Navigation with `arch` Need Type

**Date:** 2026-05-13
**Status:** Implemented
**Relates to:** `docs/superpowers/specs/2026-05-13-needsvg-design.md`

## Problem

The original drilldown example used `ref()` to link SVG boxes to the **need
definition** of the next level (e.g. `ref('STAGE_BUILD')`).  This scrolls the
browser to the `.. req::` block, not to the SVG diagram that visualises that
stage's contents.  Users must then manually scroll further to find the detail
SVG.  There is no back-link, no breadcrumb, and no way to jump between sibling
layers.

## Goal

Let users **click a box in one SVG** and land precisely on the **next-layer SVG
diagram**, with clear navigation aids (back-link, breadcrumb, sibling links) to
traverse the hierarchy in both directions.

## Solution: `arch` Need Type as SVG Wrapper

Introduce a custom sphinx-needs type called `arch` ("Architecture View").  Each
SVG layer is wrapped in an `.. arch::` directive with an ID.  The `needsvg`
block is nested inside the `arch` element's content.

Because `arch` is a proper sphinx-needs element, it gets an HTML anchor
(`#ARCH_BUILD`), and `ref('ARCH_BUILD')` resolves to it.  This means SVG boxes
can link directly to the `arch` element that contains the next-layer SVG.

### Why not RST anchor labels?

RST labels (`.. _svg-build:`) work but live outside the sphinx-needs data
model.  They cannot participate in traceability, filtering, or needflow.  Using
`arch` elements means:

- The layer hierarchy is **traceable** via `:implements:` links
  (`ARCH_BUILD` implements `ARCH_PIPELINE`)
- Layers are **filterable** (`filter("type == 'arch'")"`)
- Layers show up in **needflow** and **needtable** views automatically
- `ref()` works uniformly -- no mixing of anchor syntaxes

### Navigation Aids (pure SVG, no JavaScript)

Each detail SVG includes three navigation elements rendered as SVG `<a>` +
`<text>`:

| Element | Position | Purpose |
|---|---|---|
| **Back-link** | Top-left | `ref('ARCH_PIPELINE')` -- returns to parent layer |
| **Breadcrumb** | Top-center | Shows path: `CI Pipeline > Build > Lint Job` |
| **Sibling links** | Bottom-center | Jump between peer layers (Build / Test / Deploy) |

Boxes that have a deeper layer show a small "drill down" hint (`▼ drill down`)
in the bottom-right corner.

## Data Model

```
ARCH_PIPELINE (top-level SVG)
├── ARCH_BUILD  (implements ARCH_PIPELINE)
│   └── ARCH_LINT  (implements ARCH_BUILD)
├── ARCH_TEST   (implements ARCH_PIPELINE)
└── ARCH_DEPLOY (implements ARCH_PIPELINE)
```

Each `arch` element contains:
- A title describing the view
- An `:implements:` link to its parent `arch`
- A `.. needsvg::` block with the SVG content

## Configuration

A single line added to `conf.py`:

```python
needs_types = [
    # ... existing types ...
    {"directive": "arch", "title": "Architecture View", "prefix": "ARCH_",
     "color": "#E3F2FD", "style": "node"},
]
```

No new directive options, no new Jinja helpers, no code changes required.  The
entire feature is a **documentation pattern** built on existing primitives.

## SVG Linking Pattern

### Drill-down link (parent -> child layer)

```jinja
{%- set stages = [
  {"id": "STAGE_BUILD", "arch": "ARCH_BUILD", ...},
] -%}
<a href="{{ ref(s.arch) }}">
  <rect .../>
  <text ...>{{ needs[s.id].title }}</text>
  <text ...>▼ drill down</text>
</a>
```

### Back-link (child -> parent layer)

```jinja
<a href="{{ ref('ARCH_PIPELINE') }}">
  <text x="8" y="14" font-size="11" fill="#d4836a">◀ CI Pipeline</text>
</a>
```

### Sibling navigation

```jinja
<a href="{{ ref('ARCH_BUILD') }}"><text ...>Build</text></a>
<a href="{{ ref('ARCH_TEST') }}"><text ...>Test</text></a>
<a href="{{ ref('ARCH_DEPLOY') }}"><text ...>Deploy</text></a>
```

The current sibling is rendered **bold**, others in their stage color.

## Tradeoffs

| Decision | Rationale |
|---|---|
| `arch` as a need type, not a directive option | Keeps it simple; no code changes; leverages sphinx-needs traceability |
| Navigation in SVG text, not HTML | Self-contained; works in any SVG viewer; no external CSS/JS dependency |
| No JavaScript show/hide layers | Static output is simpler, more portable, works in PDF |
| Manual sibling links | Could be automated via `filter()` in future, but explicit is clearer for the example |

## Future Extensions

- **Jinja macro** for back-link + breadcrumb + sibling bar (reduces boilerplate)
- **`parent()` / `children()` helpers** that traverse `:implements:` links
- **Collapsible layers** via `<details>` wrapping (HTML-only, still no JS)
