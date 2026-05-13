# Design: mise + uv Developer Workflow

**Date:** 2026-05-13
**Status:** Implemented

## Goal

Provide a consistent, discoverable developer experience via `mise` task runner backed by `uv` for Python package management. Every common operation should be a single `mise run <task>` command.

## Motivation

- **Discoverability:** `mise tasks` lists everything a contributor can do -- no need to read a Makefile or remember ad-hoc commands.
- **Reproducibility:** `uv` with `uv.lock` ensures identical dependency resolution across machines.
- **Speed:** `uv` is significantly faster than pip/pip-tools for resolution and installation.
- **No global state:** `mise` manages the Python version and venv locally (`.venv`), avoiding system-level pollution.

## Tool Chain

| Tool | Role |
|---|---|
| `mise` | Task runner, Python version manager, venv orchestration |
| `uv` | Package installer/resolver, lock file, build frontend |
| `ruff` | Linter + formatter (replaces flake8, isort, black) |
| `mypy` | Static type checker (strict mode) |
| `pytest` | Test runner |
| `commitizen` | Conventional commit enforcement, version bump, changelog |
| `sphinx-build` | Documentation builder |

## Task Map

| Task | Command | Purpose |
|---|---|---|
| `install` | `uv pip install -e '.[test,docs]'` | Editable install with all extras |
| `test` | `uv run pytest tests/ -v` | Full test suite |
| `test-unit` | `uv run pytest tests/test_needsvg.py -v` | Unit/integration tests only |
| `test-e2e` | `uv run pytest tests/test_docs_build.py -v` | E2E docs build test |
| `docs` | `uv run sphinx-build -b html docs docs/_build/html` | Build HTML docs |
| `docs-clean` | `rm -rf docs/_build && sphinx-build ...` | Clean rebuild |
| `build` | `uv build` | Build sdist + wheel |
| `lint` | `uv run ruff check src/ tests/` | Lint check |
| `lint-fix` | `uv run ruff check --fix src/ tests/` | Lint with auto-fix |
| `format` | `uv run ruff format src/ tests/` | Format code |
| `format-check` | `uv run ruff format --check src/ tests/` | Check formatting |
| `typecheck` | `uv run mypy` | Type check |
| `check` | lint + format-check + typecheck + test | All quality gates |
| `clean` | `rm -rf dist/ build/ docs/_build/ ...` | Remove artifacts |
| `bump` | `uv run cz bump --dry-run` | Preview version bump |
| `bump-apply` | `uv run cz bump --yes --changelog` | Bump + changelog + tag |

## Configuration

### `.mise.toml`

```toml
[tools]
python = "3.12"

[env]
_.python.venv = { path = ".venv", create = true }
```

- Pins Python 3.12 via mise
- Auto-creates `.venv` in project root
- All `uv run` commands execute inside this venv

### `pyproject.toml` Extras

```toml
[project.optional-dependencies]
test = ["pytest", "pytest-regressions", "sphinx-need-svg[docs]"]
docs = ["sphinx", "sphinx-needs", "furo", "myst-parser"]
dev = ["sphinx-need-svg[test,docs]", "ruff", "mypy", "commitizen"]
```

- `test` includes `docs` transitively (needed for e2e docs build test)
- `dev` is the union of everything

### Quality Tool Config (in `pyproject.toml`)

- **ruff:** `target-version = "py39"`, select rules: E, F, I, UP, B, SIM, RUF
- **mypy:** `python_version = "3.12"`, strict mode, `mypy_path = "src"`
- **pytest:** `testpaths = ["tests"]`
- **commitizen:** `tag_format = "v$version"`, `update_changelog_on_bump = true`

## Design Choices

- **`mise` over Makefile:** cross-platform, built-in tool management, structured task descriptions, no tab-sensitivity footguns.
- **`uv` over pip/pip-tools:** faster, built-in lockfile, `uv run` avoids manual venv activation.
- **`ruff` over flake8+isort+black:** single tool, faster, consistent config in `pyproject.toml`.
- **`check` as compound task:** runs all gates sequentially -- lint, format, typecheck, test. Mirrors what CI does. Fail-fast via `&&` chaining.
- **Separate `bump` (dry-run) and `bump-apply`:** prevents accidental version bumps. CI uses `bump-apply`; developers use `bump` to preview.

## Relationship to CI

The `check` task is the local equivalent of the CI pipeline's quality gate. CI runs the same commands:

```yaml
- run: uv run ruff check src/ tests/
- run: uv run ruff format --check src/ tests/
- run: uv run mypy
- run: uv run pytest tests/ -v
```

This ensures local `mise run check` and CI produce identical results.
