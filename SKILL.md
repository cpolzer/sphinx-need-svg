# sphinx-need-svg v0.3.0

A Sphinx-Needs extension for rendering SVG diagrams with clickable links to
needs entities.  Write SVG markup with Jinja2 templating in your RST docs.

## When to Use This Skill

Trigger on:
- "needsvg", "need svg", "svg diagram"
- "visualise needs", "visualize needs"
- "sphinx-needs diagram", "needs flow"
- Working with `.rst` or `.md` files that contain `.. needsvg::` directives
- Creating architecture diagrams that reference sphinx-needs objects

## Installation

```bash
pip install sphinx-need-svg
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add sphinx-need-svg
```

Add to your `conf.py`:

```python
extensions = [
    "sphinx_needs",
    "sphinx_need_svg",
]
```

## Directive: `.. needsvg::`

Renders SVG markup with Jinja2 templating and sphinx-needs integration.
The directive body is an SVG template processed through Jinja2 at build time.

### Options


| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `:width:` | string | `100%` | SVG container width |
| `:height:` | string | `auto` | SVG container height |
| `:align:` | choice | `center` | Horizontal alignment: `left`, `center`, or `right` |
| `:debug:` | flag | off | Show raw RST/Jinja source as a code block above the rendered SVG |
| `:file:` | path | -- | Load SVG/Jinja2 template from an external file (relative to source doc). Works with `.drawio.svg` files -- drawio `content` attribute is synced at build time. |

**Note:** If both `:file:` and inline content are provided, `:file:` wins.

## Jinja Helpers

Available inside `.. needsvg::` content:

### `needs`

*Property.* Dict of all needs keyed by ID. Access fields like needs['REQ_001'].title.

### `ref(need_id)`

Return the URL anchor for a need.

### `filter(filter_string)`

Return needs matching a filter expression.

### `flow(need_id)`

Return a pre-styled SVG <g> element for a need.

### Usage Examples

```jinja
{# Access a need by ID #}
{{ needs['REQ_001'].title }}

{# Link to a need #}
<a href="{{ ref('REQ_001') }}">Click me</a>

{# Loop over filtered needs #}
{% for need in filter("type == 'req'") %}
  <text>{{ need.title }}</text>
{% endfor %}

{# Pre-styled card #}
{{ flow('REQ_001') }}
```

## Configuration

### needs_types

| Directive | Title | Prefix | Color |
|-----------|-------|--------|-------|
| `req` | Requirement | `REQ_` | `#BFD8D2` |
| `spec` | Specification | `SPEC_` | `#DCB5FF` |
| `impl` | Implementation | `IMPL_` | `#FEDCD2` |
| `test` | Test Case | `TC_` | `#B9F6CA` |
| `arch` | Architecture View | `ARCH_` | `#E3F2FD` |

The `arch` type wraps SVG layers for drill-down navigation (see Patterns).

### needs_links

| Link Type | Outgoing | Incoming |
|-----------|----------|----------|
| `implements` | implements | is implemented by |
| `tests` | tests | is tested by |
| `traces` | traces | is traced by |


## Patterns

### Architecture Drilldown with `arch` Wrappers

Wrap each SVG layer in an `.. arch::` need element.  Boxes in a parent SVG
link to the child `arch` ID via `ref()`.

```rst
.. arch:: Pipeline Overview
   :id: ARCH_PIPELINE

   .. needsvg::

      <svg width="600" height="100" xmlns="http://www.w3.org/2000/svg">

        <a href="{{ ref('ARCH_BUILD') }}">
          <rect .../>
          <text>{{ needs['STAGE_BUILD'].title }}</text>
        </a>

      </svg>

.. arch:: Build Stage Detail
   :id: ARCH_BUILD
   :implements: ARCH_PIPELINE

   .. needsvg::

      <svg width="500" height="120" xmlns="http://www.w3.org/2000/svg">

        <!-- Back-link -->
        <a href="{{ ref('ARCH_PIPELINE') }}">
          <text x="8" y="14">◀ Pipeline</text>
        </a>

        ...
      </svg>
```

**Key elements:**
- **Drill-down:** Box links to child `arch` via `ref('ARCH_CHILD')`
- **Back-link:** Child SVG links to parent via `ref('ARCH_PARENT')`
- **Breadcrumb:** Static SVG text showing hierarchy path
- **Sibling nav:** Links to peer `arch` elements at the same level
- **Traceability:** `:implements:` on `arch` elements creates traceable hierarchy

### Traceability Chain

Link needs across types and render as a flow:

```jinja
{% set chain = ["REQ_ENC", "SPEC_DBENC", "IMPL_TDE", "TC_ENC"] %}
{% for id in chain %}
  <a href="{{ ref(id) }}">
    <rect x="{{ loop.index0 * 170 }}" .../>
    <text>{{ needs[id].title }}</text>
  </a>
{% endfor %}
```

### Dynamic Dashboard

Render all needs of a type automatically:

```jinja
{% for need in filter("type == 'req'") %}
  <a href="{{ ref(need.id) }}">
    <rect x="5" y="{{ loop.index0 * 55 }}" .../>
    <text>{{ need.title }}</text>
  </a>
{% endfor %}
```

## Common Mistakes

1. **Missing SVG namespace** -- Always include `xmlns="http://www.w3.org/2000/svg"`
2. **`:file:` + inline content** -- If both given, `:file:` wins with a warning
3. **Missing `sphinx_needs` extension** -- Context helpers return empty data without it
4. **Unescaped characters in SVG** -- Use `&amp;`, `&lt;`, `&gt;` in `<text>`
5. **Relative `:file:` paths** -- Relative to the source document, not project root
6. **SVG `id` collisions** -- Use unique IDs for `<defs>` markers across blocks
7. **`flow()` in drawio SVGs** -- Do not use `flow()` or `filter()` inside drawio-exported SVGs; they return SVG markup that conflicts with drawio's `<foreignObject>` wrappers. Use only `ref()` and `needs[]` accessors.

## Drawio Integration

`.drawio.svg` files can be loaded via `:file:`. At build time:

1. Jinja expressions in visible SVG elements (`<text>`, `<a xlink:href>`) are rendered normally.
2. If the SVG has a drawio `content` attribute (embedded mxfile), Jinja expressions in cell `value` attributes are also rendered and the attribute is updated in the output.
3. The source file is never modified -- sync only affects build output.

**Safe Jinja in drawio shapes:**
- `{{ ref('NEED_ID') }}` in link targets
- `{{ needs['NEED_ID'].title }}` in shape labels

**Unsafe:** `{{ flow('...') }}`, `{{ filter(...) }}` -- these return SVG markup.
