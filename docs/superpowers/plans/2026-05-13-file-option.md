# :file: Option -- Implementation Plan

> **For agentic workers:** This plan documents an already-completed feature. No further action needed.

**Goal:** Add a `:file:` option to `needsvg` for loading SVG/Jinja2 templates from external files.

**Spec:** `docs/superpowers/specs/2026-05-13-file-option.md`

---

## File Structure

| File | Responsibility |
|---|---|
| `src/sphinx_need_svg/directives/needsvg.py` | Add `:file:` to `option_spec`, resolve path, read content, register dependency |
| `tests/roots/test-file/conf.py` | Minimal Sphinx config for file-option tests |
| `tests/roots/test-file/index.rst` | RST using `:file:` (valid + missing) |
| `tests/roots/test-file/template.svg.j2` | External Jinja SVG template |
| `tests/test_needsvg.py` | Two new tests |
| `docs/reference.rst` | Document `:file:` option |

---

### Task 1: Add `:file:` Option to Directive

**Files:** `src/sphinx_need_svg/directives/needsvg.py`

- [x] **Step 1:** Add `from pathlib import Path` import
- [x] **Step 2:** Add `"file": directives.unchanged` to `option_spec`
- [x] **Step 3:** In `run()`, before storing content:
  - Check `self.options.get("file")`
  - If both `:file:` and body, log warning, prefer `:file:`
  - Resolve path relative to `Path(env.doc2path(env.docname)).parent`
  - `file_path.read_text(encoding="utf-8")`
  - `env.note_dependency(str(file_path))` for incremental rebuild
  - On `FileNotFoundError`, log warning + produce error SVG string
- [x] **Step 4:** Store resolved content (file or inline) in `env.needsvg_all_data`

---

### Task 2: Test Root and Tests

**Files:** `tests/roots/test-file/*`, `tests/test_needsvg.py`

- [x] **Step 1:** Create `tests/roots/test-file/conf.py` with minimal config
- [x] **Step 2:** Create `tests/roots/test-file/template.svg.j2`:
  ```xml
  <svg width="300" height="50" xmlns="http://www.w3.org/2000/svg">
    <a href="{{ ref('REQ_F1') }}">
      <rect width="300" height="50" rx="4" fill="#ddeeff" stroke="#336699"/>
      <text x="150" y="30" text-anchor="middle">{{ needs['REQ_F1'].title }}</text>
    </a>
  </svg>
  ```
- [x] **Step 3:** Create `tests/roots/test-file/index.rst` with:
  - A `req` directive (`REQ_F1`)
  - `.. needsvg::` with `:file: template.svg.j2`
  - `.. needsvg::` with `:file: nonexistent.svg.j2`
- [x] **Step 4:** Add `test_needsvg_file_option` -- asserts title rendered, href present, fill color
- [x] **Step 5:** Add `test_needsvg_file_not_found` -- asserts error message in output

---

### Task 3: Update Documentation

**Files:** `docs/reference.rst`

- [x] **Step 1:** Add `:file:` usage example in directive synopsis
- [x] **Step 2:** Add `:file:` row to options table with description of path resolution and dependency tracking

---

### Task 4: Verify

- [x] **Step 1:** `uv run pytest -x` -- 21 tests pass
- [x] **Step 2:** `uv run sphinx-build -b html docs docs/_build/html` -- clean build
