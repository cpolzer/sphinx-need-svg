# Rename to sphinx-need-svg -- Implementation Plan

> **For agentic workers:** This plan documents an already-completed rename. No further action needed.

**Goal:** Rename `sphinx-needs-svg` / `sphinx_needs_svg` to `sphinx-need-svg` / `sphinx_need_svg` across all project files.

**Spec:** `docs/superpowers/specs/2026-05-13-rename-to-sphinx-need-svg.md`

---

## File Structure

| File | Change |
|---|---|
| `src/sphinx_needs_svg/` | Directory rename to `src/sphinx_need_svg/` |
| `pyproject.toml` | Package name, wheel target, mypy/ruff paths |
| `src/sphinx_need_svg/__init__.py` | Import paths |
| `src/sphinx_need_svg/directives/needsvg.py` | Import paths |
| `docs/conf.py` | Project name, extension, copyright |
| `docs/index.rst` | Title |
| `docs/quickstart.rst` | Install commands |
| `docs/contributing.rst` | References |
| `docs/architecture.rst` | References |
| `README.md` | All mentions |
| `LICENSE` | Copyright holder |
| `tests/roots/test-basic/conf.py` | Extension import |
| `tests/roots/test-errors/conf.py` | Extension import |
| `uv.lock` | Regenerated |

---

### Task 1: Rename Source Directory

- [x] **Step 1:** `mv src/sphinx_needs_svg src/sphinx_need_svg`

---

### Task 2: Replace `sphinx_needs_svg` in All Files

- [x] **Step 1:** Find all files: `rg -l "sphinx_needs_svg" -g '!_build' -g '!*.lock' -g '!__pycache__'`
- [x] **Step 2:** `sed -i '' 's/sphinx_needs_svg/sphinx_need_svg/g'` on all matched files
- [x] **Step 3:** Verify no remaining references: `rg "sphinx_needs_svg"` returns empty

---

### Task 3: Replace `sphinx-needs-svg` in All Files

- [x] **Step 1:** Find all files: `rg -l "sphinx-needs-svg" -g '!_build' -g '!*.lock'`
- [x] **Step 2:** `sed -i '' 's/sphinx-needs-svg/sphinx-need-svg/g'` on all matched files
- [x] **Step 3:** Verify no remaining references

---

### Task 4: Regenerate Lock and Verify

- [x] **Step 1:** `uv lock && uv sync`
- [x] **Step 2:** Confirm lock shows `sphinx-need-svg` (not `sphinx-needs-svg`)
- [x] **Step 3:** `uv run pytest -x` -- 21 tests pass
- [x] **Step 4:** `uv run sphinx-build -b html docs docs/_build/html` -- clean build
