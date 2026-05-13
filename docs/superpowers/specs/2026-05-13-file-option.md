# Design: `:file:` Option for needsvg Directive

**Date:** 2026-05-13
**Status:** Implemented

## Goal

Allow `needsvg` to load SVG/Jinja2 template content from an external file instead of requiring inline content in the directive body.

## Motivation

As SVG templates grow (especially in drilldown patterns with repeated structure), embedding them inline in RST becomes unwieldy. An external file option:

- Keeps RST documents readable
- Enables template reuse across multiple pages
- Allows IDEs to provide SVG/Jinja syntax highlighting on `.svg.j2` files
- Matches patterns from other Sphinx directives (`.. literalinclude::`, `.. image::`)

## Interface

```rst
.. needsvg::
   :file: _svgs/pipeline-overview.svg.j2
   :debug:
```

### Behaviour

| Scenario | Result |
|---|---|
| `:file:` only | File content used as template |
| Inline body only | Body used as template (existing behaviour) |
| Both `:file:` and body | `:file:` wins; warning logged |
| `:file:` path not found | Warning logged; red error SVG rendered |

### Path Resolution

The `:file:` path is resolved **relative to the document's source directory**, matching Sphinx conventions (`.. image::`, `.. literalinclude::`).

### Dependency Tracking

`env.note_dependency(str(file_path))` is called so Sphinx rebuilds the page when the template file changes. This is critical for incremental builds.

## Implementation

### Changes to `NeedsvgDirective.run()`

1. Add `"file": directives.unchanged` to `option_spec`
2. Before storing content, check for `:file:`:
   - Resolve path relative to `Path(env.doc2path(env.docname)).parent`
   - Read file content with `file_path.read_text(encoding="utf-8")`
   - Call `env.note_dependency()` for rebuild tracking
   - On `FileNotFoundError`, log warning and produce error SVG
3. If both `:file:` and body provided, log warning and prefer `:file:`
4. Store resolved content string in `env.needsvg_all_data` (same as before)

### No Changes Required

- `process_needsvg()` -- unchanged, it already receives content as a string
- `render_jinja_svg()` -- unchanged, it already processes any string
- `SvgJinjaContext` -- unchanged

## Verification

1. New test root `tests/roots/test-file/` with:
   - `template.svg.j2` -- valid Jinja SVG template
   - `index.rst` -- two `needsvg` blocks: one `:file:` (valid), one `:file:` (missing)
2. `test_needsvg_file_option` -- verifies rendered content from file
3. `test_needsvg_file_not_found` -- verifies error handling
4. Full suite: 21 tests passing
