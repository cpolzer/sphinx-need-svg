# Design: Drilldown Architecture Example

**Date:** 2026-05-13
**Status:** Implemented

## Goal

Demonstrate how `needsvg` diagrams can link to each other on the same page, creating a hierarchical drill-down navigation experience -- from high-level architecture down to implementation details.

## Motivation

A key value proposition of `needsvg` is that SVG boxes link to actual sphinx-needs entities via `ref()`. When multiple `needsvg` diagrams are placed on the same page, each near its corresponding need definition, clicking a box in an overview diagram scrolls directly to the detail diagram below. This creates a native drill-down UX with zero JavaScript.

## Content Model

The example uses a CI pipeline as a familiar domain:

```
Level 1: Pipeline Overview
├── STAGE_BUILD  ──→  Level 2: Build Stage (JOB_LINT, JOB_COMPILE)
├── STAGE_TEST   ──→  Level 2: Test Stage  (JOB_UNIT, JOB_DOCS)
└── STAGE_DEPLOY ──→  Level 2: Deploy Stage (JOB_PAGES, JOB_RELEASE)
                              │
                              └── Level 3: Lint Job Steps (STEP_RUFF, STEP_MYPY)
```

### Need Hierarchy

All entities use `req` type with `implements` links for traceability:

| Level | IDs | Implements |
|---|---|---|
| Pipeline | `PIPE_CI` | -- |
| Stages | `STAGE_BUILD`, `STAGE_TEST`, `STAGE_DEPLOY` | `PIPE_CI` |
| Jobs | `JOB_LINT`, `JOB_COMPILE`, `JOB_UNIT`, `JOB_DOCS`, `JOB_PAGES`, `JOB_RELEASE` | respective stage |
| Steps | `STEP_RUFF`, `STEP_MYPY` | `JOB_LINT` |

### Navigation Mechanism

Each `needsvg` block uses `ref(id)` which produces `docname.html#NEED_ID`. Since all needs and diagrams are on the same page, clicking a box scrolls to the anchor of the target need, which sits right above its detail diagram.

No JavaScript. No custom link handling. Pure HTML anchor navigation.

## Page Structure

`docs/examples-drilldown.rst` added to the toctree between `examples` and `architecture`.

Each level is separated by `----` horizontal rules and has:
1. Section heading
2. Need definitions (visible as sphinx-needs cards)
3. `needsvg` diagram with `:debug:` showing source

## Design Choices

- **All on one page** (not separate subpages) -- keeps the scroll-to-anchor UX instant and avoids page load latency. Users can still split across pages if preferred.
- **`:debug:` on all diagrams** -- this is a documentation example, showing source is the point.
- **Unique marker IDs per SVG** (`arr1`, `arr2`, ...) -- SVG marker IDs are document-global; reusing `arr` across inline SVGs would cause rendering conflicts.
- **Color coding by level** -- stages get needs-type colors, jobs get lighter task-oriented colors.

## Verification

- `uv run sphinx-build -b html docs docs/_build/html` -- clean build
- Visual inspection of `examples-drilldown.html` -- clicking boxes scrolls to detail views
- All 21 tests pass (drilldown page included in e2e docs build test)
