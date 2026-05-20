# Add Secret Scanning to CI — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add secret leak detection via gitleaks (CI) and detect-secrets (pre-commit) to catch leaked credentials before they reach the repo.

**Architecture:** Two parallel detection layers: gitleaks scans full git history in CI on PRs, detect-secrets runs as a pre-commit hook locally and in CI.

**Tech Stack:** gitleaks, detect-secrets, pre-commit, GitHub Actions

---

## Chunk 1: Pre-commit Setup

### Task 1: Add dev dependencies

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add detect-secrets and pre-commit to dev deps**

Change the `dev` array in `pyproject.toml` from:
```toml
dev = [
    "sphinx-need-svg[test,docs]",
    "ruff",
    "mypy",
    "commitizen",
]
```
to:
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

- [ ] **Step 2: Verify install**

```bash
uv sync --all-extras && uv run detect-secrets --version && uv run pre-commit --version
```

Expected: both print version numbers

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "deps: add detect-secrets and pre-commit to dev dependencies"
```

### Task 2: Create `.pre-commit-config.yaml`

**Files:**
- Create: `.pre-commit-config.yaml`

- [ ] **Step 1: Create config**

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

- [ ] **Step 2: Verify YAML**

```bash
python3 -c "import yaml; yaml.safe_load(open('.pre-commit-config.yaml')); print('valid')"
```

Expected: `valid`

- [ ] **Step 3: Commit**

```bash
git add .pre-commit-config.yaml
git commit -m "ci: add pre-commit config with detect-secrets hook"
```

### Task 3: Generate baseline and add mise tasks

**Files:**
- Create: `.secrets.baseline`
- Modify: `.mise.toml`

- [ ] **Step 1: Generate baseline**

```bash
uv run detect-secrets scan > .secrets.baseline
```

Expected: empty JSON `{}` or minimal baseline

- [ ] **Step 2: Add mise tasks**

Append to `.mise.toml`:
```toml
[tasks.pre-commit-install]
description = "Install pre-commit hooks"
run = "uv run pre-commit install"

[tasks.pre-commit]
description = "Run pre-commit hooks on all files"
run = "uv run pre-commit run --all-files"
```

- [ ] **Step 3: Verify pre-commit runs**

```bash
uv run pre-commit run --all-files
```

Expected: all hooks pass

- [ ] **Step 4: Commit**

```bash
git add .secrets.baseline .mise.toml
git commit -m "ci: add pre-commit mise tasks and secrets baseline"
```

---

## Chunk 2: CI Integration

### Task 4: Add secret-scan and pre-commit jobs to ci.yml

**Files:**
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Insert jobs after `test` job, before `docs-build`**

Add these two jobs between the `test` job (ends around line 67) and `docs-build` (starts at line 69):

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

  pre-commit:
    name: Pre-commit Hooks
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pre-commit/action@v3.0.1
```

- [ ] **Step 2: Verify YAML**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); print('valid')"
```

Expected: `valid`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add gitleaks and pre-commit jobs to CI workflow"
```

---

## External Setup

None required.
