# Add Secret Scanning to CI

**Date:** 2026-05-20
**Status:** Draft

## Purpose

Add secret leak detection at two levels: pre-commit (local) and CI (PRs), using detect-secrets and gitleaks.

## Changes

### Modified Files

#### `.github/workflows/ci.yml`

Add two new jobs after the `test` job, before `docs-build`:

**`secret-scan`** — runs on PRs only:
```yaml
  secret-scan:
    name: Secret Scan (gitleaks)
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**`pre-commit`** — runs on PRs only:
```yaml
  pre-commit:
    name: Pre-commit Hooks
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pre-commit/action@v3.0.1
```

No changes to `needs` chains — these jobs are independent and don't block docs-build or bump.

#### `pyproject.toml`

Add `detect-secrets` to dev dependencies:

```toml
dev = [
    "sphinx-need-svg[test,docs]",
    "ruff",
    "mypy",
    "commitizen",
    "detect-secrets",
    "pre-commit",
]
```

### New Files

#### `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
        exclude: ^\.github/workflows/
```

Note: `check-yaml` excludes `.github/workflows/` because GitHub Actions YAML uses `${{ }}` syntax which the hook may flag.

#### `.secrets.baseline`

Generated via `detect-secrets scan > .secrets.baseline`. Contains baseline of known secrets (should be empty for a clean repo).

#### `.mise.toml` — add tasks

```toml
[tasks.pre-commit-install]
description = "Install pre-commit hooks"
run = "uv run pre-commit install"

[tasks.pre-commit]
description = "Run pre-commit hooks on all files"
run = "uv run pre-commit run --all-files"
```

## External Setup

None required. Gitleaks and detect-secrets work out of the box.
