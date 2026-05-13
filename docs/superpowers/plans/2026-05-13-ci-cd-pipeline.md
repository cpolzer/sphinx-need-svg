# CI/CD Pipeline -- Implementation Plan

> **For agentic workers:** This plan documents an already-completed CI/CD setup. No further action needed.

**Goal:** GitHub Actions CI for quality gates (lint, test, docs) on PRs, commitizen auto-bump on main, and tag-triggered GitHub Pages deployment.

**Spec:** `docs/superpowers/specs/2026-05-13-ci-cd-pipeline.md`

---

## File Structure

| File | Responsibility |
|---|---|
| `.github/workflows/ci.yml` | PR/main quality gates, PR preview, commitizen bump |
| `.github/workflows/deploy-pages.yml` | Tag-triggered docs deployment to GitHub Pages |

---

### Task 1: CI Workflow -- Lint & Type Check Job

**File:** `.github/workflows/ci.yml`

- [x] **Step 1:** Create workflow file with triggers (`pull_request` + `push` to `main`)
- [x] **Step 2:** Set permissions: `contents: read`, `pull-requests: write`
- [x] **Step 3:** Add concurrency group `ci-${{ github.ref }}` with `cancel-in-progress: true`
- [x] **Step 4:** Add `lint` job:
  - `actions/checkout@v4`
  - `astral-sh/setup-uv@v4`
  - `uv python install 3.12`
  - `uv sync --all-extras`
  - `uv run ruff check src/ tests/`
  - `uv run ruff format --check src/ tests/`
  - `uv run mypy`

---

### Task 2: CI Workflow -- Test Matrix Job

- [x] **Step 1:** Add `test` job with matrix: Python 3.10, 3.11, 3.12
- [x] **Step 2:** Steps: checkout, setup-uv, install python, sync, `pytest tests/ -v`

---

### Task 3: CI Workflow -- Docs Build + PR Preview

- [x] **Step 1:** Add `docs-build` job, depends on `[lint, test]`
- [x] **Step 2:** Steps: checkout, setup-uv, python, sync, `sphinx-build -b html docs docs/_build/html`
- [x] **Step 3:** Upload artifact `docs-preview` on PR events (7-day retention)
- [x] **Step 4:** Add `docs-preview-comment` job (PR only):
  - `peter-evans/find-comment@v3` to find existing comment by `## Docs Preview` marker
  - `peter-evans/create-or-update-comment@v4` to post/update with artifact link
  - Edit mode `replace` for idempotent updates

---

### Task 4: CI Workflow -- Commitizen Bump Job

- [x] **Step 1:** Add `bump` job with condition `github.ref == 'refs/heads/main' && github.event_name == 'push'`
- [x] **Step 2:** Depends on `[lint, test, docs-build]`
- [x] **Step 3:** Set `permissions: contents: write`
- [x] **Step 4:** Checkout with `fetch-depth: 0` (full history for commitizen)
- [x] **Step 5:** Configure git identity as `github-actions[bot]`
- [x] **Step 6:** Run `cz bump --yes --changelog`, capture output
- [x] **Step 7:** Detect `NO_INCREMENT_DETECTED` → set `bumped=false`, skip push
- [x] **Step 8:** On success: `git push --follow-tags` (pushes commit + `v*` tag)

---

### Task 5: Deploy Pages Workflow

**File:** `.github/workflows/deploy-pages.yml`

- [x] **Step 1:** Create workflow with trigger `push: tags: ["v*"]`
- [x] **Step 2:** Set permissions: `contents: read`, `pages: write`, `id-token: write`
- [x] **Step 3:** Add concurrency group `pages` with `cancel-in-progress: true`
- [x] **Step 4:** Add `build` job: checkout, setup-uv, python, sync, sphinx-build, `actions/upload-pages-artifact@v3`
- [x] **Step 5:** Add `deploy` job: depends on `build`, uses `actions/deploy-pages@v4`
- [x] **Step 6:** Set `environment: github-pages` with URL output

---

### Task 6: Commitizen Config

**File:** `pyproject.toml`

- [x] **Step 1:** Add `[tool.commitizen]` section:
  - `tag_format = "v$version"`
  - `update_changelog_on_bump = true`
  - `changelog_file = "CHANGELOG.md"`
  - `version_files = ["src/sphinx_need_svg/__init__.py:__version__"]`
- [x] **Step 2:** Add `commitizen` to `dev` optional dependency

---

### Task 7: Verify

- [x] **Step 1:** Push to `main` -- lint, test, docs-build jobs pass
- [x] **Step 2:** Create PR -- preview comment appears with artifact link
- [ ] **Step 3:** Verify first conventional commit bump creates `v*` tag
- [ ] **Step 4:** Verify tag push triggers `deploy-pages.yml` and docs appear at `https://cpolzer.github.io/sphinx-need-svg/`
- [ ] **Step 5:** Enable GitHub Pages source to **GitHub Actions** in repo settings
