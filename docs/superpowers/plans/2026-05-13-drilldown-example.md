# Drilldown Architecture Example -- Implementation Plan

> **For agentic workers:** This plan documents an already-completed example page. No further action needed.

**Goal:** Add a documentation page demonstrating hierarchical drill-down navigation using linked `needsvg` diagrams on a single page.

**Spec:** `docs/superpowers/specs/2026-05-13-drilldown-example.md`

---

## File Structure

| File | Responsibility |
|---|---|
| `docs/examples-drilldown.rst` | New page with 3-level CI pipeline drilldown |
| `docs/index.rst` | Add `examples-drilldown` to toctree |

---

### Task 1: Define Need Hierarchy

**File:** `docs/examples-drilldown.rst`

- [x] **Step 1:** Define pipeline root: `PIPE_CI`
- [x] **Step 2:** Define 3 stages: `STAGE_BUILD`, `STAGE_TEST`, `STAGE_DEPLOY` (all `implements: PIPE_CI`)
- [x] **Step 3:** Define 2 jobs per stage:
  - Build: `JOB_LINT`, `JOB_COMPILE`
  - Test: `JOB_UNIT`, `JOB_DOCS`
  - Deploy: `JOB_PAGES`, `JOB_RELEASE`
- [x] **Step 4:** Define 2 steps for lint job: `STEP_RUFF`, `STEP_MYPY`

---

### Task 2: Create Level 1 Diagram (Pipeline Overview)

- [x] **Step 1:** `needsvg` with 3 stage boxes in a row
- [x] **Step 2:** Each box uses `ref(s.id)` to link to stage anchor
- [x] **Step 3:** Arrow markers between boxes
- [x] **Step 4:** Title text from `needs[s.id].title`
- [x] **Step 5:** Use unique marker ID `arr1` (avoid SVG ID collisions)

---

### Task 3: Create Level 2 Diagrams (Stage Details)

- [x] **Step 1:** Build stage -- 2-job diagram with `JOB_LINT`, `JOB_COMPILE`
- [x] **Step 2:** Test stage -- 2-job diagram with `JOB_UNIT`, `JOB_DOCS`
- [x] **Step 3:** Deploy stage -- 2-job diagram with `JOB_PAGES`, `JOB_RELEASE`
- [x] **Step 4:** Each uses unique marker IDs (`arr2`, `arr3`, `arr4`)
- [x] **Step 5:** Color-coded title text matching stage identity

---

### Task 4: Create Level 3 Diagram (Job Steps)

- [x] **Step 1:** Lint job steps -- 2-step diagram with `STEP_RUFF`, `STEP_MYPY`
- [x] **Step 2:** Unique marker ID `arr5`

---

### Task 5: Wire Into Docs

- [x] **Step 1:** Add `examples-drilldown` to `docs/index.rst` toctree between `examples` and `architecture`
- [x] **Step 2:** Add `:debug:` to all diagrams for source visibility
- [x] **Step 3:** Add horizontal rules (`----`) between levels for visual separation
- [x] **Step 4:** Add introductory text and tip admonition explaining the pattern

---

### Task 6: Verify

- [x] **Step 1:** `uv run sphinx-build -b html docs docs/_build/html` -- clean build
- [x] **Step 2:** Open `docs/_build/html/examples-drilldown.html` -- visual inspection
- [x] **Step 3:** Click stage boxes -- browser scrolls to stage detail sections
- [x] **Step 4:** `uv run pytest -x` -- all 21 tests pass (includes e2e docs build)
