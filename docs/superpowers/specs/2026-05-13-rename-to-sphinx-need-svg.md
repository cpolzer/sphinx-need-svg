# Design: Rename sphinx-needs-svg to sphinx-need-svg

**Date:** 2026-05-13
**Status:** Implemented

## Goal

Rename the project from `sphinx-needs-svg` / `sphinx_needs_svg` to `sphinx-need-svg` / `sphinx_need_svg` to match the GitHub repository name `cpolzer/sphinx-need-svg`.

## Motivation

The repo was created as `sphinx-need-svg` (singular "need") but the package was scaffolded as `sphinx-needs-svg` (plural). Align everything to the canonical repo name.

## Scope of Change

Three naming surfaces must be updated consistently:

| Surface | Before | After |
|---|---|---|
| PyPI / pip name | `sphinx-needs-svg` | `sphinx-need-svg` |
| Python import | `sphinx_needs_svg` | `sphinx_need_svg` |
| Source directory | `src/sphinx_needs_svg/` | `src/sphinx_need_svg/` |

### Files Affected

Every file containing either `sphinx-needs-svg` or `sphinx_needs_svg`:

- `pyproject.toml` -- package name, wheel target, ruff/mypy config
- `src/sphinx_needs_svg/` -- directory rename
- `src/sphinx_needs_svg/__init__.py` -- internal imports
- `src/sphinx_needs_svg/directives/needsvg.py` -- import path
- `docs/conf.py` -- project name, extension import, copyright
- `docs/index.rst` -- title
- `docs/quickstart.rst` -- install commands
- `docs/contributing.rst` -- references
- `docs/architecture.rst` -- references
- `README.md` -- all mentions
- `LICENSE` -- copyright holder
- `tests/roots/test-basic/conf.py` -- extension import
- `tests/roots/test-errors/conf.py` -- extension import
- `uv.lock` -- regenerated after `pyproject.toml` change

### Not Changed

- Git remote URL (`git@github.com:cpolzer/sphinx-need-svg.git`) -- already correct
- GitHub repo name -- already `sphinx-need-svg`
- Internal directive name (`needsvg`) -- unchanged, this is the RST directive, not the package

## Risks

- Any downstream user with `sphinx-needs-svg` in their `requirements.txt` breaks. Acceptable since we have no external users yet (v0.1.0).
- `uv.lock` must be regenerated or builds fail.

## Verification

1. `uv lock && uv sync` succeeds
2. `uv run pytest` -- all tests pass
3. `uv run sphinx-build -b html docs docs/_build/html` -- clean build
4. `python -c "import sphinx_need_svg"` -- importable
