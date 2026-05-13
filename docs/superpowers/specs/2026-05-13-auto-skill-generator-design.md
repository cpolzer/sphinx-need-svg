# Design: Auto-Generated Agent Skill for sphinx-need-svg

**Date:** 2026-05-13
**Status:** Approved

## Problem

Agentic AI tools (Claude Code, OpenCode, Cursor) work best when they have a
structured skill file describing the API, patterns, and configuration of a
library.  Manually maintaining such a file is error-prone -- directive options
get added, Jinja helpers change signatures, examples evolve, and the skill goes
stale.

## Goal

A Python script that reads the source code and documentation of sphinx-need-svg
and produces a `SKILL.md` at the repo root.  CI enforces that the committed
SKILL.md matches what the script would generate, so it can never drift from the
actual API.

## Solution: AST + RST Hybrid Generator

### Components

| File | Purpose |
|---|---|
| `scripts/generate_skill.py` | Generator script (stdlib + jinja2) |
| `scripts/skill_template.md.j2` | Jinja2 template for SKILL.md output |
| `SKILL.md` | Generated output, committed to repo root |

### Data Extraction

**From source code (via `ast` module):**

| Source file | What is extracted |
|---|---|
| `src/sphinx_need_svg/__init__.py` | Package version string |
| `src/sphinx_need_svg/directives/needsvg.py` | `option_spec` dict from `NeedsvgDirective` -- keys, type functions, defaults |
| `src/sphinx_need_svg/jinja_context.py` | Public methods on `SvgJinjaContext` -- name, signature, docstring |

**From documentation (via text/regex parsing):**

| Source file | What is extracted |
|---|---|
| `docs/conf.py` | `needs_types` list (parsed as Python literal) |
| `docs/quickstart.rst` | Installation instructions and basic usage example |
| `docs/reference.rst` | Directive option descriptions, helper descriptions |
| `docs/examples-drilldown.rst` | Drilldown pattern as advanced example (first `needsvg` block) |

The RST parsing is intentionally simple -- regex extraction of directive blocks
and specific sections by heading name.  No full RST parse tree needed.

### Template Structure

`scripts/skill_template.md.j2` produces:

```
# sphinx-need-svg v{{ version }}

<one-line description>

## When to Use This Skill

<trigger phrases -- static in template>

## Installation

{{ installation_section }}

## Directive: `.. needsvg::`

| Option | Type | Default | Description |
|---|---|---|---|
{% for opt in directive_options %}
| `{{ opt.name }}` | {{ opt.type }} | {{ opt.default }} | {{ opt.description }} |
{% endfor %}

## Jinja Helpers

{% for helper in jinja_helpers %}
### `{{ helper.signature }}`

{{ helper.docstring }}

{% if helper.example %}
```rst
{{ helper.example }}
```
{% endif %}
{% endfor %}

## Configuration

### Need Types

{{ needs_types_table }}

## Patterns

### Traceability Chain
{{ traceability_example }}

### Drilldown with `arch` Wrappers
{{ drilldown_example }}

## Common Mistakes

<static list in template>
```

Static prose sections (When to Use, Common Mistakes) live directly in the
template and are hand-curated.  Dynamic sections are filled from extracted data.

### CI Integration

Added as a dedicated job in `.github/workflows/ci.yml` that runs after
`docs-build` on main pushes.  It regenerates SKILL.md and auto-commits if
the content changed -- similar to how the `bump` job auto-commits version
changes.

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

The `[skip ci]` in the commit message prevents the auto-commit from
triggering another CI run.  On PRs, the job does not run -- reviewers can
check SKILL.md manually or the PR author can regenerate locally.

### Developer Workflow

1. Change a directive option, Jinja helper, or doc example
2. Optionally run `uv run python scripts/generate_skill.py` locally to preview
3. Push to main -- CI auto-regenerates and commits SKILL.md if needed

### Script Interface

```
usage: generate_skill.py [-h] [-o OUTPUT]

Generate SKILL.md from source code and documentation.

options:
  -o, --output PATH   Output file (default: SKILL.md at repo root)
```

Exit code 0 on success, 1 on error.  The `--check` mode is not needed as a
flag -- CI just runs the script and uses `git diff --exit-code`.

## Dependencies

No new dependencies.  The script uses:
- `ast` (stdlib) for Python source parsing
- `re` (stdlib) for RST section extraction
- `pathlib` (stdlib) for file handling
- `jinja2` (already a transitive dependency via Sphinx)

## Tradeoffs

| Decision | Rationale |
|---|---|
| AST over import/inspect | No need to install the package or its deps to generate the skill |
| Regex over docutils RST parser | Simpler, fewer deps, sufficient for section-level extraction |
| Committed output over build-time-only | Agents need the file in the repo, not as a build artifact |
| CI auto-commit over fail-only check | Zero friction -- developers never need to remember to regenerate |
| Jinja2 template over f-strings | Readable, maintainable template; easy to adjust skill format |

## What This Is Not

- Not a doc generator -- it produces a single skill file, not documentation
- Not a Sphinx extension -- runs standalone, no Sphinx build required
- Not tied to any specific agent platform -- produces generic Markdown
