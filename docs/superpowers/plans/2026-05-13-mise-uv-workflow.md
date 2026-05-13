# mise + uv Developer Workflow -- Implementation Plan

> **For agentic workers:** This plan documents an already-completed setup. No further action needed.

**Goal:** Configure `mise` as the project task runner with `uv` for Python/dependency management, providing a single-command interface for all dev operations.

**Spec:** `docs/superpowers/specs/2026-05-13-mise-uv-workflow.md`

---

## File Structure

| File | Responsibility |
|---|---|
| `.mise.toml` | Task definitions, Python version pin, venv config |
| `pyproject.toml` | Package metadata, optional dependency groups, tool config |
| `uv.lock` | Locked dependency graph |

---

### Task 1: Base mise Configuration

**File:** `.mise.toml`

- [x] **Step 1:** Pin Python version: `[tools] python = "3.12"`
- [x] **Step 2:** Configure auto-venv: `[env] _.python.venv = { path = ".venv", create = true }`

---

### Task 2: Install Task

- [x] **Step 1:** Add `[tasks.install]`: `uv pip install -e '.[test,docs]'`

---

### Task 3: Test Tasks

- [x] **Step 1:** Add `[tasks.test]`: `uv run pytest tests/ -v` (full suite)
- [x] **Step 2:** Add `[tasks.test-unit]`: `uv run pytest tests/test_needsvg.py -v`
- [x] **Step 3:** Add `[tasks.test-e2e]`: `uv run pytest tests/test_docs_build.py -v`

---

### Task 4: Documentation Tasks

- [x] **Step 1:** Add `[tasks.docs]`: `uv run sphinx-build -b html docs docs/_build/html`
- [x] **Step 2:** Add `[tasks.docs-clean]`: clean `docs/_build` then rebuild

---

### Task 5: Build Task

- [x] **Step 1:** Add `[tasks.build]`: `uv build`

---

### Task 6: Linting & Formatting Tasks

- [x] **Step 1:** Add `[tasks.lint]`: `uv run ruff check src/ tests/`
- [x] **Step 2:** Add `[tasks.lint-fix]`: `uv run ruff check --fix src/ tests/`
- [x] **Step 3:** Add `[tasks.format]`: `uv run ruff format src/ tests/`
- [x] **Step 4:** Add `[tasks.format-check]`: `uv run ruff format --check src/ tests/`

---

### Task 7: Type Checking Task

- [x] **Step 1:** Add `[tasks.typecheck]`: `uv run mypy`

---

### Task 8: Compound Check Task

- [x] **Step 1:** Add `[tasks.check]`: sequential run of lint, format-check, typecheck, test
- [x] **Step 2:** Mirrors CI pipeline for local pre-push validation

---

### Task 9: Cleanup Task

- [x] **Step 1:** Add `[tasks.clean]`: `rm -rf dist/ build/ docs/_build/ src/*.egg-info .pytest_cache`

---

### Task 10: Commitizen Bump Tasks

- [x] **Step 1:** Add `[tasks.bump]`: `uv run cz bump --dry-run` (safe preview)
- [x] **Step 2:** Add `[tasks.bump-apply]`: `uv run cz bump --yes --changelog` (actual bump)

---

### Task 11: pyproject.toml Dependency Groups

- [x] **Step 1:** Define `test` extra: pytest, pytest-regressions, docs transitive
- [x] **Step 2:** Define `docs` extra: sphinx, sphinx-needs, furo, myst-parser
- [x] **Step 3:** Define `dev` extra: union of test + docs + ruff + mypy + commitizen
- [x] **Step 4:** Configure ruff: `target-version = "py39"`, rule selection
- [x] **Step 5:** Configure mypy: `python_version = "3.12"`, `mypy_path = "src"`
- [x] **Step 6:** Configure pytest: `testpaths = ["tests"]`

---

### Task 12: Verify

- [x] **Step 1:** `mise run install` -- editable install succeeds
- [x] **Step 2:** `mise run check` -- all gates pass (lint, format, typecheck, test)
- [x] **Step 3:** `mise run docs` -- docs build clean
- [x] **Step 4:** `mise run build` -- wheel builds successfully
- [x] **Step 5:** `mise run bump` -- dry-run shows expected version
