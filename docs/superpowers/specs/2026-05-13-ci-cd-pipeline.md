# Design: CI/CD Pipeline (GitHub Actions)

**Date:** 2026-05-13
**Status:** Implemented

## Goal

Automated quality gates on PRs, version bumping on main, and documentation deployment on release tags -- all via GitHub Actions.

## Pipeline Model

Two workflow files, three trigger contexts:

| Trigger | Workflow | Jobs |
|---|---|---|
| PR to `main` | `ci.yml` | lint → test → docs-build → docs-preview-comment |
| Push to `main` | `ci.yml` | lint → test → docs-build → bump (commitizen) |
| Tag `v*` | `deploy-pages.yml` | build docs → deploy to GitHub Pages |

```
PR ──→ lint ──→ test (3.10, 3.11, 3.12) ──→ docs-build ──→ preview comment
                                                              (artifact + PR comment)

main push ──→ lint ──→ test ──→ docs-build ──→ bump ──→ push tag
                                                           │
                                                           ▼
                                              deploy-pages.yml triggers
                                                           │
                                                           ▼
                                              GitHub Pages deploy
```

## Workflow 1: `ci.yml`

### Triggers

```yaml
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
```

### Concurrency

```yaml
concurrency:
  group: "ci-${{ github.ref }}"
  cancel-in-progress: true
```

Cancels in-flight runs for the same branch/PR when new commits arrive.

### Jobs

#### `lint` -- Lint & Type Check

- Runs on: `ubuntu-latest`, Python 3.12
- Steps: `ruff check`, `ruff format --check`, `mypy`
- No matrix -- linting is Python-version-independent

#### `test` -- Test Matrix

- Runs on: `ubuntu-latest`
- Matrix: Python 3.10, 3.11, 3.12
- Steps: `uv sync --all-extras`, `pytest tests/ -v`
- Tests include unit/integration (`test_needsvg.py`) and e2e docs build (`test_docs_build.py`)

#### `docs-build` -- Build Documentation

- Depends on: `lint`, `test` (only runs if both pass)
- Steps: `sphinx-build -b html docs docs/_build/html`
- On PR: uploads `docs-preview` artifact (7-day retention)

#### `docs-preview-comment` -- PR Preview Link

- Runs only on PRs
- Depends on: `docs-build`
- Uses `peter-evans/find-comment` + `peter-evans/create-or-update-comment`
- Posts/updates a comment with a link to the Actions run's artifact download
- Idempotent: finds existing comment by body marker `## Docs Preview` and replaces

#### `bump` -- Version Bump & Tag

- Runs only on push to `main` (not PRs)
- Depends on: `lint`, `test`, `docs-build`
- Needs `contents: write` permission
- Checks out with `fetch-depth: 0` (full history for commitizen)
- Configures git as `github-actions[bot]`
- Runs `cz bump --yes --changelog`
- Detects `NO_INCREMENT_DETECTED` → skips push (no conventional commits since last bump)
- On successful bump: `git push --follow-tags` → pushes commit + `v*` tag

## Workflow 2: `deploy-pages.yml`

### Trigger

```yaml
on:
  push:
    tags:
      - "v*"
```

Only fires when a `v*` tag is pushed -- decoupled from the CI workflow.

### Permissions

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

Uses OIDC-based deployment (no PAT needed).

### Jobs

#### `build` -- Build Docs

- Same as `ci.yml` docs-build but uploads via `actions/upload-pages-artifact`

#### `deploy` -- Deploy to GitHub Pages

- Uses `actions/deploy-pages@v4`
- Deploys to `github-pages` environment
- URL output: `https://cpolzer.github.io/sphinx-need-svg/`

## Design Choices

### Why Two Workflows?

Separating CI (`ci.yml`) and deployment (`deploy-pages.yml`) keeps concerns clean:
- CI runs on every PR and push -- fast feedback, quality gates
- Deploy runs only on tags -- deliberate release cadence
- Tag creation is automated by commitizen in CI, bridging the two

### Why Commitizen Auto-Bump on Main?

- Conventional commits (`feat:`, `fix:`, `chore:`) drive version semantics automatically
- No manual version editing, no release branches
- `NO_INCREMENT_DETECTED` guard prevents empty bumps when only non-conventional commits land

### Why Artifact-Based PR Preview (Not Hosted)?

- GitHub Actions artifacts are free and require no additional infrastructure
- Hosted previews (Netlify, Surge, etc.) add third-party dependencies and secrets management
- For a small project, artifact download + local open is sufficient
- Can upgrade to hosted preview later if needed

### Why Python Matrix 3.10--3.12?

- `requires-python = ">=3.9"` in `pyproject.toml`
- 3.10 is the oldest widely-used version
- 3.12 is current stable
- 3.11 covers the middle ground
- 3.9 omitted from CI matrix (low usage, still declared as minimum)

### Concurrency Groups

- `ci.yml`: `ci-${{ github.ref }}` -- one active run per branch
- `deploy-pages.yml`: `pages` -- one active deploy globally (prevents race conditions on Pages)

## Permissions Model

| Job | Permission | Reason |
|---|---|---|
| lint, test, docs-build | `contents: read` | Read repo only |
| docs-preview-comment | `pull-requests: write` | Post PR comments |
| bump | `contents: write` | Push version commit + tag |
| deploy | `pages: write`, `id-token: write` | OIDC Pages deployment |

Minimal permissions per job -- no blanket `write-all`.

## Prerequisites

- GitHub Pages source must be set to **GitHub Actions** in repo settings (Settings → Pages → Source)
- `GITHUB_TOKEN` is used for bump (no PAT needed for same-repo push)
- Commitizen config in `pyproject.toml`:
  - `tag_format = "v$version"`
  - `update_changelog_on_bump = true`
  - `changelog_file = "CHANGELOG.md"`
