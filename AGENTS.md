# AGENTS.md — AI Agent Instructions

## Project Overview

sphinx-need-svg is a Sphinx extension that adds SVG diagram support for sphinx-needs.

## Quick Reference

For full development setup, tasks, testing, and packaging instructions, see:
**docs/contributing.rst**

## Key Files

- `pyproject.toml` — package metadata, dependencies, tool config
- `.mise.toml` — task runner and Python version
- `src/sphinx_need_svg/` — extension source
- `tests/` — test suite (pytest)
- `docs/` — Sphinx documentation (uses the extension itself)

## Commands

```bash
mise run check       # lint + format + mypy + test
mise run test        # run all tests
mise run lint        # ruff lint
mise run format      # ruff format
mise run typecheck   # mypy
mise run docs        # build docs
mise run build       # build wheel + sdist
```

## CI/CD

- **CI** — lint, test matrix (3.10–3.12), docs build, PR preview
- **coverage.yaml** — push → tests + Codecov
- **release.yaml** — tag push (`v*`) → build → PyPI (trusted publishing)

## Before Submitting PRs

Always run `mise run check` and ensure all tests pass.
